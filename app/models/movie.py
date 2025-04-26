import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False)
    release_year = Column(Integer, nullable=False)
    director = Column(String, nullable=False)
    cast = Column(ARRAY(String), nullable=False)
    genre = Column(ARRAY(String), nullable=False)
    plot = Column(Text, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    poster_url = Column(String, nullable=True)
    images = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)