"""
Vercel serverless function entry point for FastAPI app.
Uses Mangum to properly wrap FastAPI for serverless environments.
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
    
    # Use Mangum to wrap FastAPI for serverless
    from mangum import Mangum
    
    # Create handler for Vercel
    handler = Mangum(app, lifespan="off")
    
except Exception as e:
    # Create a minimal error handler if import fails
    import traceback
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from mangum import Mangum
    
    error_app = FastAPI()
    
    @error_app.get("/")
    @error_app.get("/{path:path}")
    async def error_handler(path: str = ""):
        error_details = {
            "error": "Failed to initialize application",
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(f"Initialization error: {error_details}")
        return JSONResponse(
            status_code=500,
            content=error_details
        )
    
    handler = Mangum(error_app, lifespan="off")
