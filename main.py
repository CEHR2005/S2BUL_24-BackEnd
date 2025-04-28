from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.database import Base, engine, connect_with_retries, logger
from app.routes import auth, users, movies, comments, ratings, statistics
from app.database.init_db import init_db
import sys

# Try to connect to the database with retries
if not connect_with_retries(max_retries=5, retry_interval=5):
    logger.error("Could not connect to the database. Exiting...")
    sys.exit(1)

# Create database tables
try:
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    sys.exit(1)

# Initialize database with test data
try:
    logger.info("Initializing database with test data...")
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Error initializing database: {str(e)}")
    # Continue even if initialization fails, as this is not critical

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=None,  # Don't use regex matching
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(movies.router, prefix=f"{settings.API_V1_STR}/movies", tags=["movies"])
app.include_router(comments.router, prefix=f"{settings.API_V1_STR}/comments", tags=["comments"])
app.include_router(ratings.router, prefix=f"{settings.API_V1_STR}/ratings", tags=["ratings"])
app.include_router(statistics.router, prefix=f"{settings.API_V1_STR}/statistics", tags=["statistics"])


@app.get("/")
async def root():
    return {"message": "Movie Rating API"}
