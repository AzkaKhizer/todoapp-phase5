"""Environment configuration for the Todo backend application."""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://localhost/todo"
        )
        self.jwt_secret: str = os.getenv(
            "JWT_SECRET",
            "dev-secret-key-change-in-production"
        )
        self.jwt_expiry_hours: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
        self.cors_origins: list[str] = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000"
        ).split(",")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
