"""
Quick test script to verify the setup is correct.
Run this before starting the server to check for common issues.
"""
import os
import sys

def check_dependencies():
    """Check if all required packages are installed."""
    print("Checking dependencies...")
    required_packages = [
        'fastapi',
        'uvicorn',
        'deepgram',
        'google.genai',
        'dotenv',
        'aiofiles',
        'sqlalchemy',
        'aiosqlite'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'google.genai':
                __import__('google.genai')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All dependencies installed!")
        return True

def check_env_file():
    """Check if .env file exists and has required keys."""
    print("\nChecking .env file...")
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print("  ✗ .env file not found")
        print("  Create a .env file with:")
        print("    DEEPGRAM_API_KEY=your_key_here")
        print("    GEMINI_API_KEY=your_key_here")
        return False
    
    print("  ✓ .env file exists")
    
    # Check for required keys (without exposing values)
    from dotenv import load_dotenv
    load_dotenv()
    
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not deepgram_key:
        print("  ✗ DEEPGRAM_API_KEY not set")
    else:
        print("  ✓ DEEPGRAM_API_KEY is set")
    
    if not gemini_key:
        print("  ✗ GEMINI_API_KEY not set")
    else:
        print("  ✓ GEMINI_API_KEY is set")
    
    if not deepgram_key or not gemini_key:
        return False
    
    return True

def check_database_import():
    """Check if database module can be imported."""
    print("\nChecking database setup...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from database import init_db, get_db, LectureUpload
        print("  ✓ Database module imports successfully")
        return True
    except Exception as e:
        print(f"  ✗ Database import failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Lecture Notes MVP - Setup Verification")
    print("=" * 50)
    
    all_ok = True
    all_ok = check_dependencies() and all_ok
    all_ok = check_env_file() and all_ok
    all_ok = check_database_import() and all_ok
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✓ All checks passed! You can start the server with:")
        print("  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("=" * 50)

if __name__ == "__main__":
    main()

