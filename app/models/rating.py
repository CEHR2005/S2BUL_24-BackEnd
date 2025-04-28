import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.database.custom_types import GUID

class Rating(Base):
    """
    Represents a movie rating entity in the database.

    This class is used to store and manage information about ratings that
    users have assigned to movies. Each rating belongs to a user and a movie
    and records the score given to the movie. The score is represented as an
    integer on a scale from 1 to 10. A unique constraint ensures that a user
    can only rate a movie once.

    Attributes:
        id: The unique identifier of the rating.
        movie_id: The ID of the movie being rated, which corresponds to the
            movie's unique ID in the 'movies' table.
        user_id: The ID of the user who provided the rating, which corresponds
            to the user's unique ID in the 'users' table.
        score: The rating score provided by the user for the movie (integer
            on a scale of 1-10).
        created_at: Timestamp indicating when the rating was created.
        updated_at: Timestamp indicating the last update of the rating.

    Relationships:
        user: A relationship to the User entity, representing the user who
            provided the rating.
        movie: A relationship to the Movie entity, representing the movie
            being rated.
    """
    __tablename__ = "ratings"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    movie_id = Column(GUID, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)  # 1-10 rating scale
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ensure a user can only rate a movie once
    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_rating'),
    )

    # Relationships
    user = relationship("User", backref="ratings")
    movie = relationship("Movie", backref="ratings")
