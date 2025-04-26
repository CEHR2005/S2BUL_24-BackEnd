from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Shared properties
class MovieBase(BaseModel):
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
    pass

# Properties to receive via API on update
class MovieUpdate(BaseModel):
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
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
