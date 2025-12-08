"""
Database models and setup for storing lecture upload history.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - using SQLite for simplicity
# For Vercel/serverless, use /tmp directory (writable)
if os.getenv("VERCEL"):
    # Vercel serverless environment - use /tmp
    DATABASE_URL = "sqlite:////tmp/lecture_notes.db"
else:
    # Local or other environments
    DATABASE_URL = "sqlite:///./lecture_notes.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class LectureUpload(Base):
    """Model for storing lecture upload history."""
    __tablename__ = "lecture_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String, nullable=False)  # MIME type
    transcript = Column(Text, nullable=False)
    notes = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def init_db():
    """Initialize the database by creating all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database initialization error: {e}")
        # In serverless, this might fail on first call, but will work on subsequent calls
        raise


def get_db():
    """Dependency function to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

