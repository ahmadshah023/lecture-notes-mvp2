# How to Push Your Project to GitHub

Follow these steps to push your Lecture Notes Generator to GitHub.

## Step 1: Create a GitHub Repository

1. Go to [github.com](https://github.com) and sign in (or create an account)
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in:
   - **Repository name:** `lecture-notes-mvp2` (or your preferred name)
   - **Description:** "Lecture Notes Generator - Transcribe and summarize audio lectures"
   - **Visibility:** Choose **Public** (free) or **Private**
   - **DO NOT** check "Initialize with README" (we already have files)
4. Click **"Create repository"**

## Step 2: Initialize Git in Your Project (if not already done)

Open PowerShell in your project directory and run:

```powershell
# Navigate to your project folder
cd "C:\Users\hp\OneDrive - Higher Education Commission\Desktop\lecture-notes-mvp2"

# Initialize git (if not already done)
git init

# Set your branch name to 'main'
git branch -M main
```

## Step 3: Add All Files

```powershell
# Add all files to git
git add .

# Check what will be committed (optional)
git status
```

**Important:** Make sure these files are NOT committed (they should be in .gitignore):
- ❌ `.env` (contains your API keys - NEVER commit this!)
- ❌ `venv/` (virtual environment)
- ❌ `*.db` (database files)
- ❌ `__pycache__/` (Python cache)

## Step 4: Make Your First Commit

```powershell
# Commit your files
git commit -m "Initial commit: Lecture Notes Generator MVP"
```

## Step 5: Connect to GitHub

Replace `YOUR_USERNAME` with your actual GitHub username:

```powershell
# Add GitHub as remote repository
git remote add origin https://github.com/YOUR_USERNAME/lecture-notes-mvp2.git

# Verify it was added
git remote -v
```

## Step 6: Push to GitHub

```powershell
# Push your code to GitHub
git push -u origin main
```

**Note:** You'll be prompted for your GitHub username and password:
- **Username:** Your GitHub username
- **Password:** Use a **Personal Access Token** (not your GitHub password)
  - See below for how to create one

## Step 7: Create a Personal Access Token (if needed)

If GitHub asks for a password, you need a Personal Access Token:

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **"Generate new token (classic)"**
3. Give it a name: `lecture-notes-project`
4. Select scopes: Check **`repo`** (full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token immediately** (you won't see it again!)
7. Use this token as your password when pushing

## Step 8: Verify Upload

1. Go to your GitHub repository page
2. You should see all your files:
   - ✅ `backend/`
   - ✅ `frontend/`
   - ✅ `requirements.txt`
   - ✅ `render.yaml`
   - ✅ `README.md`
   - ✅ `.gitignore`
   - ❌ `.env` (should NOT be there)
   - ❌ `venv/` (should NOT be there)
   - ❌ `*.db` (should NOT be there)

## Troubleshooting

### "Repository not found" error
- Check that the repository name matches exactly
- Verify you have access to the repository
- Make sure you're using the correct GitHub username

### "Authentication failed" error
- Use a Personal Access Token instead of password
- Make sure the token has `repo` permissions

### "Files not showing up"
- Check `.gitignore` - files listed there won't be uploaded
- Run `git status` to see what files are tracked

### "Permission denied"
- Make sure you're logged into GitHub
- Check your Personal Access Token has correct permissions

## Quick Command Summary

```powershell
# Navigate to project
cd "C:\Users\hp\OneDrive - Higher Education Commission\Desktop\lecture-notes-mvp2"

# Initialize (if needed)
git init
git branch -M main

# Add files
git add .

# Commit
git commit -m "Initial commit: Lecture Notes Generator MVP"

# Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/lecture-notes-mvp2.git

# Push
git push -u origin main
```

## After Pushing

Once your code is on GitHub, you can:
1. ✅ Deploy to Render.com (it will connect to your GitHub repo)
2. ✅ Share your code with others
3. ✅ Track changes and versions
4. ✅ Collaborate with others

---

**Need help?** Check GitHub's official guide: https://docs.github.com/en/get-started/quickstart/create-a-repo

