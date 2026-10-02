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
# Priority: DATABASE_URL (explicit Postgres URI) > SUPABASE_URL (if postgres://) > SQLite fallback
DATABASE_URL = os.getenv("DATABASE_URL", "")


def _make_pg_url(raw_url: str) -> str:
    """
    Safely construct a psycopg2 SQLAlchemy URL from a raw Postgres connection string.
    Handles passwords that contain special characters (e.g. '@') by parsing components.
    """
    from urllib.parse import urlparse, quote_plus
    from sqlalchemy import URL

    # Normalise scheme for parsing
    normalized = raw_url.replace("postgres://", "postgresql://", 1)
    parsed = urlparse(normalized)

    return URL.create(
        drivername="postgresql+psycopg2",
        username=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path.lstrip("/"),
    )


if DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://"):
    db_url = _make_pg_url(DATABASE_URL)
    logger.info("Using PostgreSQL database connection (DATABASE_URL).")
elif SUPABASE_URL.startswith("postgres://") or SUPABASE_URL.startswith("postgresql://"):
    db_url = _make_pg_url(SUPABASE_URL)
    logger.info("Using PostgreSQL database connection (SUPABASE_URL).")
else:
    db_url = "sqlite:///./cartiq.db"
    logger.info("Using SQLite local database engine (cartiq.db).")

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if isinstance(db_url, str) and "sqlite" in db_url else {}
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
