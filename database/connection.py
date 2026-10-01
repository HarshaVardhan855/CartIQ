"""
Database Connection Manager for CartIQ (Supabase PostgreSQL / Client & SQLite fallback).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from utils.logger import logger

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase_client = None

# Initialize native Supabase SDK client if HTTP API URL & key provided
if SUPABASE_URL.startswith("http") and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Initialized native Supabase SDK client.")
    except Exception as e:
        logger.warning(f"Could not initialize Supabase SDK client: {e}")

# Determine SQLAlchemy Engine URL
if SUPABASE_URL.startswith("postgres://") or SUPABASE_URL.startswith("postgresql://"):
    db_url = SUPABASE_URL.replace("postgres://", "postgresql://")
    logger.info("Using PostgreSQL database connection.")
else:
    db_url = "sqlite:///./cartiq.db"
    logger.info("Using SQLite local database engine (cartiq.db).")

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Creates database tables if they do not exist.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

def get_db():
    """
    Dependency generator for database sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
