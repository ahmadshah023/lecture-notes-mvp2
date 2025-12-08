"""
Vercel serverless function entry point for FastAPI app.
This file wraps the FastAPI app for Vercel's serverless environment.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the FastAPI app
from backend.main import app

# Vercel's Python runtime automatically handles FastAPI apps
# The app is exported directly
