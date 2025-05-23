from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, or_, func, and_
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.database.database import get_db
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user import User
from app.schemas.movie import Movie as MovieSchema, MovieCreate, MovieUpdate

router = APIRouter()

@router.get("/", response_model=List[MovieSchema])
def get_movies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    genre: Optional[str] = None,
    director: Optional[str] = None,
    year: Optional[int] = None,
    rating: Optional[float] = None,
) -> Any:
    """
    Retrieves a list of movies from the database with optional filtering and pagination.

    Filters can be applied based on movie title, genre, director, year of release, and minimum rating.
    Provides support for query pagination through the 'skip' and 'limit' parameters.

    Args:
        db (Session): The database session dependency.
        skip (int): The number of records to skip for pagination. Defaults to 0.
        limit (int): The maximum number of records to return. Defaults to 100.
        title (Optional[str]): The full or partial title of the movie to filter by. Defaults to None.
        genre (Optional[str]): The genre of the movie to filter by. Defaults to None.
        director (Optional[str]): The name of the movie's director to filter by. Defaults to None.
        year (Optional[int]): The release year of the movie to filter by. Defaults to None.
        rating (Optional[float]): The minimum average rating of the movie to filter by. Defaults to None.

    Returns:
        Any: A list of movies matching the applied filters and pagination criteria, with UUIDs
        converted to strings for compatibility with the response model.
    """
    query = db.query(Movie)

    # Apply filters if provided
    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))
    if genre:
        # For SQLite, we need to filter differently since arrays are stored as JSON strings
        # This approach works for both SQLite and PostgreSQL
        query = query.filter(Movie.genre.cast(String).ilike(f"%{genre}%"))
    if director:
        query = query.filter(Movie.director.ilike(f"%{director}%"))
    if year:
        query = query.filter(Movie.release_year == year)

    # Apply rating filter if provided
    if rating is not None:
        # Create a subquery to calculate average ratings for each movie
        rating_subquery = (
            db.query(
                Rating.movie_id,
                func.avg(Rating.score).label("avg_rating")
            )
            .group_by(Rating.movie_id)
            .subquery()
        )

        # Left outer join with the rating subquery and filter by minimum rating
        # This ensures movies without ratings are still included when appropriate
        query = query.outerjoin(
            rating_subquery,
            Movie.id == rating_subquery.c.movie_id
        ).filter(
            # Include movies with ratings >= specified value OR movies with no ratings (when rating = 0)
            or_(
                rating_subquery.c.avg_rating >= rating,
                # If rating is 0, include movies with no ratings (NULL avg_rating)
                and_(rating == 0, rating_subquery.c.avg_rating.is_(None))
            )
        )

    # Apply pagination
    movies = query.offset(skip).limit(limit).all()

    # Convert UUIDs to strings to match Pydantic model expectations
    for movie in movies:
        movie.id = str(movie.id)

    return movies

@router.post("/", response_model=MovieSchema)
def create_movie(
    *,
    db: Session = Depends(get_db),
    movie_in: MovieCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Handles the creation of a new movie entity through a POST request.

    Only users with admin privileges are authorized to use this endpoint.
    Upon successful creation, the movie is stored in the database, and its
    details are returned as a response.

    Arguments:
        db: Database session dependency used for interacting with the
            database.
        movie_in: Data required to create a new movie, provided in the
            request body and validated against the `MovieCreate` schema.
        current_user: The currently authenticated user, verified to ensure
            they possess admin privileges.

    Returns:
        A dictionary object of the created movie, including its ID and other
        attributes, as derived from the response model `MovieSchema`.
    """
    # Only admin users can create movies
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    movie = Movie(
        title=movie_in.title,
        release_year=movie_in.release_year,
        director=movie_in.director,
        cast=movie_in.cast,
        genre=movie_in.genre,
        plot=movie_in.plot,
        duration=movie_in.duration,
        poster_url=movie_in.poster_url,
        images=movie_in.images,
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)

    # Convert UUID to string to match Pydantic model expectations
    movie.id = str(movie.id)
    return movie

@router.get("/{movie_id}", response_model=MovieSchema)
def get_movie(
    *,
    db: Session = Depends(get_db),
    movie_id: str,
) -> Any:
    """
    Retrieves a movie by its unique identifier (UUID). This function queries the database
    for a movie matching the provided UUID. If a movie is found, it is returned with its
    UUID converted to a string to conform to the expected Pydantic model format.
    If the movie does not exist or the provided UUID format is invalid, an HTTPException
    is raised.

    Parameters:
        db: Session
            The database session dependency used for querying the database.
        movie_id: str
            The unique identifier (UUID in string format) of the movie to retrieve.

    Returns:
        MovieSchema
            The movie data matching the given movie ID.

    Raises:
        HTTPException
            If the movie ID is invalid or the requested movie is not found in the database.
    """
    try:
        # Convert string to UUID object before querying
        uuid_obj = uuid.UUID(movie_id)
        movie = db.query(Movie).filter(Movie.id == uuid_obj).first()
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found",
            )

        # Convert UUID to string to match Pydantic model expectations
        movie.id = str(movie.id)
        return movie
    except ValueError:
        # Handle invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid movie ID format",
        )

@router.put("/{movie_id}", response_model=MovieSchema)
def update_movie(
    *,
    db: Session = Depends(get_db),
    movie_id: str,
    movie_in: MovieUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Updates an existing movie in the database based on its ID. This endpoint is restricted to admin users only. It allows an administrator to change various fields of a movie by providing the updated data. If the movie does not exist or the provided ID format is invalid, appropriate HTTP errors are raised.

    Parameters:
        db (Session): The SQLAlchemy database session dependency, used to query and update the database.
        movie_id (str): The unique identifier of the movie to be updated, provided as a string. It should match the UUID format.
        movie_in (MovieUpdate): An object containing the updated movie data. Only the fields that are provided will be updated.
        current_user (User): The currently authenticated user, obtained through the dependency mechanism. Used to check if the user has admin privileges.

    Returns:
        Any: The updated movie object as defined by the MovieSchema, converted to match Pydantic model expectations.
    """
    # Only admin users can update movies
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    try:
        # Convert string to UUID object before querying
        uuid_obj = uuid.UUID(movie_id)
        movie = db.query(Movie).filter(Movie.id == uuid_obj).first()
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found",
            )

        # Update movie attributes
        for field, value in movie_in.model_dump(exclude_unset=True).items():
            setattr(movie, field, value)

        db.add(movie)
        db.commit()
        db.refresh(movie)

        # Convert UUID to string to match Pydantic model expectations
        movie.id = str(movie.id)
        return movie
    except ValueError:
        # Handle invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid movie ID format",
        )

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    *,
    db: Session = Depends(get_db),
    movie_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Deletes a specific movie from the database. This operation is restricted to
    admin users only. It requires a valid movie ID, the database session, and the
    authenticated user information. If the ID is invalid, not found, or if the
    user lacks the necessary permissions, appropriate HTTP exceptions with status
    codes are raised.

    Args:
        db (Session): The database session dependency for database operations.
        movie_id (str): The unique identifier of the movie to delete in UUID format.
        current_user (User): The currently authenticated user invoking the operation.

    Raises:
        HTTPException: A 403 Forbidden error if the user is not an admin.
        HTTPException: A 404 Not Found error if the movie does not exist.
        HTTPException: A 400 Bad Request error if the movie ID format is invalid.
    """
    # Only admin users can delete movies
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    try:
        # Convert string to UUID object before querying
        uuid_obj = uuid.UUID(movie_id)
        movie = db.query(Movie).filter(Movie.id == uuid_obj).first()
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found",
            )

        db.delete(movie)
        db.commit()
    except ValueError:
        # Handle invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid movie ID format",
        )
