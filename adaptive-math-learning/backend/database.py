"""
Database configuration and session management.

Supports:
- SQLite for development
- PostgreSQL/Supabase for production
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool, QueuePool
from pathlib import Path

from .config import get_settings


settings = get_settings()


def get_engine():
    """
    Create database engine based on configuration.

    For SQLite: Uses StaticPool with check_same_thread=False
    For PostgreSQL: Uses QueuePool with configurable pool size
    """
    if settings.is_postgres:
        # PostgreSQL/Supabase configuration
        return create_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            poolclass=QueuePool,
            echo=settings.debug,
        )
    else:
        # SQLite configuration (development)
        # Ensure data directory exists
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        return create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.debug,
        )


# Create engine
engine = get_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session.

    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """
    Async version of get_db for async contexts.

    Note: For full async support with PostgreSQL,
    use asyncpg with SQLAlchemy's async engine.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables (for testing)."""
    Base.metadata.drop_all(bind=engine)


def check_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
