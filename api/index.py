"""
Vercel serverless function entry point for FastAPI app.
Uses Mangum to properly wrap FastAPI for serverless environments.
"""
import sys
import os
import traceback

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set environment to handle serverless
os.environ.setdefault("VERCEL", "1")

# Try to import and setup
try:
    print("Starting import...")
    # Import the FastAPI app
    from backend.main import app
    print("FastAPI app imported successfully")
    
    # Use Mangum to wrap FastAPI for serverless
    from mangum import Mangum
    print("Mangum imported successfully")
    
    # Create handler for Vercel
    handler = Mangum(app, lifespan="off")
    print("Handler created successfully")
    
except Exception as e:
    # Log the full error
    error_traceback = traceback.format_exc()
    print(f"ERROR during initialization: {str(e)}")
    print(f"Traceback: {error_traceback}")
    
    # Create a minimal error handler if import fails
    try:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        from mangum import Mangum
        
        error_app = FastAPI()
        
        @error_app.get("/")
        @error_app.get("/{path:path}")
        async def error_handler(path: str = ""):
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Failed to initialize application",
                    "message": str(e),
                    "type": type(e).__name__,
                    "traceback": error_traceback
                }
            )
        
        handler = Mangum(error_app, lifespan="off")
        print("Error handler created")
    except Exception as e2:
        # Last resort - create a simple handler
        def handler(event, context):
            return {
                "statusCode": 500,
                "body": f"Critical error: {str(e)} | Secondary error: {str(e2)}"
            }
