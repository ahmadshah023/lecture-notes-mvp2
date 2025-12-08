"""
Simple script to view the lecture uploads database.
Run this script to see all your uploaded lectures and their details.
"""
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import SessionLocal, LectureUpload

def view_database():
    """Display all lecture uploads from the database."""
    db = SessionLocal()
    try:
        uploads = db.query(LectureUpload).order_by(LectureUpload.created_at.desc()).all()
        
        if not uploads:
            print("\n📭 No uploads found in the database.")
            print("Upload some audio files to see them here!\n")
            return
        
        print("\n" + "="*80)
        print(f"📚 LECTURE UPLOADS DATABASE - {len(uploads)} total upload(s)")
        print("="*80 + "\n")
        
        for idx, upload in enumerate(uploads, 1):
            print(f"📄 Upload #{upload.id}")
            print(f"   Filename: {upload.filename}")
            print(f"   Size: {upload.file_size / 1024 / 1024:.2f} MB")
            print(f"   Type: {upload.file_type}")
            print(f"   Uploaded: {upload.created_at.strftime('%Y-%m-%d %H:%M:%S') if upload.created_at else 'Unknown'}")
            
            # Show transcript preview (first 100 characters)
            transcript_preview = upload.transcript[:100] + "..." if len(upload.transcript) > 100 else upload.transcript
            print(f"   Transcript Preview: {transcript_preview}")
            
            # Show notes preview (first 100 characters)
            notes_preview = upload.notes[:100] + "..." if len(upload.notes) > 100 else upload.notes
            print(f"   Notes Preview: {notes_preview}")
            
            print("-" * 80)
            print()
        
        print(f"\n✅ Total: {len(uploads)} upload(s)\n")
        
    except Exception as e:
        print(f"\n❌ Error reading database: {e}\n")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    view_database()
