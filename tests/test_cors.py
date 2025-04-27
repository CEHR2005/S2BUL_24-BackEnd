import pytest
from fastapi.testclient import TestClient
from app.core.config import settings
from main import app

def test_cors_allowed_origin():
    """Test that CORS allows requests from allowed origins."""
    client = TestClient(app)

    # Get the first allowed origin from settings
    allowed_origin = settings.CORS_ORIGINS_LIST[0]

    # Make a request with the allowed origin
    response = client.options(
        "/api/v1/movies/",
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )

    # Check that the response includes the CORS headers
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == allowed_origin
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "Content-Type" in response.headers["access-control-allow-headers"]

def test_cors_disallowed_origin():
    """Test that CORS blocks requests from disallowed origins."""
    client = TestClient(app)

    # Use a disallowed origin
    disallowed_origin = "http://evil-site.com"

    # Make sure it's not in the allowed origins
    assert disallowed_origin not in settings.CORS_ORIGINS_LIST

    # Make a request with the disallowed origin
    response = client.options(
        "/api/v1/movies/",
        headers={
            "Origin": disallowed_origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )

    # Check that the response is rejected with a 400 status code
    assert response.status_code == 400
    # The disallowed origin should not be in the response headers
    assert response.headers.get("access-control-allow-origin") != disallowed_origin

def test_cors_allowed_methods():
    """Test that CORS allows all HTTP methods."""
    client = TestClient(app)

    # Get the first allowed origin from settings
    allowed_origin = settings.CORS_ORIGINS_LIST[0]

    # Test each HTTP method
    for method in ["GET", "POST", "PUT", "DELETE", "OPTIONS"]:
        response = client.options(
            "/api/v1/movies/",
            headers={
                "Origin": allowed_origin,
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "Content-Type",
            }
        )

        # Check that the response includes the method in allowed methods
        assert response.status_code == 200
        assert method in response.headers["access-control-allow-methods"]

def test_cors_allowed_headers():
    """Test that CORS allows common headers."""
    client = TestClient(app)

    # Get the first allowed origin from settings
    allowed_origin = settings.CORS_ORIGINS_LIST[0]

    # Test common headers
    for header in ["Content-Type", "Authorization", "X-Requested-With"]:
        response = client.options(
            "/api/v1/movies/",
            headers={
                "Origin": allowed_origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": header,
            }
        )

        # Check that the response includes the header in allowed headers
        assert response.status_code == 200
        assert header in response.headers["access-control-allow-headers"]
