import pytest
from fastapi import status
import uuid

from app.models.user import User
from app.models.movie import Movie
from app.models.rating import Rating
from app.database.database import get_db

def test_statistics_no_ratings(client, db_session):
    """Test getting statistics for a movie with no ratings."""
    # Create a test movie with no ratings
    movie = Movie(
        id=uuid.uuid4(),
        title="Movie with No Ratings",
        release_year=2023,
        director="Test Director",
        cast=["Actor 1", "Actor 2"],
        genre=["Action", "Drama"],
        plot="Test plot description",
        duration=120,
        poster_url="http://example.com/poster.jpg",
        images=["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    )
    
    # Add movie to the database
    db_session.add(movie)
    db_session.commit()
    
    movie_id = str(movie.id)
    
    # Make request to get movie statistics
    response = client.get(f"/api/v1/statistics/movie/{movie_id}")
    
    # Check response status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check response data structure
    data = response.json()
    assert data["movie_id"] == movie_id
    assert data["average_rating"] == 0.0
    assert data["total_ratings"] == 0
    
    # Check that all demographic statistics are zero
    age_stats = data["age_statistics"]
    assert age_stats["under18"] == 0
    assert age_stats["age18to24"] == 0
    assert age_stats["age25to34"] == 0
    assert age_stats["age35to44"] == 0
    assert age_stats["age45to54"] == 0
    assert age_stats["age55plus"] == 0
    
    gender_stats = data["gender_statistics"]
    assert gender_stats["male"] == 0
    assert gender_stats["female"] == 0
    assert gender_stats["other"] == 0
    assert gender_stats["not_specified"] == 0
    
    continent_stats = data["continent_statistics"]
    assert continent_stats["africa"] == 0
    assert continent_stats["asia"] == 0
    assert continent_stats["europe"] == 0
    assert continent_stats["north_america"] == 0
    assert continent_stats["south_america"] == 0
    assert continent_stats["australia"] == 0
    assert continent_stats["antarctica"] == 0
    
    # Check that country statistics is an empty dict
    assert data["country_statistics"] == {}

def test_statistics_no_demographics(client, db_session):
    """Test getting statistics for a movie with ratings from users with no demographic information."""
    # Create a test movie
    movie = Movie(
        id=uuid.uuid4(),
        title="Movie with No Demographics",
        release_year=2023,
        director="Test Director",
        cast=["Actor 1", "Actor 2"],
        genre=["Action", "Drama"],
        plot="Test plot description",
        duration=120,
        poster_url="http://example.com/poster.jpg",
        images=["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    )
    
    # Create users with no demographic information
    users = [
        User(
            id=uuid.uuid4(),
            username=f"nodemo_user{i}",
            email=f"nodemo_user{i}@example.com",
            password="hashed_password",
            first_name=f"First{i}",
            last_name=f"Last{i}",
            age=None,
            gender=None,
            country=None,
            continent=None,
            is_admin=False
        )
        for i in range(3)
    ]
    
    # Add movie and users to the database
    db_session.add(movie)
    for user in users:
        db_session.add(user)
    db_session.commit()
    
    # Create ratings for the movie
    ratings = [
        Rating(
            id=uuid.uuid4(),
            movie_id=movie.id,
            user_id=users[i].id,
            score=score
        )
        for i, score in enumerate([8, 9, 7])
    ]
    
    # Add ratings to the database
    for rating in ratings:
        db_session.add(rating)
    db_session.commit()
    
    movie_id = str(movie.id)
    
    # Make request to get movie statistics
    response = client.get(f"/api/v1/statistics/movie/{movie_id}")
    
    # Check response status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check response data structure
    data = response.json()
    assert data["movie_id"] == movie_id
    assert data["average_rating"] == 8.0  # (8 + 9 + 7) / 3 = 8.0
    assert data["total_ratings"] == 3
    
    # Check that all demographic statistics are zero or reflect "not specified"
    age_stats = data["age_statistics"]
    assert age_stats["under18"] == 0
    assert age_stats["age18to24"] == 0
    assert age_stats["age25to34"] == 0
    assert age_stats["age35to44"] == 0
    assert age_stats["age45to54"] == 0
    assert age_stats["age55plus"] == 0
    
    gender_stats = data["gender_statistics"]
    assert gender_stats["male"] == 0
    assert gender_stats["female"] == 0
    assert gender_stats["other"] == 0
    assert gender_stats["not_specified"] == 3  # All 3 users have no gender specified
    
    continent_stats = data["continent_statistics"]
    assert continent_stats["africa"] == 0
    assert continent_stats["asia"] == 0
    assert continent_stats["europe"] == 0
    assert continent_stats["north_america"] == 0
    assert continent_stats["south_america"] == 0
    assert continent_stats["australia"] == 0
    assert continent_stats["antarctica"] == 0
    
    # Check that country statistics is an empty dict
    assert data["country_statistics"] == {}

def test_statistics_single_rating(client, db_session):
    """Test getting statistics for a movie with only one rating."""
    # Create a test movie
    movie = Movie(
        id=uuid.uuid4(),
        title="Movie with Single Rating",
        release_year=2023,
        director="Test Director",
        cast=["Actor 1", "Actor 2"],
        genre=["Action", "Drama"],
        plot="Test plot description",
        duration=120,
        poster_url="http://example.com/poster.jpg",
        images=["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    )
    
    # Create a user with demographic information
    user = User(
        id=uuid.uuid4(),
        username="single_user",
        email="single_user@example.com",
        password="hashed_password",
        first_name="Single",
        last_name="User",
        age=30,
        gender="male",
        country="TestCountry",
        continent="europe",
        is_admin=False
    )
    
    # Add movie and user to the database
    db_session.add(movie)
    db_session.add(user)
    db_session.commit()
    
    # Create a rating for the movie
    rating = Rating(
        id=uuid.uuid4(),
        movie_id=movie.id,
        user_id=user.id,
        score=10
    )
    
    # Add rating to the database
    db_session.add(rating)
    db_session.commit()
    
    movie_id = str(movie.id)
    
    # Make request to get movie statistics
    response = client.get(f"/api/v1/statistics/movie/{movie_id}")
    
    # Check response status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check response data structure
    data = response.json()
    assert data["movie_id"] == movie_id
    assert data["average_rating"] == 10.0
    assert data["total_ratings"] == 1
    
    # Check that demographic statistics reflect the single user
    age_stats = data["age_statistics"]
    assert age_stats["under18"] == 0
    assert age_stats["age18to24"] == 0
    assert age_stats["age25to34"] == 1  # User is 30
    assert age_stats["age35to44"] == 0
    assert age_stats["age45to54"] == 0
    assert age_stats["age55plus"] == 0
    
    gender_stats = data["gender_statistics"]
    assert gender_stats["male"] == 1  # User is male
    assert gender_stats["female"] == 0
    assert gender_stats["other"] == 0
    assert gender_stats["not_specified"] == 0
    
    continent_stats = data["continent_statistics"]
    assert continent_stats["africa"] == 0
    assert continent_stats["asia"] == 0
    assert continent_stats["europe"] == 1  # User is from Europe
    assert continent_stats["north_america"] == 0
    assert continent_stats["south_america"] == 0
    assert continent_stats["australia"] == 0
    assert continent_stats["antarctica"] == 0
    
    # Check that country statistics reflects the user's country
    assert data["country_statistics"]["TestCountry"] == 1

def test_statistics_mixed_demographics(client, db_session):
    """Test getting statistics for a movie with ratings from users with mixed demographic information."""
    # Create a test movie
    movie = Movie(
        id=uuid.uuid4(),
        title="Movie with Mixed Demographics",
        release_year=2023,
        director="Test Director",
        cast=["Actor 1", "Actor 2"],
        genre=["Action", "Drama"],
        plot="Test plot description",
        duration=120,
        poster_url="http://example.com/poster.jpg",
        images=["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    )
    
    # Create users with mixed demographic information
    users = [
        User(
            id=uuid.uuid4(),
            username=f"mixed_user1",
            email=f"mixed_user1@example.com",
            password="hashed_password",
            first_name="First1",
            last_name="Last1",
            age=25,
            gender="male",
            country="USA",
            continent="north_america",
            is_admin=False
        ),
        User(
            id=uuid.uuid4(),
            username=f"mixed_user2",
            email=f"mixed_user2@example.com",
            password="hashed_password",
            first_name="First2",
            last_name="Last2",
            age=None,  # No age
            gender="female",
            country="UK",
            continent="europe",
            is_admin=False
        ),
        User(
            id=uuid.uuid4(),
            username=f"mixed_user3",
            email=f"mixed_user3@example.com",
            password="hashed_password",
            first_name="First3",
            last_name="Last3",
            age=40,
            gender=None,  # No gender
            country="Japan",
            continent="asia",
            is_admin=False
        ),
        User(
            id=uuid.uuid4(),
            username=f"mixed_user4",
            email=f"mixed_user4@example.com",
            password="hashed_password",
            first_name="First4",
            last_name="Last4",
            age=55,
            gender="other",
            country=None,  # No country
            continent=None,  # No continent
            is_admin=False
        )
    ]
    
    # Add movie and users to the database
    db_session.add(movie)
    for user in users:
        db_session.add(user)
    db_session.commit()
    
    # Create ratings for the movie
    ratings = [
        Rating(
            id=uuid.uuid4(),
            movie_id=movie.id,
            user_id=users[i].id,
            score=score
        )
        for i, score in enumerate([8, 9, 7, 6])
    ]
    
    # Add ratings to the database
    for rating in ratings:
        db_session.add(rating)
    db_session.commit()
    
    movie_id = str(movie.id)
    
    # Make request to get movie statistics
    response = client.get(f"/api/v1/statistics/movie/{movie_id}")
    
    # Check response status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check response data structure
    data = response.json()
    assert data["movie_id"] == movie_id
    assert data["average_rating"] == 7.5  # (8 + 9 + 7 + 6) / 4 = 7.5
    assert data["total_ratings"] == 4
    
    # Check that demographic statistics reflect the mixed demographics
    age_stats = data["age_statistics"]
    assert age_stats["under18"] == 0
    assert age_stats["age18to24"] == 0
    assert age_stats["age25to34"] == 1  # User 1 is 25
    assert age_stats["age35to44"] == 1  # User 3 is 40
    assert age_stats["age45to54"] == 0
    assert age_stats["age55plus"] == 1  # User 4 is 55
    
    gender_stats = data["gender_statistics"]
    assert gender_stats["male"] == 1  # User 1 is male
    assert gender_stats["female"] == 1  # User 2 is female
    assert gender_stats["other"] == 1  # User 4 is other
    assert gender_stats["not_specified"] == 1  # User 3 has no gender specified
    
    continent_stats = data["continent_statistics"]
    assert continent_stats["africa"] == 0
    assert continent_stats["asia"] == 1  # User 3 is from Asia
    assert continent_stats["europe"] == 1  # User 2 is from Europe
    assert continent_stats["north_america"] == 1  # User 1 is from North America
    assert continent_stats["south_america"] == 0
    assert continent_stats["australia"] == 0
    assert continent_stats["antarctica"] == 0
    
    # Check that country statistics reflects the users' countries
    assert data["country_statistics"]["USA"] == 1
    assert data["country_statistics"]["UK"] == 1
    assert data["country_statistics"]["Japan"] == 1