# Movie Rating API

A comprehensive API for managing movies, ratings, and user interactions. This backend application allows users to browse movies, rate them, and comment on them, with detailed statistics based on user demographics.

## Project Overview

The Movie Rating API is built with FastAPI and SQLAlchemy, providing a robust and scalable backend for a movie rating platform. The application includes the following features:

- User authentication and registration
- Movie management (CRUD operations)
- Rating system
- Commenting system
- Detailed statistics based on user demographics

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library
- **Pydantic**: Data validation and settings management
- **PostgreSQL**: Database for production
- **SQLite**: Database for testing
- **JWT**: JSON Web Tokens for authentication
- **Pytest**: Testing framework

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (for production)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/movie-rating-api.git
   cd movie-rating-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   SECRET_KEY=your-secret-key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   CORS_ORIGINS=http://localhost:3000,http://localhost:8080
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the application is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

#### Authentication

- `POST /api/v1/auth/register`: Register a new user
- `POST /api/v1/auth/login`: Login and get access token

#### Users

- `GET /api/v1/users/me`: Get current user information
- `PUT /api/v1/users/me`: Update current user information
- `GET /api/v1/users/{user_id}`: Get user by ID

#### Movies

- `GET /api/v1/movies/`: Get list of movies (with optional filtering)
- `POST /api/v1/movies/`: Create a new movie (admin only)
- `GET /api/v1/movies/{movie_id}`: Get movie by ID
- `PUT /api/v1/movies/{movie_id}`: Update a movie (admin only)
- `DELETE /api/v1/movies/{movie_id}`: Delete a movie (admin only)

#### Comments

- `GET /api/v1/comments/movie/{movie_id}`: Get all comments for a movie
- `POST /api/v1/comments/`: Create a new comment
- `PUT /api/v1/comments/{comment_id}`: Update a comment (author or admin only)
- `DELETE /api/v1/comments/{comment_id}`: Delete a comment (author or admin only)

#### Ratings

- `GET /api/v1/ratings/movie/{movie_id}`: Get all ratings for a movie
- `GET /api/v1/ratings/movie/{movie_id}/stats`: Get rating statistics for a movie
- `POST /api/v1/ratings/`: Create or update a rating
- `DELETE /api/v1/ratings/{rating_id}`: Delete a rating (author or admin only)

#### Statistics

- `GET /api/v1/statistics/movie/{movie_id}`: Get detailed statistics for a movie

## Testing

The project includes comprehensive unit tests for all endpoints and components. To run the tests:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=app

# Run specific test file
pytest tests/test_users.py

# Run specific test function
pytest tests/test_users.py::test_get_current_user
```

### Test Structure

The tests are organized into several files:

- **test_main.py**: Tests for the main application setup
- **test_auth.py**: Tests for authentication endpoints (login, registration)
- **test_users.py**: Tests for user-related endpoints
- **test_movies.py**: Tests for movie-related endpoints
- **test_comments.py**: Tests for comment-related endpoints
- **test_ratings.py**: Tests for rating-related endpoints
- **test_statistics.py**: Tests for statistics-related endpoints
- **test_statistics_edge_cases.py**: Tests for edge cases in statistics calculations
- **test_cors.py**: Tests for CORS configuration
- **test_database.py**: Tests for database connection and error handling

### Test Coverage

The tests cover:
- Authentication and user management
- Movie CRUD operations
- Comment creation, retrieval, updating, and deletion
- Rating creation, retrieval, updating, and deletion
- Statistics calculation and edge cases
- Authorization and permission checks
- CORS configuration
- Database connection and error handling

### Test Fixtures

The tests use fixtures defined in `conftest.py` to set up the test environment:

- **test_engine**: Creates a test database engine using in-memory SQLite
- **db_session**: Creates a fresh database session for each test
- **client**: Creates a test client with a test database session
- **test_data**: Creates test data (users, movies, ratings) for the database
- **user_token**: Creates a token for a regular user
- **admin_token**: Creates a token for an admin user

### Writing New Tests

When writing new tests, follow these guidelines:

1. Create a new test file or add to an existing one based on the component being tested
2. Use the fixtures from `conftest.py` to set up the test environment
3. Write clear test functions with descriptive names and docstrings
4. Test both successful operations and error cases
5. Test edge cases and boundary conditions
6. Use assertions to verify the expected behavior

## Deployment

### Docker Deployment

The project includes a Dockerfile for easy deployment:

1. Build the Docker image:
   ```bash
   docker build -t movie-rating-api .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 --name movie-rating-api movie-rating-api
   ```

### Production Considerations

For production deployment, consider:
- Using a production-grade ASGI server like Uvicorn behind Nginx
- Setting up proper database backups
- Implementing rate limiting
- Using HTTPS with proper SSL certificates
- Setting up monitoring and logging

## Project Structure

```
movie-rating-api/
├── app/
│   ├── core/
│   │   ├── config.py         # Application configuration
│   │   └── security.py       # Security utilities (JWT, password hashing)
│   ├── database/
│   │   └── database.py       # Database connection and session management
│   ├── models/
│   │   ├── comment.py        # Comment model
│   │   ├── movie.py          # Movie model
│   │   ├── rating.py         # Rating model
│   │   └── user.py           # User model
│   ├── routes/
│   │   ├── auth.py           # Authentication routes
│   │   ├── comments.py       # Comment routes
│   │   ├── movies.py         # Movie routes
│   │   ├── ratings.py        # Rating routes
│   │   ├── statistics.py     # Statistics routes
│   │   └── users.py          # User routes
│   └── schemas/
│       ├── comment.py        # Comment schemas
│       ├── movie.py          # Movie schemas
│       ├── rating.py         # Rating schemas
│       ├── statistics.py     # Statistics schemas
│       └── user.py           # User schemas
├── tests/
│   ├── conftest.py                  # Test configuration and fixtures
│   ├── test_auth.py                 # Authentication tests
│   ├── test_comments.py             # Comment tests
│   ├── test_cors.py                 # CORS configuration tests
│   ├── test_database.py             # Database connection and error handling tests
│   ├── test_main.py                 # Main application tests
│   ├── test_movies.py               # Movie tests
│   ├── test_ratings.py              # Rating tests
│   ├── test_statistics.py           # Statistics tests
│   ├── test_statistics_edge_cases.py # Statistics edge cases tests
│   └── test_users.py                # User tests
├── Dockerfile                # Docker configuration
├── main.py                   # Application entry point
└── requirements.txt          # Project dependencies
```

Advanced Programming_S2BUL_24. st2218026. Arsentii Bieliaiev