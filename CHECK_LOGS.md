# How to Check Runtime Logs (Not Build Logs)

The build is successful, but the function crashes at **runtime**. You need to check **Runtime Logs**, not Build Logs.

## Step 1: Check Runtime Logs

1. Go to **Vercel Dashboard** → Your Project
2. Click **"Logs"** tab (at the top, next to "Deployments")
3. OR go to **"Functions"** tab → Click on the function → "View Logs"
4. Look for:
   - Python errors
   - Import errors
   - Tracebacks
   - Any error messages

**Important:** These are different from Build Logs. Build logs show the build process, Runtime logs show what happens when the function executes.

## Step 2: Test with Minimal Handler

I've created `api/test.py` - a minimal FastAPI app to test if the basic setup works.

**Temporarily** update `vercel.json`:

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

Then:
1. Push to GitHub
2. Redeploy
3. Visit your Vercel URL

If `api/test.py` works, the issue is with your main app imports.
If `api/test.py` also crashes, there's a fundamental setup issue.

## Step 3: Common Runtime Issues

### Issue 1: Import Path Problems
The error might be: `ModuleNotFoundError: No module named 'backend'`

**Solution:** Check if the import path is correct in `api/index.py`

### Issue 2: Database Initialization
SQLite might be failing in serverless environment

### Issue 3: Missing Dependencies at Runtime
Some packages might not be installed correctly

### Issue 4: Environment Variables
Missing API keys might cause initialization to fail silently

## Step 4: Enable Detailed Logging

The updated `api/index.py` should print errors. Check the Runtime Logs to see:
- "Starting import..."
- "FastAPI app imported successfully"
- Or any error messages

## What to Do Next

1. **Check Runtime Logs** (not Build Logs)
2. **Share the error message** from Runtime Logs
3. **Test with `api/test.py`** to isolate the issue

The Runtime Logs will show the actual error that's causing the crash.

