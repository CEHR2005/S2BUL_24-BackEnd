from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Shared properties
class RatingBase(BaseModel):
    """Representation of a base model for a rating system.

    This class extends BaseModel and provides a structure for a rating score
    with validation constraints. The score must be an integer within the range of
    1 to 10, inclusive. It ensures valid input with strict validation rules,
    while allowing for seamless integration into broader data modeling structures.

    Attributes:
        score: int
            An integer representing the rating score. Must be between 1 and 10,
            inclusive.

    Methods:
        score_range(v: Any) -> Any
            Validates that the provided score is within the acceptable range.
    """
    score: int = Field(..., ge=1, le=10)

    @field_validator('score', mode='before')
    def score_range(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Score must be between 1 and 10')
        return v

# Properties to receive via API on creation
class RatingCreate(RatingBase):
    """
    Represents the creation of a rating for a movie.

    This class is used to define the data representation required when creating
    a new rating for a movie. It inherits from RatingBase and extends it to
    include the specific attributes necessary for associating the rating with
    a particular movie in the system.

    Attributes:
        movie_id: A unique identifier for the movie to which the rating applies.
    """
    movie_id: str

# Properties to return via API
class Rating(RatingBase):
    """
    Represents a rating given by a user for a specific movie.

    This class is used to store information about a rating provided
    for a movie by a user. It includes data about the rating itself,
    associated movie and user identifiers, and timestamps for when
    the rating was created and last updated.

    Attributes:
        id: Unique identifier for the rating.
        movie_id: Identifier for the movie associated with this rating.
        user_id: Identifier for the user who provided this rating.
        created_at: Timestamp indicating when the rating was created.
        updated_at: Timestamp indicating the last update to the rating data.
    """
    id: str
    movie_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Properties to return via API with user information
class RatingWithUser(Rating):
    """
    Represents a rating with additional user information.

    This class extends the functionality of the Rating class by including
    a dictionary attribute for user information and setting up a model
    configuration to allow attributes to be generated from the provided
    attributes using a custom configuration.

    Attributes:
        user (dict): A dictionary containing information about a user.

    """
    user: dict

    model_config = ConfigDict(from_attributes=True)

# Movie rating statistics
class MovieRating(BaseModel):
    """
    Represents a movie rating with associated details.

    This class holds information about a particular movie's rating, including its ID,
    average score, and the total number of ratings it has received. It can be used
    to encapsulate movie rating data and provide a structured format for storage or
    manipulation.
    """
    movie_id: str
    average_score: float
    total_ratings: int

    model_config = ConfigDict(from_attributes=True)
