import pytest
from fastapi import status
import uuid

from app.core.security import create_access_token
from app.models.user import User
from app.models.rating import Rating
from app.database.database import get_db

def test_get_ratings_by_movie(client, test_data):
    """Test getting ratings for a movie."""
    movie_id = str(test_data["movie"].id)

    # Make request to get ratings
    response = client.get(f"/api/v1/ratings/movie/{movie_id}")

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check that the test ratings are in the response
    for rating_data in data:
        assert rating_data["movie_id"] == movie_id
        assert "user" in rating_data
        assert "username" in rating_data["user"]
        assert "score" in rating_data
        assert isinstance(rating_data["score"], int)

def test_get_ratings_movie_not_found(client):
    """Test getting ratings for a non-existent movie."""
    # Make request with a non-existent movie ID
    response = client.get(f"/api/v1/ratings/movie/{uuid.uuid4()}")

    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check error message
    assert response.json()["detail"] == "Movie not found"

def test_get_movie_rating_stats(client, test_data):
    """Test getting rating statistics for a movie."""
    movie_id = str(test_data["movie"].id)

    # Make request to get rating stats
    response = client.get(f"/api/v1/ratings/movie/{movie_id}/stats")

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert data["movie_id"] == movie_id
    assert "average_score" in data
    assert isinstance(data["average_score"], float)
    assert "total_ratings" in data
    assert isinstance(data["total_ratings"], int)

    # Check that the stats match the test data
    expected_avg = sum(rating.score for rating in test_data["ratings"]) / len(test_data["ratings"])
    assert abs(data["average_score"] - expected_avg) < 0.01  # Allow for small floating point differences
    assert data["total_ratings"] == len(test_data["ratings"])

def test_get_movie_rating_stats_movie_not_found(client):
    """Test getting rating statistics for a non-existent movie."""
    # Make request with a non-existent movie ID
    response = client.get(f"/api/v1/ratings/movie/{uuid.uuid4()}/stats")

    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check error message
    assert response.json()["detail"] == "Movie not found"

@pytest.fixture
def user_token(test_data):
    """Create a token for a regular user."""
    user = test_data["users"][0]
    access_token = create_access_token(data={"sub": str(user.id)})
    return access_token, user

def test_create_rating(client, test_data, user_token):
    """Test creating a new rating."""
    token, user = user_token
    movie_id = str(test_data["movie"].id)

    # First, delete any existing ratings by this user for this movie
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.query(Rating).filter(
        Rating.movie_id == movie_id,
        Rating.user_id == user.id
    ).delete()
    db.commit()

    # Create rating data
    rating_data = {
        "movie_id": movie_id,
        "score": 8
    }

    # Make request to create rating
    response = client.post(
        "/api/v1/ratings/",
        json=rating_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert data["movie_id"] == movie_id
    assert data["user_id"] == str(user.id)
    assert data["score"] == rating_data["score"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_update_rating(client, test_data, user_token):
    """Test updating an existing rating."""
    token, user = user_token
    movie_id = str(test_data["movie"].id)

    # First, delete any existing ratings by this user for this movie
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.query(Rating).filter(
        Rating.movie_id == test_data["movie"].id,
        Rating.user_id == user.id
    ).delete()
    db.commit()

    # Create a test rating
    rating = Rating(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=user.id,
        score=5
    )

    # Add rating to the database
    db.add(rating)
    db.commit()

    # Create update data
    update_data = {
        "movie_id": movie_id,
        "score": 9
    }

    # Make request to update rating
    response = client.post(
        "/api/v1/ratings/",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert data["movie_id"] == movie_id
    assert data["user_id"] == str(user.id)
    assert data["score"] == update_data["score"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_rating_movie_not_found(client, user_token):
    """Test creating a rating for a non-existent movie."""
    token, _ = user_token

    # Create rating data with non-existent movie ID
    rating_data = {
        "movie_id": str(uuid.uuid4()),
        "score": 8
    }

    # Make request to create rating
    response = client.post(
        "/api/v1/ratings/",
        json=rating_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check error message
    assert response.json()["detail"] == "Movie not found"

def test_create_rating_unauthorized(client, test_data):
    """Test creating a rating without authentication."""
    movie_id = str(test_data["movie"].id)

    # Create rating data
    rating_data = {
        "movie_id": movie_id,
        "score": 8
    }

    # Make request to create rating without authentication
    response = client.post("/api/v1/ratings/", json=rating_data)

    # Check response status code
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_delete_rating(client, test_data, user_token):
    """Test deleting a rating."""
    token, user = user_token

    # First, delete any existing ratings by this user for this movie
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.query(Rating).filter(
        Rating.movie_id == test_data["movie"].id,
        Rating.user_id == user.id
    ).delete()
    db.commit()

    # Create a test rating
    rating = Rating(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=user.id,
        score=7
    )

    # Add rating to the database
    db.add(rating)
    db.commit()

    rating_id = str(rating.id)

    # Make request to delete rating
    response = client.delete(
        f"/api/v1/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify rating is deleted
    deleted_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    assert deleted_rating is None

def test_delete_rating_not_found(client, user_token):
    """Test deleting a non-existent rating."""
    token, _ = user_token

    # Make request with a non-existent rating ID
    response = client.delete(
        f"/api/v1/ratings/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check error message
    assert response.json()["detail"] == "Rating not found"

def test_delete_rating_forbidden(client, test_data, user_token):
    """Test deleting a rating by a user who is not the author."""
    token, _ = user_token

    # Create a test rating with a different user
    other_user = test_data["users"][1]  # Use a different user

    # First, delete any existing ratings by this user for this movie
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.query(Rating).filter(
        Rating.movie_id == test_data["movie"].id,
        Rating.user_id == other_user.id
    ).delete()
    db.commit()

    rating = Rating(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=other_user.id,
        score=6
    )

    # Add rating to the database
    db.add(rating)
    db.commit()

    rating_id = str(rating.id)

    # Make request to delete rating
    response = client.delete(
        f"/api/v1/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Check error message
    assert response.json()["detail"] == "Not enough permissions"

def test_admin_can_delete_any_rating(client, test_data, admin_token):
    """Test that an admin can delete any rating."""
    # Create a test rating with a regular user
    user = test_data["users"][0]

    # First, delete any existing ratings by this user for this movie
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.query(Rating).filter(
        Rating.movie_id == test_data["movie"].id,
        Rating.user_id == user.id
    ).delete()
    db.commit()

    rating = Rating(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=user.id,
        score=9
    )

    # Add rating to the database
    db.add(rating)
    db.commit()

    rating_id = str(rating.id)

    # Make request to delete rating as admin
    response = client.delete(
        f"/api/v1/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify rating is deleted
    deleted_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    assert deleted_rating is None
