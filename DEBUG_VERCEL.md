# Debugging Vercel 500 Error

The function is still crashing. Here's how to find the actual error:

## Step 1: Check Vercel Logs

1. Go to **Vercel Dashboard** → Your Project
2. Click **"Logs"** tab (or "Functions" → "View Logs")
3. Look for:
   - Python tracebacks
   - Import errors
   - Initialization errors
   - Any error messages

The logs will show the actual error that's causing the crash.

## Step 2: Common Issues to Check

### Issue 1: Missing Dependencies
Check if all packages are in `requirements.txt`:
- ✅ fastapi
- ✅ mangum
- ✅ uvicorn
- ✅ requests
- ✅ sqlalchemy
- ✅ aiosqlite
- ✅ etc.

### Issue 2: Import Path Errors
The error might be:
- `ModuleNotFoundError: No module named 'backend'`
- `ImportError: cannot import name 'app'`

### Issue 3: Database Initialization
SQLite might be failing in `/tmp` directory

### Issue 4: Environment Variables
Missing API keys might cause initialization to fail

## Step 3: Test Locally with Vercel CLI

```powershell
# Install Vercel CLI
npm install -g vercel

# Test locally
vercel dev
```

This will show errors in your local terminal.

## Step 4: Simplified Test

Create a minimal test to see if basic FastAPI works:

Create `api/test.py`:
```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Vercel"}

handler = Mangum(app, lifespan="off")
```

Update `vercel.json`:
```json
{
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/test.py"
    }
  ]
}
```

If this works, the issue is with your main app imports.

## Step 5: Share the Error

Once you check the logs, share:
1. The actual error message from Vercel logs
2. The full traceback
3. Any import errors

This will help identify the exact issue.

