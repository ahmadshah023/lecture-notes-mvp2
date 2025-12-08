# Deploying to Render.com

This guide will walk you through deploying your Lecture Notes Generator to Render.com.

## Prerequisites

- A GitHub account (or GitLab/Bitbucket)
- Your project pushed to a Git repository
- Render.com account (free tier available)
- Your API keys ready (Deepgram and Gemini)

## Step 1: Prepare Your Repository

1. **Make sure your project is on GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Important files to include:**
   - ✅ `requirements.txt`
   - ✅ `render.yaml`
   - ✅ `backend/` directory
   - ✅ `frontend/` directory
   - ❌ `.env` (DO NOT commit this - use Render environment variables)
   - ❌ `venv/` (DO NOT commit)
   - ❌ `*.db` (DO NOT commit - database will be created on Render)

## Step 2: Create a Render Account

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account (recommended)
3. Verify your email

## Step 3: Create a New Web Service

1. **Click "New +" → "Web Service"**

2. **Connect your repository:**
   - Select your GitHub account
   - Choose your `lecture-notes-mvp2` repository
   - Click "Connect"

3. **Configure the service:**
   - **Name:** `lecture-notes-backend` (or your preferred name)
   - **Environment:** `Python 3`
   - **Region:** Choose closest to you
   - **Branch:** `main` (or your default branch)
   - **Root Directory:** Leave empty (or `./` if needed)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

   **OR** use the `render.yaml` file (recommended):
   - Render will automatically detect `render.yaml` and use those settings

4. **Set Environment Variables:**
   Click "Advanced" → "Add Environment Variable" and add:
   - `DEEPGRAM_API_KEY` = your Deepgram API key
   - `GEMINI_API_KEY` = your Gemini API key
   - `PYTHON_VERSION` = `3.12.0` (optional, but recommended)

5. **Choose Plan:**
   - Select **Free** plan (good for testing)
   - Note: Free tier spins down after 15 minutes of inactivity

6. **Click "Create Web Service"**

## Step 4: Wait for Deployment

- Render will automatically:
  1. Clone your repository
  2. Install dependencies from `requirements.txt`
  3. Build your application
  4. Start the server

- Watch the logs for:
  - ✅ "Database initialized successfully"
  - ✅ "Uvicorn running on..."
  - ✅ Build completed successfully

## Step 5: Access Your Application

Once deployed, you'll get a URL like:
```
https://lecture-notes-backend.onrender.com
```

**Note:** On the free tier, the first request after inactivity may take 30-60 seconds (cold start).

## Step 6: Update CORS (if needed)

If you're hosting the frontend separately, update CORS in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Important Notes

### Database on Render

- **SQLite database** (`lecture_notes.db`) will be created automatically
- **⚠️ Data persistence:** On free tier, the database is stored in ephemeral storage
- **⚠️ Data loss:** If your service is deleted or redeployed, data may be lost
- **💡 Solution:** For production, consider upgrading to a paid plan with persistent storage, or use PostgreSQL (Render provides free PostgreSQL)

### Free Tier Limitations

- **Spins down** after 15 minutes of inactivity
- **Cold starts** take 30-60 seconds
- **Limited resources** (512MB RAM)
- **No persistent storage** (data may be lost on redeploy)

### Upgrading to Paid Plan

For production use:
- **Starter Plan ($7/month):**
  - Always-on (no spin-down)
  - Persistent storage
  - Better performance
  - Custom domains

## Troubleshooting

### Build Fails

1. **Check logs** in Render dashboard
2. **Verify** `requirements.txt` has all dependencies
3. **Check** Python version compatibility

### Service Won't Start

1. **Check start command:** Must use `$PORT` variable
2. **Check logs** for error messages
3. **Verify** environment variables are set correctly

### Database Issues

1. **Check** database file permissions
2. **Verify** SQLite is working (check logs)
3. **Consider** upgrading to PostgreSQL for production

### API Errors

1. **Verify** API keys are set correctly in Render environment variables
2. **Check** API key format (no extra spaces/quotes)
3. **Test** API keys locally first

## Testing Your Deployment

1. **Visit your Render URL**
2. **Upload a test audio file**
3. **Check** the history section works
4. **Verify** database is saving data

## Next Steps

- ✅ Set up custom domain (paid plans)
- ✅ Add PostgreSQL database (for persistent storage)
- ✅ Set up monitoring and alerts
- ✅ Configure auto-deploy from Git

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Your app logs: Available in Render dashboard

---

**Congratulations!** Your Lecture Notes Generator is now live on Render.com! 🎉

