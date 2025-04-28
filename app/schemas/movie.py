from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# Shared properties
class MovieBase(BaseModel):
    """
    Represents a movie object with various attributes.

    This class serves as a base data model for movies. It includes information
    such as the title, release year, director, cast, genre, plot, duration, and
    optional media assets like a poster URL and additional images. Instances of
    this class can be used to model movies in a database or as a portable data
    transfer object.
    """
    title: str
    release_year: int
    director: str
    cast: List[str]
    genre: List[str]
    plot: str
    duration: int
    poster_url: Optional[str] = None
    images: Optional[List[str]] = None

# Properties to receive via API on creation
class MovieCreate(MovieBase):
    """
    Represents a MovieCreation entity that inherits properties from the MovieBase class.

    This class is typically used to add functionality specific to movie creation processes.
    It provides a structure that ensures uniformity and coherence when dealing with movie
    creation operations. As a subclass of MovieBase, it maintains all base attributes and
    can be extended for additional behaviors, constraints, or validations related to creating
    movies.
    """
    pass

# Properties to receive via API on update
class MovieUpdate(BaseModel):
    """
    Represents an updatable movie entity.

    This class models the properties of a movie that can be updated. It is used to handle partial updates for
    movie data. Each attribute is optional, allowing selective modifications when required. The usage of this
    class facilitates flexibility in managing movie records, ensuring only specific fields are altered as
    needed.

    Attributes
    ----------
    title : Optional[str]
        The title of the movie.
    release_year : Optional[int]
        The year the movie was released.
    director : Optional[str]
        The name of the director of the movie.
    cast : Optional[List[str]]
        A list of names of cast members featured in the movie.
    genre : Optional[List[str]]
        A list of genres that classify the movie.
    plot : Optional[str]
        A brief description of the movie's storyline.
    duration : Optional[int]
        The total runtime of the movie in minutes.
    poster_url : Optional[str]
        The URL to the movie's poster image.
    images : Optional[List[str]]
        A list of URLs to additional images or stills from the movie.
    """
    title: Optional[str] = None
    release_year: Optional[int] = None
    director: Optional[str] = None
    cast: Optional[List[str]] = None
    genre: Optional[List[str]] = None
    plot: Optional[str] = None
    duration: Optional[int] = None
    poster_url: Optional[str] = None
    images: Optional[List[str]] = None

# Properties to return via API
class Movie(MovieBase):
    """
    Represents a movie entity with details about its creation and updates.

    This class inherits from MovieBase and is used to define the properties of a
    movie entity, including its unique identifier and timestamps for creation and
    modification. It utilizes a model configuration to enable attribute-based
    initialization.
    """
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
