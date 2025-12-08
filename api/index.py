"""
Vercel serverless function entry point for FastAPI app.
"""
import sys
import os

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set environment to handle serverless
os.environ.setdefault("VERCEL", "1")

try:
    # Import the FastAPI app
    from backend.main import app
    
    # Export the app for Vercel
    # Vercel's Python runtime will automatically handle FastAPI apps
    handler = app
    
except Exception as e:
    # Create a minimal error handler if import fails
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    error_app = FastAPI()
    
    @error_app.get("/")
    @error_app.get("/{path:path}")
    async def error_handler(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to initialize application",
                "message": str(e),
                "type": type(e).__name__
            }
        )
    
    handler = error_app
