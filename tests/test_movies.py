import pytest
from fastapi import status
import uuid

from app.core.security import create_access_token
from app.models.user import User
from app.database.database import get_db

def test_get_movies(client, test_data):
    """Test getting a list of movies."""
    # Make request to get movies
    response = client.get("/api/v1/movies/")

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check that the test movie is in the response
    movie_ids = [movie["id"] for movie in data]
    assert str(test_data["movie"].id) in movie_ids

def test_get_movies_with_filters(client, test_data):
    """Test getting a list of movies with filters."""
    movie = test_data["movie"]

    # Test filtering by title
    response = client.get(f"/api/v1/movies/?title={movie.title}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == movie.title

    # Test filtering by genre
    response = client.get(f"/api/v1/movies/?genre={movie.genre[0]}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert movie.genre[0] in data[0]["genre"]

    # Test filtering by director
    response = client.get(f"/api/v1/movies/?director={movie.director}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["director"] == movie.director

    # Test filtering by year
    response = client.get(f"/api/v1/movies/?year={movie.release_year}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["release_year"] == movie.release_year

def test_get_movie_by_id(client, test_data):
    """Test getting a movie by ID."""
    movie_id = str(test_data["movie"].id)

    # Make request to get movie
    response = client.get(f"/api/v1/movies/{movie_id}")

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert data["id"] == movie_id
    assert data["title"] == test_data["movie"].title
    assert data["release_year"] == test_data["movie"].release_year
    assert data["director"] == test_data["movie"].director

def test_get_movie_not_found(client):
    """Test getting a non-existent movie."""
    # Make request with a non-existent movie ID
    response = client.get(f"/api/v1/movies/{uuid.uuid4()}")

    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check error message
    assert response.json()["detail"] == "Movie not found"

@pytest.fixture
def admin_token(db_session):
    """Create an admin user and return a token for that user."""
    from app.core.security import get_password_hash

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

def test_create_movie(client, admin_token):
    """Test creating a new movie."""
    # Create movie data
    movie_data = {
        "title": "New Test Movie",
        "release_year": 2023,
        "director": "Test Director",
        "cast": ["Actor 1", "Actor 2"],
        "genre": ["Action", "Drama"],
        "plot": "Test plot description",
        "duration": 120,
        "poster_url": "http://example.com/poster.jpg",
        "images": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    }

    # Make request to create movie
    response = client.post(
        "/api/v1/movies/",
        json=movie_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert data["title"] == movie_data["title"]
    assert data["release_year"] == movie_data["release_year"]
    assert data["director"] == movie_data["director"]
    assert data["cast"] == movie_data["cast"]
    assert data["genre"] == movie_data["genre"]
    assert data["plot"] == movie_data["plot"]
    assert data["duration"] == movie_data["duration"]
    assert data["poster_url"] == movie_data["poster_url"]
    assert data["images"] == movie_data["images"]
    assert "id" in data

def test_create_movie_unauthorized(client):
    """Test creating a movie without authentication."""
    # Create movie data
    movie_data = {
        "title": "New Test Movie",
        "release_year": 2023,
        "director": "Test Director",
        "cast": ["Actor 1", "Actor 2"],
        "genre": ["Action", "Drama"],
        "plot": "Test plot description",
        "duration": 120,
        "poster_url": "http://example.com/poster.jpg",
        "images": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    }

    # Make request to create movie without authentication
    response = client.post("/api/v1/movies/", json=movie_data)

    # Check response status code
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_movie_forbidden(client, test_data):
    """Test creating a movie with a non-admin user."""
    # Create a token for a non-admin user
    user = test_data["users"][0]
    access_token = create_access_token(data={"sub": str(user.id)})

    # Create movie data
    movie_data = {
        "title": "New Test Movie",
        "release_year": 2023,
        "director": "Test Director",
        "cast": ["Actor 1", "Actor 2"],
        "genre": ["Action", "Drama"],
        "plot": "Test plot description",
        "duration": 120,
        "poster_url": "http://example.com/poster.jpg",
        "images": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    }

    # Make request to create movie with non-admin user
    response = client.post(
        "/api/v1/movies/",
        json=movie_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Check error message
    assert response.json()["detail"] == "Not enough permissions"

def test_update_movie(client, test_data, admin_token):
    """Test updating a movie."""
    movie_id = str(test_data["movie"].id)

    # Create update data
    update_data = {
        "title": "Updated Test Movie",
        "release_year": 2024,
        "director": "Updated Director"
    }

    # Make request to update movie
    response = client.put(
        f"/api/v1/movies/{movie_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert data["id"] == movie_id
    assert data["title"] == update_data["title"]
    assert data["release_year"] == update_data["release_year"]
    assert data["director"] == update_data["director"]

def test_update_movie_not_found(client, admin_token):
    """Test updating a non-existent movie."""
    # Create update data
    update_data = {
        "title": "Updated Test Movie",
        "release_year": 2024,
        "director": "Updated Director"
    }

    # Make request with a non-existent movie ID
    response = client.put(
        f"/api/v1/movies/{uuid.uuid4()}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check error message
    assert response.json()["detail"] == "Movie not found"

def test_delete_movie(client, test_data, admin_token):
    """Test deleting a movie."""
    # Create a new movie to delete
    from app.models.movie import Movie

    new_movie = Movie(
        id=uuid.uuid4(),
        title="Movie to Delete",
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
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.add(new_movie)
    db.commit()

    movie_id = str(new_movie.id)

    # Make request to delete movie
    response = client.delete(
        f"/api/v1/movies/{movie_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify movie is deleted
    get_response = client.get(f"/api/v1/movies/{movie_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_movie_not_found(client, admin_token):
    """Test deleting a non-existent movie."""
    # Make request with a non-existent movie ID
    response = client.delete(
        f"/api/v1/movies/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check error message
    assert response.json()["detail"] == "Movie not found"
