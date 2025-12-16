"""
Vercel serverless entrypoint for the FastAPI app.
Exports the ASGI app directly (no Mangum) to avoid Vercel's handler
auto-detection calling issubclass() on non-class objects.
"""
import sys
import os
import traceback

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mark environment as Vercel so backend can switch to /tmp SQLite
os.environ.setdefault("VERCEL", "1")

try:
    print("Starting import...")
    from backend.main import app as fastapi_app
    print("FastAPI app imported successfully")

    # Expose ASGI app for Vercel's Python runtime
    app = fastapi_app
    __all__ = ["app"]
    print("ASGI app exported for Vercel")

except Exception as e:
    # Log the full error for Vercel runtime logs
    error_traceback = traceback.format_exc()
    print(f"ERROR during initialization: {str(e)}")
    print(f"Traceback: {error_traceback}")

    # Fallback minimal FastAPI app to surface the error in HTTP response
    try:
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
                    "type": type(e).__name__,
                    "traceback": error_traceback,
                },
            )

        app = error_app
        __all__ = ["app"]
        print("Fallback error app exported")
    except Exception as e2:
        # Last resort: plain dict response
        def app(event, context):
            return {
                "statusCode": 500,
                "body": f"Critical error: {str(e)} | Secondary error: {str(e2)}",
            }
