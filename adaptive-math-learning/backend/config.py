from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Adaptive Math Learning"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./data/math_learning.db"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"

    # Mastery Tracking
    ema_alpha: float = 0.3
    initial_mastery: float = 0.5

    # Question Generation
    question_timeout_seconds: int = 3
    max_distractors: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
