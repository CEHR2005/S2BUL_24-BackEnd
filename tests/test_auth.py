import pytest
from fastapi import status
from app.core.security import verify_password
from app.database.database import get_db

def test_register_user(client):
    """Test registering a new user."""
    # Create user data
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "gender": "male",
        "country": "TestCountry",
        "continent": "TestContinent"
    }

    # Make request to register user
    response = client.post("/api/v1/auth/register", json=user_data)

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert data["age"] == user_data["age"]
    assert data["gender"] == user_data["gender"]
    assert data["country"] == user_data["country"]
    assert data["continent"] == user_data["continent"]
    assert "id" in data
    assert "password" not in data  # Password should not be returned

def test_register_duplicate_email(client, test_data):
    """Test registering a user with an email that already exists."""
    # Create user data with an email that already exists
    user_data = {
        "username": "newuser",
        "email": test_data["users"][0].email,  # Use existing email
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "gender": "male",
        "country": "TestCountry",
        "continent": "TestContinent"
    }

    # Make request to register user
    response = client.post("/api/v1/auth/register", json=user_data)

    # Check response status code
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Check error message
    assert response.json()["detail"] == "A user with this email already exists"

def test_register_duplicate_username(client, test_data):
    """Test registering a user with a username that already exists."""
    # Create user data with a username that already exists
    user_data = {
        "username": test_data["users"][0].username,  # Use existing username
        "email": "newuser@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "gender": "male",
        "country": "TestCountry",
        "continent": "TestContinent"
    }

    # Make request to register user
    response = client.post("/api/v1/auth/register", json=user_data)

    # Check response status code
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Check error message
    assert response.json()["detail"] == "A user with this username already exists"

def test_login_with_email(client, test_data):
    """Test logging in with email."""
    # Get an existing user
    user = test_data["users"][0]

    # Set the password for the test user (since the test data uses a placeholder)
    from app.core.security import get_password_hash
    from sqlalchemy import update
    from app.models.user import User

    # Update the user's password in the database
    password = "testpassword"
    hashed_password = get_password_hash(password)

    # Update the user's password directly in the database session
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.execute(
        update(User).where(User.id == user.id).values(password=hashed_password)
    )
    db.commit()

    # Make request to login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": password}
    )

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_with_username(client, test_data):
    """Test logging in with username."""
    # Get an existing user
    user = test_data["users"][0]

    # Set the password for the test user (since the test data uses a placeholder)
    from app.core.security import get_password_hash
    from sqlalchemy import update
    from app.models.user import User

    # Update the user's password in the database
    password = "testpassword"
    hashed_password = get_password_hash(password)

    # Update the user's password directly in the database session
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    db.execute(
        update(User).where(User.id == user.id).values(password=hashed_password)
    )
    db.commit()

    # Make request to login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user.username, "password": password}
    )

    # Check response status code
    assert response.status_code == status.HTTP_200_OK

    # Check response data structure
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test logging in with invalid credentials."""
    # Make request to login with invalid credentials
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrongpassword"}
    )

    # Check response status code
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Check error message
    assert response.json()["detail"] == "Incorrect email/username or password"
