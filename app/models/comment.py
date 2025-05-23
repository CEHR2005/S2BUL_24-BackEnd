import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.database.custom_types import GUID

class Comment(Base):
    """
    Represents a comment made by a user on a specific movie.

    This class defines the structure of a comment, including attributes for the ID
    of the comment, the associated movie and user, the text content of the comment,
    and timestamp fields for creation and updates. The purpose of this class is to
    store and manage comments related to movies, and it establishes relationships
    with the User and Movie classes for tracking the comment's ownership and target
    movie.

    Attributes:
        id: GUID
            The unique identifier of the comment, generated by default as a UUID.
        movie_id: GUID
            The unique identifier of the movie the comment is associated with.
        user_id: GUID
            The unique identifier of the user who made the comment.
        text: str
            The content of the comment written by the user.
        created_at: datetime
            The timestamp when the comment was created, defaulted to the current
            UTC time.
        updated_at: datetime
            The timestamp when the comment was last updated, defaulted to the
            current UTC time, updated automatically on modification.
        user: User
            The relationship to the User model, linking the comment to the user who
            authored it.
        movie: Movie
            The relationship to the Movie model, linking the comment to the movie
            it is associated with.
    """
    __tablename__ = "comments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    movie_id = Column(GUID, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="comments")
    movie = relationship("Movie", backref="comments")
