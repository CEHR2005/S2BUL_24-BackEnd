import pytest
from fastapi.testclient import TestClient
from main import app

def test_read_root(client):
    """Test the root endpoint returns the expected message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Movie Rating API"}

def test_api_v1_endpoints_exist():
    """Test that all API v1 endpoints are registered."""
    client = TestClient(app)
    openapi_schema = app.openapi()
    
    # Check that all expected API routes are in the OpenAPI schema
    paths = openapi_schema["paths"]
    
    # Check for auth endpoints
    assert "/api/v1/auth/login" in paths
    
    # Check for users endpoints
    assert any(path.startswith("/api/v1/users") for path in paths)
    
    # Check for movies endpoints
    assert any(path.startswith("/api/v1/movies") for path in paths)
    
    # Check for comments endpoints
    assert any(path.startswith("/api/v1/comments") for path in paths)
    
    # Check for ratings endpoints
    assert any(path.startswith("/api/v1/ratings") for path in paths)
    
    # Check for statistics endpoints
    assert any(path.startswith("/api/v1/statistics") for path in paths)