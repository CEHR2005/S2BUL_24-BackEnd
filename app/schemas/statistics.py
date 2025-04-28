from typing import Dict
from pydantic import BaseModel, RootModel, ConfigDict

class AgeStatistics(BaseModel):
    """
    Represents age-related statistics with various predefined age group segments.

    This class inherits from BaseModel and is used to store and manage statistical
    data for distinct age groups. Each attribute corresponds to a specific age
    group, allowing for organized and clear representation of demographic age
    statistics.

    Attributes:
        under18 (int): Represents the count of individuals under the age of 18.
            Defaults to 0.
        age18to24 (int): Represents the count of individuals aged 18 to 24.
            Defaults to 0.
        age25to34 (int): Represents the count of individuals aged 25 to 34.
            Defaults to 0.
        age35to44 (int): Represents the count of individuals aged 35 to 44.
            Defaults to 0.
        age45to54 (int): Represents the count of individuals aged 45 to 54.
            Defaults to 0.
        age55plus (int): Represents the count of individuals aged 55 and above.
            Defaults to 0.
    """
    under18: int = 0
    age18to24: int = 0
    age25to34: int = 0
    age35to44: int = 0
    age45to54: int = 0
    age55plus: int = 0

class GenderStatistics(BaseModel):
    """
    Represents statistical data related to gender.

    This class is designed to store and manage information regarding the
    count of individuals within specific gender categories, including male,
    female, other, and not specified.
    """
    male: int = 0
    female: int = 0
    other: int = 0
    not_specified: int = 0

class ContinentStatistics(BaseModel):
    """
    Represents statistical data for different continents.

    This class is a data model intended to store and represent the statistics
    for each continent. It allows for organizing count or other numerical data
    related to specific continents.

    Attributes:
        africa (int): Statistic for Africa. Defaults to 0.
        asia (int): Statistic for Asia. Defaults to 0.
        europe (int): Statistic for Europe. Defaults to 0.
        north_america (int): Statistic for North America. Defaults to 0.
        south_america (int): Statistic for South America. Defaults to 0.
        australia (int): Statistic for Australia. Defaults to 0.
        antarctica (int): Statistic for Antarctica. Defaults to 0.
    """
    africa: int = 0
    asia: int = 0
    europe: int = 0
    north_america: int = 0
    south_america: int = 0
    australia: int = 0
    antarctica: int = 0

class CountryStatistics(RootModel):
    """
    Represents statistical data for countries in a structured format.

    This class is designed to hold statistical information about various
    countries in the form of key-value pairs. The keys are country names
    represented as strings, and the values are integers representing
    associated statistics for these countries.
    """
    root: Dict[str, int]

class MovieStatistics(BaseModel):
    """
    Represents statistical data for a specific movie.

    This class encapsulates details about a movie's statistical information,
    including average ratings, total ratings, and demographic-based statistics
    in various categories such as age, gender, continent, and country.

    Attributes
    ----------
    movie_id : str
        Unique identifier for the movie.
    average_rating : float
        The average rating given to the movie by users.
    total_ratings : int
        Total number of ratings received by the movie.
    age_statistics : AgeStatistics
        Statistical rating information categorized by different age groups.
    gender_statistics : GenderStatistics
        Statistical data categorized by gender demographics.
    continent_statistics : ContinentStatistics
        Statistical data sorted by continent-level demographics.
    country_statistics : CountryStatistics
        Statistical data categorized by country-level demographics.
    """
    movie_id: str
    average_rating: float
    total_ratings: int
    age_statistics: AgeStatistics
    gender_statistics: GenderStatistics
    continent_statistics: ContinentStatistics
    country_statistics: CountryStatistics

    model_config = ConfigDict(from_attributes=True)
