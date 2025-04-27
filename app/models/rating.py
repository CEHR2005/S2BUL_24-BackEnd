import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.database.custom_types import GUID

class Rating(Base):
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
