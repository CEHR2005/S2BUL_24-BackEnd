import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from unittest.mock import patch, MagicMock

from app.database.database import get_db, Base, engine
from app.models.user import User
from app.models.movie import Movie

def test_database_connection(db_session):
    """Test that the database connection is working."""
    # Try to execute a simple query
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1

def test_database_models(db_session):
    """Test that the database models are correctly defined and can be used."""
    # Create a test user
    user = User(
        id="00000000-0000-0000-0000-000000000001",
        username="testuser",
        email="testuser@example.com",
        password="hashed_password",
        first_name="Test",
        last_name="User",
        age=30,
        gender="male",
        country="TestCountry",
        continent="TestContinent",
        is_admin=False
    )

    # Create a test movie
    movie = Movie(
        id="00000000-0000-0000-0000-000000000002",
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

    # Add user and movie to the database
    db_session.add(user)
    db_session.add(movie)
    db_session.commit()

    # Query the user and movie
    queried_user = db_session.query(User).filter(User.id == "00000000-0000-0000-0000-000000000001").first()
    queried_movie = db_session.query(Movie).filter(Movie.id == "00000000-0000-0000-0000-000000000002").first()

    # Check that the queried objects match the created objects
    assert queried_user.username == user.username
    assert queried_user.email == user.email
    assert queried_movie.title == movie.title
    assert queried_movie.release_year == movie.release_year

def test_get_db():
    """Test that the get_db dependency yields a database session."""
    # Get a database session
    db_generator = get_db()
    db = next(db_generator)

    try:
        # Try to execute a simple query
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        # Close the session
        try:
            next(db_generator)
        except StopIteration:
            pass

@pytest.mark.parametrize("exception", [
    SQLAlchemyError("Database error"),
    Exception("General error")
])
def test_get_db_error_handling(exception):
    """Test that the get_db dependency handles errors correctly."""
    # Mock the sessionmaker to raise an exception
    with patch("app.database.database.SessionLocal", side_effect=exception):
        # Get a database session
        db_generator = get_db()

        # Check that an exception is raised
        with pytest.raises(Exception) as excinfo:
            next(db_generator)

        # Check that the exception is the one we raised
        assert str(excinfo.value) == str(exception)

def test_database_custom_types(db_session):
    """Test that custom database types (like arrays) work correctly."""
    # Create a test movie with array fields
    movie = Movie(
        id="00000000-0000-0000-0000-000000000003",
        title="Test Movie with Arrays",
        release_year=2023,
        director="Test Director",
        cast=["Actor 1", "Actor 2", "Actor 3"],  # Array field
        genre=["Action", "Drama", "Sci-Fi"],  # Array field
        plot="Test plot description",
        duration=120,
        poster_url="http://example.com/poster.jpg",
        images=["http://example.com/image1.jpg", "http://example.com/image2.jpg"]  # Array field
    )

    # Add movie to the database
    db_session.add(movie)
    db_session.commit()

    # Query the movie
    queried_movie = db_session.query(Movie).filter(Movie.id == "00000000-0000-0000-0000-000000000003").first()

    # Check that the array fields are correctly stored and retrieved
    assert len(queried_movie.cast) == 3
    assert "Actor 1" in queried_movie.cast
    assert "Actor 2" in queried_movie.cast
    assert "Actor 3" in queried_movie.cast

    assert len(queried_movie.genre) == 3
    assert "Action" in queried_movie.genre
    assert "Drama" in queried_movie.genre
    assert "Sci-Fi" in queried_movie.genre

    assert len(queried_movie.images) == 2
    assert "http://example.com/image1.jpg" in queried_movie.images
    assert "http://example.com/image2.jpg" in queried_movie.images
