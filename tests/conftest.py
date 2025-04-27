import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.core.config import settings
from main import app

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a fresh database session for each test."""
    # Drop all tables and recreate them for each test
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_data(db_session):
    """Create test data for the database."""
    from app.models.user import User
    from app.models.movie import Movie
    from app.models.rating import Rating
    import uuid

    # Create test users with different demographics
    users = [
        User(
            id=uuid.uuid4(),
            username=f"user{i}",
            email=f"user{i}@example.com",
            password="hashed_password",
            first_name=f"First{i}",
            last_name=f"Last{i}",
            age=age,
            gender=gender,
            country=country,
            continent=continent,
            is_admin=False
        )
        for i, (age, gender, country, continent) in enumerate([
            (16, "male", "USA", "north_america"),
            (20, "female", "Canada", "north_america"),
            (30, "male", "UK", "europe"),
            (40, "female", "Germany", "europe"),
            (50, "other", "Japan", "asia"),
            (60, "male", "Australia", "australia"),
            (25, "female", "Brazil", "south_america"),
            (35, "male", "South Africa", "africa"),
            (45, None, None, None)  # User with unspecified demographics
        ])
    ]

    # Create test movie
    movie = Movie(
        id=uuid.uuid4(),
        title="Test Movie",
        release_year=2023,
        director="Test Director",
        cast=["Actor 1", "Actor 2"],
        genre=["Action", "Drama"],
        plot="Test plot description",
        duration=120,
        poster_url="http://example.com/poster.jpg",
        images=["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    )

    # Add users and movie to the database
    for user in users:
        db_session.add(user)
    db_session.add(movie)
    db_session.commit()

    # Create ratings for the movie
    ratings = [
        Rating(
            id=uuid.uuid4(),
            movie_id=movie.id,
            user_id=users[i].id,
            score=score
        )
        for i, score in enumerate([10, 8, 7, 9, 6, 8, 7, 9, 5])  # One rating per user
    ]

    # Add ratings to the database
    for rating in ratings:
        db_session.add(rating)
    db_session.commit()

    # Return the test data
    return {
        "users": users,
        "movie": movie,
        "ratings": ratings
    }

@pytest.fixture
def admin_token(db_session):
    """Create an admin user and return a token for that user."""
    from app.core.security import get_password_hash
    from app.core.security import create_access_token
    from app.models.user import User
    import uuid

    # Create admin user
    admin = User(
        id=uuid.uuid4(),
        username="admin",
        email="admin@example.com",
        password=get_password_hash("adminpassword"),
        first_name="Admin",
        last_name="User",
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()

    # Create access token
    access_token = create_access_token(data={"sub": str(admin.id)})
    return access_token
