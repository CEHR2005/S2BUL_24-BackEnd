from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, case, and_, or_
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user import User
from app.schemas.statistics import MovieStatistics, AgeStatistics, GenderStatistics, ContinentStatistics, CountryStatistics

router = APIRouter()

@router.get("/movie/{movie_id}", response_model=MovieStatistics)
def get_movie_statistics(
    movie_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    Fetches statistical data related to a specific movie, such as its rating statistics, demographic user data, and global
    distribution of user ratings. The function retrieves statistics such as average rating, number of ratings,
    distribution of user ages, genders, continents, and countries. The data is retrieved from the database
    and formatted into a comprehensive response.

    Parameters:
        movie_id (str): The unique identifier of the movie for which statistics are being retrieved.
        db (Session): The database session used to query data. This is provided via dependency injection.

    Returns:
        Any: A dictionary containing detailed statistical data associated with the specified movie, including:
            - Average rating and total number of ratings.
            - Age group statistics.
            - Gender-based statistics.
            - Continent-based user statistics.
            - Country-based user statistics.

    Raises:
        HTTPException: If the specified movie does not exist in the database (HTTP status code 404).
    """
    # Check if movie exists
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    # Get basic rating statistics
    basic_stats = (
        db.query(
            func.avg(Rating.score).label("average_rating"),
            func.count(Rating.id).label("total_ratings")
        )
        .filter(Rating.movie_id == movie_id)
        .first()
    )

    # Get age statistics
    age_stats = (
        db.query(
            func.sum(case((User.age < 18, 1), else_=0)).label("under18"),
            func.sum(case((and_(User.age >= 18, User.age <= 24), 1), else_=0)).label("age18to24"),
            func.sum(case((and_(User.age >= 25, User.age <= 34), 1), else_=0)).label("age25to34"),
            func.sum(case((and_(User.age >= 35, User.age <= 44), 1), else_=0)).label("age35to44"),
            func.sum(case((and_(User.age >= 45, User.age <= 54), 1), else_=0)).label("age45to54"),
            func.sum(case((User.age >= 55, 1), else_=0)).label("age55plus")
        )
        .join(Rating, Rating.user_id == User.id)
        .filter(Rating.movie_id == movie_id)
        .first()
    )

    # Get gender statistics
    gender_stats = (
        db.query(
            func.sum(case((User.gender == "male", 1), else_=0)).label("male"),
            func.sum(case((User.gender == "female", 1), else_=0)).label("female"),
            func.sum(case((User.gender == "other", 1), else_=0)).label("other"),
            func.sum(case((or_(
                and_(User.gender != "male", User.gender != "female", User.gender != "other"),
                User.gender == None
            ), 1), else_=0)).label("not_specified")
        )
        .join(Rating, Rating.user_id == User.id)
        .filter(Rating.movie_id == movie_id)
        .first()
    )

    # Get continent statistics
    continent_stats = (
        db.query(
            func.sum(case((User.continent == "africa", 1), else_=0)).label("africa"),
            func.sum(case((User.continent == "asia", 1), else_=0)).label("asia"),
            func.sum(case((User.continent == "europe", 1), else_=0)).label("europe"),
            func.sum(case((User.continent == "north_america", 1), else_=0)).label("north_america"),
            func.sum(case((User.continent == "south_america", 1), else_=0)).label("south_america"),
            func.sum(case((User.continent == "australia", 1), else_=0)).label("australia"),
            func.sum(case((User.continent == "antarctica", 1), else_=0)).label("antarctica")
        )
        .join(Rating, Rating.user_id == User.id)
        .filter(Rating.movie_id == movie_id)
        .first()
    )

    # Get country statistics
    country_stats_query = (
        db.query(
            User.country,
            func.count(Rating.id).label("count")
        )
        .join(Rating, Rating.user_id == User.id)
        .filter(Rating.movie_id == movie_id)
        .filter(User.country != None)
        .group_by(User.country)
        .all()
    )

    country_stats = {}
    for country, count in country_stats_query:
        if country:
            country_stats[country] = count

    # Prepare the response
    return {
        "movie_id": movie_id,
        "average_rating": float(basic_stats.average_rating or 0),
        "total_ratings": basic_stats.total_ratings or 0,
        "age_statistics": {
            "under18": age_stats.under18 or 0,
            "age18to24": age_stats.age18to24 or 0,
            "age25to34": age_stats.age25to34 or 0,
            "age35to44": age_stats.age35to44 or 0,
            "age45to54": age_stats.age45to54 or 0,
            "age55plus": age_stats.age55plus or 0
        },
        "gender_statistics": {
            "male": gender_stats.male or 0,
            "female": gender_stats.female or 0,
            "other": gender_stats.other or 0,
            "not_specified": gender_stats.not_specified or 0
        },
        "continent_statistics": {
            "africa": continent_stats.africa or 0,
            "asia": continent_stats.asia or 0,
            "europe": continent_stats.europe or 0,
            "north_america": continent_stats.north_america or 0,
            "south_america": continent_stats.south_america or 0,
            "australia": continent_stats.australia or 0,
            "antarctica": continent_stats.antarctica or 0
        },
        "country_statistics": country_stats
    }
