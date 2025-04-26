from typing import Dict
from pydantic import BaseModel, RootModel

class AgeStatistics(BaseModel):
    under18: int = 0
    age18to24: int = 0
    age25to34: int = 0
    age35to44: int = 0
    age45to54: int = 0
    age55plus: int = 0

class GenderStatistics(BaseModel):
    male: int = 0
    female: int = 0
    other: int = 0
    not_specified: int = 0

class ContinentStatistics(BaseModel):
    africa: int = 0
    asia: int = 0
    europe: int = 0
    north_america: int = 0
    south_america: int = 0
    australia: int = 0
    antarctica: int = 0

class CountryStatistics(RootModel):
    root: Dict[str, int]

class MovieStatistics(BaseModel):
    movie_id: str
    average_rating: float
    total_ratings: int
    age_statistics: AgeStatistics
    gender_statistics: GenderStatistics
    continent_statistics: ContinentStatistics
    country_statistics: CountryStatistics

    class Config:
        from_attributes = True
