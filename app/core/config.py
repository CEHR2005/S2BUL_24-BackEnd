import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Movie Rating API"

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/moviedb")

    # CORS settings
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def CORS_ORIGINS_LIST(self) -> list:
        cors_origins = os.getenv("CORS_ORIGINS", self.CORS_ORIGINS)
        if cors_origins:
            return [origin.strip() for origin in cors_origins.split(",")]
        return ["http://localhost:5173"]  # Default Frontend Vite port

    model_config = ConfigDict(env_file=".env")

settings = Settings()
