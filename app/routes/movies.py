from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.database.database import get_db
from app.models.movie import Movie
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
) -> Any:
    """
    Retrieve movies with optional filtering.
    """
    query = db.query(Movie)

    # Apply filters if provided
    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))
    if genre:
        # For SQLite, we need to filter differently since arrays are stored as JSON strings
        # This approach works for both SQLite and PostgreSQL
        query = query.filter(Movie.genre.cast(String).like(f"%{genre}%"))
    if director:
        query = query.filter(Movie.director.ilike(f"%{director}%"))
    if year:
        query = query.filter(Movie.release_year == year)

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
    Create new movie.
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
    Get movie by ID.
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
    Update a movie.
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
    Delete a movie.
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
