import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text

from app.database.database import Base
from app.database.custom_types import ArrayOfStrings, GUID

class Movie(Base):
    __tablename__ = "movies"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False)
    release_year = Column(Integer, nullable=False)
    director = Column(String, nullable=False)
    cast = Column(ArrayOfStrings, nullable=False)
    genre = Column(ArrayOfStrings, nullable=False)
    plot = Column(Text, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    poster_url = Column(String, nullable=True)
    images = Column(ArrayOfStrings, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
