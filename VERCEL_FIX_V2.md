# Vercel 500 Error - Fix V2 (Using Mangum)

I've applied a more robust fix using **Mangum**, which is the proper way to wrap FastAPI for serverless environments like Vercel.

## What Changed:

1. **Added Mangum** - ASGI adapter for serverless (required for Vercel)
2. **Updated api/index.py** - Now properly wraps FastAPI with Mangum
3. **Better error handling** - Shows detailed error messages if initialization fails
4. **Lazy database init** - Database initializes on first use (better for serverless)

## Next Steps:

1. **Push to GitHub:**
   ```powershell
   git add .
   git commit -m "Fix Vercel: Add Mangum for proper FastAPI serverless support"
   git push
   ```

2. **Redeploy on Vercel:**
   - Vercel will auto-redeploy, OR
   - Go to Dashboard → Your Project → "Redeploy"

3. **Check Logs:**
   - Vercel Dashboard → Your Project → "Logs"
   - Look for any import errors or initialization issues

## If Still Getting Errors:

The error handler will now show detailed error messages. Check:

1. **Vercel Logs** - Look for the actual error message
2. **Environment Variables** - Make sure both API keys are set:
   - `DEEPGRAM_API_KEY`
   - `GEMINI_API_KEY`

3. **Common Issues:**
   - Missing dependencies (check requirements.txt)
   - Import path errors
   - Database permission errors

## Testing:

After redeploy, visit:
- `https://your-app.vercel.app/` - Should show frontend
- `https://your-app.vercel.app/test-deepgram` - Should test API

If you see an error page, it will now show the actual error message instead of a generic 500.

