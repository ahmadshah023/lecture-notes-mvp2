import os
import tempfile
import asyncio
import requests
from typing import Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from deepgram import DeepgramClient, FileSource
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv
import aiofiles
from sqlalchemy.orm import Session

from backend.database import init_db, get_db, LectureUpload

# --- Configuration and Setup ---

# Load environment variables from .env file
load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Initialize Deepgram Client ---
try:
    if DEEPGRAM_API_KEY:
        # Initialize Deepgram client
        # Note: The SDK uses httpx internally with default timeouts
        # We'll handle timeouts at the application level
        deepgram_client = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        print("Deepgram client initialized successfully")
    else:
        print("Warning: DEEPGRAM_API_KEY not set")
        deepgram_client = None
except Exception as e:
    print(f"Error initializing Deepgram client: {e}")
    deepgram_client = None


# --- Initialize Gemini Client (Correct Way) ---
try:
    # Initialize the client using the API key directly
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    gemini_client = None


# Define constants
# Note: Vercel has 4.5MB limit, but we'll keep 20MB for other platforms
# Adjust based on your deployment platform
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES = [
    "audio/wav",
    "audio/mpeg", # mp3
    "audio/m4a",
    "audio/x-m4a",
    "audio/ogg",
    "audio/flac",
    "video/mp4", # m4a is often treated as video/mp4
]
# LLM Prompt for summarization
SUMMARIZATION_PROMPT = """
You are an expert academic assistant. Your task is to analyze the provided lecture transcript and generate clean, structured notes.

The notes must strictly follow this format:
1.  **One-Sentence Summary**: A single, concise sentence summarizing the main topic of the lecture.
2.  **Key Takeaways**: A bulleted list of 5 to 15 key points from the lecture.
3.  **Key Terms/Concepts**: A list of 5 important terms or concepts introduced.
4.  **Follow-up Questions**: A list of 3 thought-provoking questions for students to consider or research further.

Lecture Transcript:
---
{transcript}
---
"""

# Initialize FastAPI app
app = FastAPI(
    title="Lecture Notes MVP Backend (Deepgram + Gemini)",
    description="FastAPI service for transcribing (Deepgram) and summarizing (Gemini) lecture audio files.",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
# For Vercel/serverless, initialize lazily instead of on startup
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
    except Exception as e:
        # Log error but don't fail startup (for serverless environments)
        print(f"Database initialization warning: {e}")
        # Database will be initialized on first use

# --- Helper Functions ---

async def save_upload_file_to_temp(upload_file: UploadFile) -> str:
    """Saves the uploaded file to a temporary location and returns the path."""
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"uploaded_audio_{os.getpid()}_{upload_file.filename}")

    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await upload_file.read(1024 * 1024):
            await out_file.write(content)
    
    return file_path

def get_mime_type_from_filename(filename: str) -> str:
    """Determine MIME type from file extension."""
    if not filename:
        return "audio/mpeg"
    
    ext = filename.lower().split('.')[-1]
    mime_map = {
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'm4a': 'audio/m4a',
        'ogg': 'audio/ogg',
        'flac': 'audio/flac',
        'mp4': 'video/mp4',
        'wma': 'audio/x-ms-wma',
        'aac': 'audio/aac',
    }
    return mime_map.get(ext, 'audio/mpeg')

def validate_file(file: UploadFile):
    """Validates file size and MIME type."""
    # Get MIME type from content_type or filename
    mime_type = file.content_type or get_mime_type_from_filename(file.filename)
    
    if mime_type not in ALLOWED_MIME_TYPES:
        # Check if it's a video file that might contain audio
        if mime_type.startswith('video/'):
            # Allow video files as they might contain audio tracks
            pass
        elif mime_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format: {mime_type}. Supported formats: MP3, WAV, M4A, OGG, FLAC, MP4 (with audio)."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {mime_type}. Please upload an audio file (MP3, WAV, M4A, OGG, FLAC, or MP4 with audio)."
            )

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    """Serves the main frontend HTML file."""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    if not os.path.exists(frontend_path):
        return HTMLResponse("<h1>Frontend not found</h1><p>Please ensure 'frontend/index.html' exists.</p>", status_code=404)
    return FileResponse(frontend_path)

@app.post("/process-lecture")
async def process_lecture(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Accepts an audio file, transcribes it with Deepgram, and summarizes it with Gemini.
    Also saves the result to the database.
    """
    temp_file_path = None
    upload_id = None
    try:
        # 1. API Key Check
        if not DEEPGRAM_API_KEY or not deepgram_client:
            raise HTTPException(
                status_code=500,
                detail="Server configuration error: DEEPGRAM_API_KEY is not set or client failed to initialize."
            )
        if not GEMINI_API_KEY or not gemini_client:
            raise HTTPException(
                status_code=500,
                detail="Server configuration error: GEMINI_API_KEY is not set or client failed to initialize."
            )
        
        # 2. File Validation (MIME type)
        validate_file(file)

        # 3. Save file to a temporary location
        temp_file_path = await save_upload_file_to_temp(file)

        # 4. Final File Size Check
        file_size = os.path.getsize(temp_file_path)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds the limit of {MAX_FILE_SIZE_MB}MB."
            )

        # 5. Transcription using Deepgram REST API directly
        # Using REST API instead of SDK for better timeout control
        print(f"Starting transcription for file: {file.filename} ({file_size / 1024 / 1024:.2f} MB)")
        
        # Calculate timeout based on file size (roughly 1 minute per 10 minutes of audio + buffer)
        # Minimum 60 seconds, maximum 15 minutes
        estimated_timeout = max(60, min(900, int(file_size / (1024 * 1024)) * 30))
        
        try:
            import concurrent.futures
            
            # Use Deepgram REST API directly with requests library for better control
            def call_deepgram_rest_api():
                url = "https://api.deepgram.com/v1/listen"
                headers = {
                    "Authorization": f"Token {DEEPGRAM_API_KEY}",
                }
                
                # Determine MIME type from content_type or filename
                mime_type = file.content_type or get_mime_type_from_filename(file.filename)
                print(f"Detected MIME type: {mime_type} for file: {file.filename}")
                
                # Read file data
                with open(temp_file_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                
                # Verify file is not empty
                if len(audio_data) == 0:
                    raise ValueError("Uploaded file is empty")
                
                # Try sending as multipart/form-data first (preferred method)
                try:
                    files = {
                        "audio": (file.filename or "audio.mp3", audio_data, mime_type)
                    }
                    
                    params = {
                        "model": "nova-2",
                        "smart_format": "true",
                    }
                    
                    print(f"Uploading to Deepgram API as multipart/form-data (timeout: {estimated_timeout}s)...")
                    response = requests.post(
                        url,
                        headers=headers,
                        files=files,
                        params=params,
                        timeout=(30, estimated_timeout)
                    )
                    
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.HTTPError as e:
                    # If multipart fails with "corrupt or unsupported", try sending as raw bytes
                    if e.response.status_code == 400:
                        error_data = e.response.json() if e.response.headers.get('content-type', '').startswith('application/json') else {}
                        if "corrupt" in str(error_data).lower() or "unsupported" in str(error_data).lower():
                            print("Multipart upload failed, trying raw bytes upload...")
                            # Try sending as raw bytes with Content-Type header
                            headers_with_content = headers.copy()
                            headers_with_content["Content-Type"] = mime_type
                            
                            params = {
                                "model": "nova-2",
                                "smart_format": "true",
                            }
                            
                            response = requests.post(
                                url,
                                headers=headers_with_content,
                                data=audio_data,
                                params=params,
                                timeout=(30, estimated_timeout)
                            )
                            response.raise_for_status()
                            return response.json()
                    raise
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await asyncio.wait_for(
                    loop.run_in_executor(executor, call_deepgram_rest_api),
                    timeout=estimated_timeout + 60  # Add buffer for processing
                )
            
            print("Deepgram API call completed successfully")
            
            # Extract transcript from response
            if "results" in result and "channels" in result["results"]:
                transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected response format from Deepgram API"
                )
                
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail=f"Transcription timeout: The Deepgram API took longer than {estimated_timeout // 60} minutes to respond. This might be due to a very large file. Please try with a smaller file or split the audio into segments."
            )
        except requests.exceptions.Timeout as e:
            raise HTTPException(
                status_code=504,
                detail=f"Connection timeout: Unable to connect to Deepgram API within 30 seconds. Please check your internet connection, firewall settings, and ensure api.deepgram.com is accessible."
            )
        except requests.exceptions.ConnectionError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Connection error: Unable to reach Deepgram API. Please check your internet connection and ensure api.deepgram.com is accessible. Error: {str(e)}"
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication error: Invalid Deepgram API key. Please check your .env file."
                )
            elif e.response.status_code == 400:
                # Try to parse error message
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("err_msg", e.response.text)
                    if "corrupt" in error_msg.lower() or "unsupported" in error_msg.lower():
                        raise HTTPException(
                            status_code=400,
                            detail=f"Audio file error: {error_msg}. Please ensure the file is a valid, uncorrupted audio file. Supported formats: MP3, WAV, M4A, OGG, FLAC, MP4 (with audio). Try converting the file to MP3 format."
                        )
                except:
                    pass
                raise HTTPException(
                    status_code=400,
                    detail=f"Deepgram API error: {e.response.text}. Please check that your audio file is valid and in a supported format (MP3, WAV, M4A, OGG, FLAC, or MP4 with audio)."
                )
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Deepgram API error: {e.response.text}"
            )
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            print(f"Deepgram API error: {error_type}: {error_msg}")
            
            if "timeout" in error_msg.lower():
                raise HTTPException(
                    status_code=504,
                    detail=f"Transcription timeout: {error_msg}. Try with a smaller file or check your internet connection."
                )
            elif "connection" in error_msg.lower() or "connect" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail=f"Connection error: Unable to connect to Deepgram API. Please check your internet connection and firewall settings. Error: {error_msg}"
                )
            raise
        
        if not transcript:
            raise HTTPException(
                status_code=400,
                detail="Transcription failed or returned empty text. The audio file might be silent or corrupted."
            )

        print(f"Transcription completed. Starting summarization...")

        # 6. Summarization using Google Gemini
        formatted_prompt = SUMMARIZATION_PROMPT.format(transcript=transcript)
        
        # Using gemini-2.5-flash for fast and capable summarization
        chat_response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_prompt
        )
        
        notes = chat_response.text.strip()

        # 7. Save to database
        try:
            db_upload = LectureUpload(
                filename=file.filename or "unknown",
                file_size=file_size,
                file_type=file.content_type or "unknown",
                transcript=transcript,
                notes=notes
            )
            db.add(db_upload)
            db.commit()
            db.refresh(db_upload)
            upload_id = db_upload.id
            print(f"Saved upload to database with ID: {upload_id}")
        except Exception as db_error:
            print(f"Warning: Failed to save to database: {db_error}")
            # Continue even if database save fails

        # 8. Return success response
        return JSONResponse(content={
            "status": "ok",
            "id": upload_id,
            "filename": file.filename,
            "transcript": transcript,
            "notes": notes,
            "error": None
        })

    except HTTPException as e:
        # Re-raise FastAPI HTTP exceptions
        raise e
    except asyncio.TimeoutError:
        # Handle timeout errors
        print("Transcription timeout error")
        return JSONResponse(content={
            "status": "error",
            "transcript": None,
            "notes": None,
            "error": "Transcription timeout: The Deepgram API took too long to respond. Please check your internet connection and try again with a smaller file."
        }, status_code=504)
    except APIError as e:
        # Handle Gemini API errors
        print(f"Gemini API Error: {e}")
        return JSONResponse(content={
            "status": "error",
            "transcript": None,
            "notes": None,
            "error": f"Gemini API Error: {str(e)}"
        }, status_code=500)
    except Exception as e:
        # Handle other potential errors (e.g., Deepgram API errors, file system errors)
        import traceback
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"An error occurred during processing: {error_type}: {error_msg}")
        print(traceback.format_exc())
        
        # Provide more helpful error messages for common issues
        if "timeout" in error_msg.lower() or "handshake" in error_msg.lower() or "ConnectTimeout" in error_type:
            user_friendly_error = "Connection timeout: Unable to connect to Deepgram API. Please check your internet connection and ensure your API key is valid."
        elif "SSL" in error_msg or "certificate" in error_msg.lower():
            user_friendly_error = "SSL connection error: There was a problem establishing a secure connection. Please check your network settings."
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            user_friendly_error = "Authentication error: Invalid Deepgram API key. Please check your .env file."
        else:
            user_friendly_error = f"Processing failed: {error_type}: {error_msg}"
        
        return JSONResponse(content={
            "status": "error",
            "transcript": None,
            "notes": None,
            "error": user_friendly_error
        }, status_code=500)
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as cleanup_error:
                print(f"Warning: Failed to clean up temp file: {cleanup_error}")


@app.get("/test-deepgram")
async def test_deepgram_connection():
    """
    Test endpoint to verify Deepgram API connectivity.
    """
    if not DEEPGRAM_API_KEY:
        return JSONResponse(content={
            "status": "error",
            "message": "DEEPGRAM_API_KEY not set in environment variables."
        }, status_code=500)
    
    try:
        import concurrent.futures
        
        def test_connection():
            # Test connection to Deepgram API
            url = "https://api.deepgram.com/v1/projects"
            headers = {
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
            }
            
            response = requests.get(url, headers=headers, timeout=(10, 10))
            response.raise_for_status()
            return response.json()
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await asyncio.wait_for(
                loop.run_in_executor(executor, test_connection),
                timeout=15.0
            )
        
        return JSONResponse(content={
            "status": "ok",
            "message": "Deepgram API connection successful.",
            "projects": len(result.get("projects", [])) if isinstance(result, dict) else 0
        })
    except requests.exceptions.Timeout:
        return JSONResponse(content={
            "status": "error",
            "message": "Connection timeout: Unable to reach Deepgram API within 10 seconds. Check your internet connection."
        }, status_code=504)
    except requests.exceptions.ConnectionError as e:
        return JSONResponse(content={
            "status": "error",
            "message": f"Connection error: Unable to reach Deepgram API. Check your internet connection and firewall. Error: {str(e)}"
        }, status_code=503)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return JSONResponse(content={
                "status": "error",
                "message": "Authentication failed: Invalid Deepgram API key. Please check your .env file."
            }, status_code=401)
        return JSONResponse(content={
            "status": "error",
            "message": f"Deepgram API error: {e.response.status_code} - {e.response.text}"
        }, status_code=e.response.status_code)
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": f"Connection test failed: {type(e).__name__}: {str(e)}"
        }, status_code=500)


@app.get("/history")
async def get_history(db: Session = Depends(get_db), limit: int = 50) -> Dict[str, Any]:
    """
    Retrieves the upload history from the database.
    """
    try:
        uploads = db.query(LectureUpload).order_by(LectureUpload.created_at.desc()).limit(limit).all()
        
        history = []
        for upload in uploads:
            history.append({
                "id": upload.id,
                "filename": upload.filename,
                "file_size": upload.file_size,
                "file_type": upload.file_type,
                "transcript": upload.transcript,
                "notes": upload.notes,
                "created_at": upload.created_at.isoformat() if upload.created_at else None
            })
        
        return JSONResponse(content={
            "status": "ok",
            "history": history,
            "count": len(history)
        })
    except Exception as e:
        print(f"Error retrieving history: {e}")
        return JSONResponse(content={
            "status": "error",
            "history": [],
            "count": 0,
            "error": str(e)
        }, status_code=500)


@app.get("/history/{upload_id}")
async def get_upload_by_id(upload_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieves a specific upload by ID.
    """
    try:
        upload = db.query(LectureUpload).filter(LectureUpload.id == upload_id).first()
        
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        return JSONResponse(content={
            "status": "ok",
            "id": upload.id,
            "filename": upload.filename,
            "file_size": upload.file_size,
            "file_type": upload.file_type,
            "transcript": upload.transcript,
            "notes": upload.notes,
            "created_at": upload.created_at.isoformat() if upload.created_at else None
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving upload: {e}")
        return JSONResponse(content={
            "status": "error",
            "error": str(e)
        }, status_code=500)

# --- Rate Limiting Note (as requested in the prompt) ---
# For simple rate limiting, you could use a library like 'fastapi-limiter'
# or implement a simple token bucket algorithm using a cache (like Redis).
# For this MVP, we will only note it in the README.
