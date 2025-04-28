import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text

from app.database.database import Base
from app.database.custom_types import ArrayOfStrings, GUID

class Movie(Base):
    """Represents a movie entity for use in the database model.

    This class defines the structure and attributes of a movie entity, including
    details such as the movie's title, release year, director, cast, genre, plot,
    duration, and related media such as posters and additional images. It is
    intended to store and manage metadata and content related to a movie in a
    persistent database.

    Attributes:
        id: Unique identifier for the movie.
        title: Title of the movie.
        release_year: Year the movie was released.
        director: Name of the movie's director.
        cast: List of names of the cast members.
        genre: List of genres the movie belongs to.
        plot: Description or synopsis of the movie's storyline.
        duration: Length of the movie in minutes.
        poster_url: URL path to the movie's poster image. Optional.
        images: List of URLs for additional related images. Optional.
        created_at: Timestamp when the movie record was created.
        updated_at: Timestamp when the movie record was last updated.
    """
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
