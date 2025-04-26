from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_active_user
from app.database.database import get_db
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user import User
from app.schemas.rating import Rating as RatingSchema, RatingCreate, RatingWithUser, MovieRating

router = APIRouter()

@router.get("/movie/{movie_id}", response_model=List[RatingWithUser])
def get_ratings_by_movie(
    movie_id: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all ratings for a movie.
    """
    # Check if movie exists
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    # Get ratings with user information
    ratings = (
        db.query(Rating)
        .filter(Rating.movie_id == movie_id)
        .options(joinedload(Rating.user))
        .order_by(Rating.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Format the response to match RatingWithUser schema
    result = []
    for rating in ratings:
        rating_dict = {
            "id": str(rating.id),
            "movie_id": str(rating.movie_id),
            "user_id": str(rating.user_id),
            "score": rating.score,
            "created_at": rating.created_at,
            "updated_at": rating.updated_at,
            "user": {
                "id": str(rating.user.id),
                "username": rating.user.username,
                "age": rating.user.age,
                "gender": rating.user.gender,
                "country": rating.user.country,
                "continent": rating.user.continent,
            }
        }
        result.append(rating_dict)

    return result

@router.get("/movie/{movie_id}/stats", response_model=MovieRating)
def get_movie_rating_stats(
    movie_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get rating statistics for a movie.
    """
    # Check if movie exists
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    # Calculate average rating and total ratings
    stats = (
        db.query(
            func.avg(Rating.score).label("average_score"),
            func.count(Rating.id).label("total_ratings")
        )
        .filter(Rating.movie_id == movie_id)
        .first()
    )

    return {
        "movie_id": movie_id,
        "average_score": float(stats.average_score or 0),
        "total_ratings": stats.total_ratings or 0
    }

@router.post("/", response_model=RatingSchema)
def create_or_update_rating(
    *,
    db: Session = Depends(get_db),
    rating_in: RatingCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create or update a rating.
    """
    # Check if movie exists
    movie = db.query(Movie).filter(Movie.id == rating_in.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    # Check if user already rated this movie
    existing_rating = (
        db.query(Rating)
        .filter(
            Rating.movie_id == rating_in.movie_id,
            Rating.user_id == current_user.id
        )
        .first()
    )

    if existing_rating:
        # Update existing rating
        existing_rating.score = rating_in.score
        db.add(existing_rating)
        db.commit()
        db.refresh(existing_rating)

        # Convert UUIDs to strings to match Pydantic model expectations
        existing_rating.id = str(existing_rating.id)
        existing_rating.movie_id = str(existing_rating.movie_id)
        existing_rating.user_id = str(existing_rating.user_id)
        return existing_rating
    else:
        # Create new rating
        rating = Rating(
            movie_id=rating_in.movie_id,
            user_id=current_user.id,
            score=rating_in.score,
        )
        db.add(rating)
        db.commit()
        db.refresh(rating)

        # Convert UUIDs to strings to match Pydantic model expectations
        rating.id = str(rating.id)
        rating.movie_id = str(rating.movie_id)
        rating.user_id = str(rating.user_id)
        return rating

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    *,
    db: Session = Depends(get_db),
    rating_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a rating.
    """
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found",
        )

    # Only the rating author or an admin can delete the rating
    if str(rating.user_id) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    db.delete(rating)
    db.commit()
