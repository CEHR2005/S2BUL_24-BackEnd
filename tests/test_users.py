import pytest
from fastapi import status
import uuid

from app.core.security import create_access_token
from app.models.user import User
from app.database.database import get_db

@pytest.fixture
def user_token(test_data):
    """Create a token for a regular user."""
    user = test_data["users"][0]
    access_token = create_access_token(data={"sub": str(user.id)})
    return access_token, user

def test_get_current_user(client, user_token):
    """Test getting the current user's information."""
    token, user = user_token
    
    # Make request to get current user
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check response status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check response data structure
    data = response.json()
    assert data["id"] == str(user.id)
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["first_name"] == user.first_name
    assert data["last_name"] == user.last_name
    assert "password" not in data  # Password should not be returned

def test_get_current_user_unauthorized(client):
    """Test getting the current user without authentication."""
    # Make request without authentication
    response = client.get("/api/v1/users/me")
    
    # Check response status code
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_user(client, user_token):
    """Test updating the current user's information."""
    token, user = user_token
    
    # Create update data
    update_data = {
        "first_name": "Updated First",
        "last_name": "Updated Last",
        "age": 35,
        "gender": "other",
        "country": "Updated Country",
        "continent": "Updated Continent"
    }
    
    # Make request to update user
    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check response status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check response data structure
    data = response.json()
    assert data["id"] == str(user.id)
    assert data["username"] == user.username  # Username should not change
    assert data["email"] == user.email  # Email should not change
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]
    assert data["age"] == update_data["age"]
    assert data["gender"] == update_data["gender"]
    assert data["country"] == update_data["country"]
    assert data["continent"] == update_data["continent"]

def test_update_user_username(client, user_token, test_data):
    """Test updating the current user's username."""
    token, user = user_token
    
    # Create update data with a new username
    update_data = {
        "username": "new_username"
    }
    
    # Make request to update user
    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check response status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check response data structure
    data = response.json()
    assert data["id"] == str(user.id)
    assert data["username"] == update_data["username"]

def test_update_user_username_taken(client, user_token, test_data):
    """Test updating the current user's username to one that's already taken."""
    token, user = user_token
    
    # Get another user's username
    other_user = test_data["users"][1]
    
    # Create update data with the other user's username
    update_data = {
        "username": other_user.username
    }
    
    # Make request to update user
    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check response status code
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Check error message
    assert response.json()["detail"] == "Username already taken"

def test_update_user_unauthorized(client):
    """Test updating the current user without authentication."""
    # Create update data
    update_data = {
        "first_name": "Updated First",
        "last_name": "Updated Last"
    }
    
    # Make request without authentication
    response = client.put("/api/v1/users/me", json=update_data)
    
    # Check response status code
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_user_by_id(client, test_data):
    """Test getting a user by ID."""
    user = test_data["users"][0]
    user_id = str(user.id)
    
    # Make request to get user
    response = client.get(f"/api/v1/users/{user_id}")
    
    # Check response status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check response data structure
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["first_name"] == user.first_name
    assert data["last_name"] == user.last_name
    assert "password" not in data  # Password should not be returned

def test_get_user_not_found(client):
    """Test getting a non-existent user."""
    # Make request with a non-existent user ID
    response = client.get(f"/api/v1/users/{uuid.uuid4()}")
    
    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Check error message
    assert response.json()["detail"] == "User not found"