"""Database connection and management."""

from contextlib import contextmanager
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

# Try to import SQLAlchemy
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, declarative_base
    from sqlalchemy.pool import QueuePool
    
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    logger.warning("SQLAlchemy not installed. Database features will be unavailable.")
    SQLALCHEMY_AVAILABLE = False
    Base = None
    engine = None
    SessionLocal = None

if SQLALCHEMY_AVAILABLE:
    # Create SQLAlchemy Base
    Base = declarative_base()

    # Create engine
    engine = create_engine(
        settings.database.database_url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )

    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    if not SQLALCHEMY_AVAILABLE:
        logger.error("SQLAlchemy not available. Cannot initialize database.")
        return False
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@contextmanager
def get_db():
    """Get database session context manager.

    Usage:
        with get_db() as db:
            # Use db session
            pass
    """
    if not SQLALCHEMY_AVAILABLE:
        logger.error("SQLAlchemy not available. Cannot create database session.")
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def get_db_session():
    """Get database session (for dependency injection).

    Returns:
        Database session or None if SQLAlchemy not available
    """
    if not SQLALCHEMY_AVAILABLE:
        logger.error("SQLAlchemy not available. Cannot create database session.")
        return None
    
    return SessionLocal()
