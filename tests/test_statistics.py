import pytest
from fastapi import status

def test_get_movie_statistics(client, test_data):
    """Test getting statistics for a movie."""
    movie_id = str(test_data["movie"].id)
    
    # Make request to get movie statistics
    response = client.get(f"/api/v1/statistics/movie/{movie_id}")
    
    # Check response status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check response data structure
    data = response.json()
    assert data["movie_id"] == movie_id
    assert isinstance(data["average_rating"], float)
    assert isinstance(data["total_ratings"], int)
    
    # Check that the average rating is calculated correctly
    expected_avg = sum(rating.score for rating in test_data["ratings"]) / len(test_data["ratings"])
    assert abs(data["average_rating"] - expected_avg) < 0.01  # Allow for small floating point differences
    
    # Check that the total ratings count is correct
    assert data["total_ratings"] == len(test_data["ratings"])
    
    # Check age statistics
    age_stats = data["age_statistics"]
    assert age_stats["under18"] == 1  # One user is under 18
    assert age_stats["age18to24"] == 1  # One user is 18-24
    assert age_stats["age25to34"] == 2  # Two users are 25-34
    assert age_stats["age35to44"] == 2  # Two users are 35-44
    assert age_stats["age45to54"] == 2  # Two users are 45-54
    assert age_stats["age55plus"] == 1  # One user is 55+
    
    # Check gender statistics
    gender_stats = data["gender_statistics"]
    assert gender_stats["male"] == 4  # Four male users
    assert gender_stats["female"] == 3  # Three female users
    assert gender_stats["other"] == 1  # One other user
    assert gender_stats["not_specified"] == 1  # One user with unspecified gender
    
    # Check continent statistics
    continent_stats = data["continent_statistics"]
    assert continent_stats["north_america"] == 2  # Two users from North America
    assert continent_stats["europe"] == 2  # Two users from Europe
    assert continent_stats["asia"] == 1  # One user from Asia
    assert continent_stats["australia"] == 1  # One user from Australia
    assert continent_stats["south_america"] == 1  # One user from South America
    assert continent_stats["africa"] == 1  # One user from Africa
    assert continent_stats["antarctica"] == 0  # No users from Antarctica
    
    # Check country statistics
    country_stats = data["country_statistics"]
    assert country_stats["USA"] == 1  # One user from USA
    assert country_stats["Canada"] == 1  # One user from Canada
    assert country_stats["UK"] == 1  # One user from UK
    assert country_stats["Germany"] == 1  # One user from Germany
    assert country_stats["Japan"] == 1  # One user from Japan
    assert country_stats["Australia"] == 1  # One user from Australia
    assert country_stats["Brazil"] == 1  # One user from Brazil
    assert country_stats["South Africa"] == 1  # One user from South Africa

def test_get_movie_statistics_not_found(client):
    """Test getting statistics for a non-existent movie."""
    # Make request with a non-existent movie ID
    response = client.get(f"/api/v1/statistics/movie/00000000-0000-0000-0000-000000000000")
    
    # Check response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Check error message
    assert response.json()["detail"] == "Movie not found"