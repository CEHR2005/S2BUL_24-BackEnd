import pytest
from fastapi import status
import uuid

from app.core.security import create_access_token
from app.models.user import User
from app.models.comment import Comment
from app.database.database import get_db

def test_get_comments_by_movie(client, test_data):
    """Test getting comments for a movie."""
    movie_id = str(test_data["movie"].id)

    # Create a test comment
    user = test_data["users"][0]
    comment = Comment(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=user.id,
        text="Test comment"
    )

    # Add comment to the database
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.add(comment)
    db.commit()

    # Make request to get comments
    response = client.get(f"/api/v1/comments/movie/{movie_id}")

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check that the test comment is in the response
    comment_found = False
    for comment_data in data:
        if comment_data["text"] == "Test comment":
            comment_found = True
            assert comment_data["movie_id"] == movie_id
            assert comment_data["user_id"] == str(user.id)
            assert "user" in comment_data
            assert comment_data["user"]["username"] == user.username
            break

    assert comment_found, "Test comment not found in response"

def test_get_comments_movie_not_found(client):
    """Test getting comments for a non-existent movie."""
    # Make request with a non-existent movie ID
    response = client.get(f"/api/v1/comments/movie/{uuid.uuid4()}")

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

def test_create_comment(client, test_data, user_token):
    """Test creating a new comment."""
    token, user = user_token
    movie_id = str(test_data["movie"].id)

    # Create comment data
    comment_data = {
        "movie_id": movie_id,
        "text": "This is a new test comment"
    }

    # Make request to create comment
    response = client.post(
        "/api/v1/comments/",
        json=comment_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert data["movie_id"] == movie_id
    assert data["user_id"] == str(user.id)
    assert data["text"] == comment_data["text"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_comment_movie_not_found(client, user_token):
    """Test creating a comment for a non-existent movie."""
    token, _ = user_token

    # Create comment data with non-existent movie ID
    comment_data = {
        "movie_id": str(uuid.uuid4()),
        "text": "This is a test comment"
    }

    # Make request to create comment
    response = client.post(
        "/api/v1/comments/",
        json=comment_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check error message
    assert response.json()["detail"] == "Movie not found"

def test_create_comment_unauthorized(client, test_data):
    """Test creating a comment without authentication."""
    movie_id = str(test_data["movie"].id)

    # Create comment data
    comment_data = {
        "movie_id": movie_id,
        "text": "This is a test comment"
    }

    # Make request to create comment without authentication
    response = client.post("/api/v1/comments/", json=comment_data)

    # Check response status code
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_comment(client, test_data, user_token):
    """Test updating a comment."""
    token, user = user_token

    # Create a test comment
    comment = Comment(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=user.id,
        text="Original comment"
    )

    # Add comment to the database
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.add(comment)
    db.commit()

    comment_id = str(comment.id)

    # Create update data
    update_data = {
        "text": "Updated comment"
    }

    # Make request to update comment
    response = client.put(
        f"/api/v1/comments/{comment_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert data["id"] == comment_id
    assert data["text"] == update_data["text"]
    assert data["movie_id"] == str(test_data["movie"].id)
    assert data["user_id"] == str(user.id)

def test_update_comment_not_found(client, user_token):
    """Test updating a non-existent comment."""
    token, _ = user_token

    # Create update data
    update_data = {
        "text": "Updated comment"
    }

    # Make request with a non-existent comment ID
    response = client.put(
        f"/api/v1/comments/{uuid.uuid4()}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check error message
    assert response.json()["detail"] == "Comment not found"

def test_update_comment_forbidden(client, test_data, user_token):
    """Test updating a comment by a user who is not the author."""
    token, _ = user_token

    # Create a test comment with a different user
    other_user = test_data["users"][1]  # Use a different user
    comment = Comment(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=other_user.id,
        text="Original comment"
    )

    # Add comment to the database
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.add(comment)
    db.commit()

    comment_id = str(comment.id)

    # Create update data
    update_data = {
        "text": "Updated comment"
    }

    # Make request to update comment
    response = client.put(
        f"/api/v1/comments/{comment_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Check error message
    assert response.json()["detail"] == "Not enough permissions"

def test_delete_comment(client, test_data, user_token):
    """Test deleting a comment."""
    token, user = user_token

    # Create a test comment
    comment = Comment(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=user.id,
        text="Comment to delete"
    )

    # Add comment to the database
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.add(comment)
    db.commit()

    comment_id = str(comment.id)

    # Make request to delete comment
    response = client.delete(
        f"/api/v1/comments/{comment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify comment is deleted
    deleted_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    assert deleted_comment is None

def test_delete_comment_not_found(client, user_token):
    """Test deleting a non-existent comment."""
    token, _ = user_token

    # Make request with a non-existent comment ID
    response = client.delete(
        f"/api/v1/comments/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check error message
    assert response.json()["detail"] == "Comment not found"

def test_delete_comment_forbidden(client, test_data, user_token):
    """Test deleting a comment by a user who is not the author."""
    token, _ = user_token

    # Create a test comment with a different user
    other_user = test_data["users"][1]  # Use a different user
    comment = Comment(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=other_user.id,
        text="Comment to delete"
    )

    # Add comment to the database
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.add(comment)
    db.commit()

    comment_id = str(comment.id)

    # Make request to delete comment
    response = client.delete(
        f"/api/v1/comments/{comment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Check error message
    assert response.json()["detail"] == "Not enough permissions"

def test_admin_can_update_any_comment(client, test_data, admin_token):
    """Test that an admin can update any comment."""
    # Create a test comment with a regular user
    user = test_data["users"][0]
    comment = Comment(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=user.id,
        text="Original comment"
    )

    # Add comment to the database
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.add(comment)
    db.commit()

    comment_id = str(comment.id)

    # Create update data
    update_data = {
        "text": "Admin updated comment"
    }

    # Make request to update comment as admin
    response = client.put(
        f"/api/v1/comments/{comment_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert data["id"] == comment_id
    assert data["text"] == update_data["text"]

def test_admin_can_delete_any_comment(client, test_data, admin_token):
    """Test that an admin can delete any comment."""
    # Create a test comment with a regular user
    user = test_data["users"][0]
    comment = Comment(
        id=uuid.uuid4(),
        movie_id=test_data["movie"].id,
        user_id=user.id,
        text="Comment to delete"
    )

    # Add comment to the database
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.add(comment)
    db.commit()

    comment_id = str(comment.id)

    # Make request to delete comment as admin
    response = client.delete(
        f"/api/v1/comments/{comment_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify comment is deleted
    deleted_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    assert deleted_comment is None
