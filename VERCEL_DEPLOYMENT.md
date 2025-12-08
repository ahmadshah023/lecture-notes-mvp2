# Deploying to Vercel

This guide will help you deploy your Lecture Notes Generator to Vercel.

## ⚠️ Important Notes About Vercel

**Limitations:**
- ✅ Vercel supports FastAPI via serverless functions
- ⚠️ SQLite database has limitations (ephemeral storage)
- ⚠️ File uploads are limited to 4.5MB per request
- ⚠️ Cold starts may occur (first request after inactivity)

**Recommendations:**
- For production with database, consider Render.com or Railway
- For simple deployments, Vercel works great
- Consider using Vercel Postgres for persistent storage

## Prerequisites

- Vercel account (free tier available)
- GitHub account
- Your project pushed to GitHub

## Step 1: Prepare Your Project

### 1.1 Create Required Files

I've created these files for you:
- ✅ `vercel.json` - Vercel configuration
- ✅ `api/index.py` - Serverless function entry point

### 1.2 Update Database for Vercel (Optional but Recommended)

Since Vercel uses ephemeral storage, consider:
- Using Vercel Postgres (free tier available)
- Or accepting that data resets on each deployment

For now, SQLite will work but data won't persist between deployments.

### 1.3 Update File Size Limit

Vercel has a 4.5MB limit per request. Update `backend/main.py`:

```python
MAX_FILE_SIZE_MB = 4  # Reduced from 20MB for Vercel
```

## Step 2: Push to GitHub

Make sure your code is on GitHub:

```powershell
git add .
git commit -m "Add Vercel configuration"
git push
```

## Step 3: Deploy to Vercel

### Method 1: Using Vercel Dashboard (Recommended)

1. **Go to [vercel.com](https://vercel.com)** and sign in
2. **Click "Add New..." → "Project"**
3. **Import your GitHub repository:**
   - Select your GitHub account
   - Choose `lecture-notes-mvp2` repository
   - Click "Import"

4. **Configure Project:**
   - **Framework Preset:** Other (or leave as auto-detected)
   - **Root Directory:** `./` (leave as default)
   - **Build Command:** Leave empty (Vercel will auto-detect)
   - **Output Directory:** Leave empty
   - **Install Command:** `pip install -r requirements.txt`

5. **Environment Variables:**
   Click "Environment Variables" and add:
   - `DEEPGRAM_API_KEY` = (your Deepgram API key)
   - `GEMINI_API_KEY` = (your Gemini API key)

6. **Click "Deploy"**

### Method 2: Using Vercel CLI

```powershell
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? lecture-notes-mvp2
# - Directory? ./
# - Override settings? No

# Add environment variables
vercel env add DEEPGRAM_API_KEY
vercel env add GEMINI_API_KEY

# Deploy to production
vercel --prod
```

## Step 4: Verify Deployment

1. **Wait for build to complete** (usually 2-5 minutes)
2. **Visit your deployment URL:** `https://your-project-name.vercel.app`
3. **Test the application:**
   - Upload a small audio file (< 4MB)
   - Check if transcription works
   - Verify history is working

## Step 5: Configure Custom Domain (Optional)

1. Go to your project settings
2. Click "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

## Troubleshooting

### Build Fails

**Error: "Module not found"**
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility

**Error: "Cannot find module backend"**
- Make sure `backend/` directory exists
- Check `vercel.json` paths are correct

### Runtime Errors

**Error: "Database file not found"**
- SQLite creates files in `/tmp` on Vercel (ephemeral)
- Data resets on each deployment
- Consider using Vercel Postgres for persistence

**Error: "Request entity too large"**
- Vercel has 4.5MB limit per request
- Reduce `MAX_FILE_SIZE_MB` in `backend/main.py`

**Error: "Function timeout"**
- Vercel free tier: 10 seconds timeout
- Paid tier: 60 seconds
- Large files may timeout - consider splitting

### Cold Starts

- First request after inactivity takes 5-10 seconds
- This is normal for serverless functions
- Consider upgrading to Pro plan for better performance

## Upgrading to Vercel Postgres (Recommended)

For persistent database storage:

1. **In Vercel Dashboard:**
   - Go to "Storage" tab
   - Click "Create Database"
   - Select "Postgres"
   - Choose "Free" plan

2. **Update `backend/database.py`:**
   ```python
   # Get connection string from Vercel environment
   DATABASE_URL = os.getenv("POSTGRES_URL", "sqlite:///./lecture_notes.db")
   ```

3. **Update `requirements.txt`:**
   ```
   psycopg2-binary~=2.9.9
   ```

4. **Redeploy**

## File Size Limitations

Vercel limits:
- **Free tier:** 4.5MB per request
- **Pro tier:** 4.5MB per request (same)

**Solutions:**
- Compress audio files before upload
- Use external storage (S3, Cloudinary) for large files
- Split large files into chunks

## Environment Variables

Set these in Vercel Dashboard:
- `DEEPGRAM_API_KEY`
- `GEMINI_API_KEY`
- `POSTGRES_URL` (if using Postgres)

## Monitoring

- **Logs:** Available in Vercel Dashboard → "Logs" tab
- **Analytics:** Available in "Analytics" tab (Pro plan)
- **Functions:** Check "Functions" tab for execution times

## Cost

- **Free tier:** 
  - 100GB bandwidth/month
  - 100 serverless function executions/day
  - Perfect for testing/small projects

- **Pro tier ($20/month):**
  - Unlimited bandwidth
  - Better performance
  - Analytics included

## Comparison: Vercel vs Render

| Feature | Vercel | Render |
|---------|--------|--------|
| **Deployment** | Serverless | Traditional server |
| **Cold Starts** | Yes (5-10s) | No (always-on) |
| **File Size Limit** | 4.5MB | 20MB+ |
| **Database** | Ephemeral (or Postgres) | Persistent |
| **Free Tier** | ✅ Generous | ✅ Limited |
| **Best For** | Small apps, APIs | Full-stack apps |

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Test with small files
3. ⚠️ Consider Postgres for database persistence
4. ⚠️ Monitor function execution times
5. 💡 Upgrade to Pro if needed

---

**Need Help?**
- Vercel Docs: https://vercel.com/docs
- Vercel Community: https://github.com/vercel/vercel/discussions

