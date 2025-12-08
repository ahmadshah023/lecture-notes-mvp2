# How to Run the Lecture Notes Generator

This guide will walk you through running the project step by step.

## Prerequisites

- Python 3.8 or higher installed
- API keys for:
  - [Deepgram](https://console.deepgram.com/) (for transcription)
  - [Google Gemini](https://ai.google.dev/gemini-api/docs/api-key) (for summarization)

## Step-by-Step Setup

### Step 1: Open Terminal/Command Prompt

Navigate to your project directory:
```bash
cd "C:\Users\hp\OneDrive - Higher Education Commission\Desktop\lecture-notes-mvp2"
```

### Step 2: Create Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

### Step 3: Install Dependencies

With the virtual environment activated, run:
```bash
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Deepgram SDK (transcription)
- Google Gemini SDK (summarization)
- SQLAlchemy (database)
- And other dependencies

### Step 4: Set Up Environment Variables

1. Create a `.env` file in the project root directory (same level as `requirements.txt`)

2. Copy the template from `.env.example`:
   ```bash
   # On Windows PowerShell:
   Copy-Item .env.example .env
   
   # On Windows CMD:
   copy .env.example .env
   
   # On macOS/Linux:
   cp .env.example .env
   ```

3. Open the `.env` file and add your API keys:
   ```
   DEEPGRAM_API_KEY=your_actual_deepgram_key_here
   GEMINI_API_KEY=your_actual_gemini_key_here
   ```

   **Important:** Replace the placeholder values with your actual API keys (without quotes).

### Step 5: Run the Server

From the project root directory, run:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Started server process
INFO:     Waiting for application startup.
Database initialized successfully.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 6: Open in Browser

Open your web browser and go to:
```
http://localhost:8000
```

You should see the Lecture Notes Generator interface.

## Testing the Application

1. **Upload an Audio File:**
   - Click the upload area or drag and drop an audio file
   - Supported formats: MP3, WAV, M4A, OGG, FLAC
   - Maximum file size: 20 MB

2. **Process the File:**
   - Click "Upload & Generate Notes"
   - Wait for processing (transcription + summarization)
   - Results will appear below

3. **View History:**
   - Scroll down to see "Upload History"
   - Click any previous upload to view its transcript and notes

## Troubleshooting

### "Module not found" error
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt` again

### "API key not set" error
- Check that your `.env` file exists in the project root
- Verify the API keys are correct (no extra spaces or quotes)
- Restart the server after creating/editing `.env`

### "Database initialized successfully" not appearing
- Check that SQLAlchemy and aiosqlite are installed
- The database file (`lecture_notes.db`) will be created automatically

### Server won't start
- Make sure port 8000 is not already in use
- Try a different port: `--port 8001`
- Check for Python syntax errors in the code

### Upload doesn't work
- Open browser console (F12) and check for errors
- Verify the server is running and accessible
- Check that API keys are valid

## Stopping the Server

Press `CTRL+C` in the terminal where the server is running.

## Quick Test Script

You can verify your setup is correct by running:
```bash
python test_setup.py
```

This will check:
- ✓ All dependencies are installed
- ✓ .env file exists and has API keys
- ✓ Database module can be imported

## Next Steps

Once everything is working:
- Upload your first lecture audio file
- View the generated transcript and notes
- Check the upload history
- Download notes as text files

Enjoy using your Lecture Notes Generator! 🎓

