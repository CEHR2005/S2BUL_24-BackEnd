from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Shared properties
class RatingBase(BaseModel):
    score: int = Field(..., ge=1, le=10)

    @field_validator('score', mode='before')
    def score_range(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Score must be between 1 and 10')
        return v

# Properties to receive via API on creation
class RatingCreate(RatingBase):
    movie_id: str

# Properties to return via API
class Rating(RatingBase):
    id: str
    movie_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Properties to return via API with user information
class RatingWithUser(Rating):
    user: dict

    model_config = ConfigDict(from_attributes=True)

# Movie rating statistics
class MovieRating(BaseModel):
    movie_id: str
    average_score: float
    total_ratings: int

    model_config = ConfigDict(from_attributes=True)
