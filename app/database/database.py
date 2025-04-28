from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
import time
import logging

from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL connection URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Function to connect to the database with retries
def connect_with_retries(max_retries=5, retry_interval=5):
    """
    Attempt to connect to the database with retries.

    Args:
        max_retries (int): Maximum number of retry attempts
        retry_interval (int): Time in seconds between retry attempts

    Returns:
        bool: True if connection successful, False otherwise
    """
    retries = 0
    while retries < max_retries:
        try:
            # Try to connect to the database
            with engine.connect() as conn:
                logger.info("Successfully connected to the database")
                return True
        except OperationalError as e:
            retries += 1
            if retries < max_retries:
                logger.warning(f"Database connection failed. Retrying in {retry_interval} seconds... ({retries}/{max_retries})")
                logger.warning(f"Error: {str(e)}")
                time.sleep(retry_interval)
            else:
                logger.error(f"Failed to connect to the database after {max_retries} attempts")
                logger.error(f"Error: {str(e)}")
                return False

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
