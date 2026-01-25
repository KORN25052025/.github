"""
Application configuration using Pydantic Settings.

Supports environment variables and .env file configuration.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Adaptive Math Learning"
    app_version: str = "2.0.0"
    debug: bool = True
    environment: str = "development"  # development, staging, production

    # Database - Supports SQLite (dev) and PostgreSQL/Supabase (prod)
    database_url: str = "sqlite:///./data/math_learning.db"
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Supabase Configuration (optional - for production)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None

    # Anthropic Claude API (Primary LLM)
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # OpenAI API (DALL-E 3 and fallback LLM)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    dalle_model: str = "dall-e-3"

    # PostHog Analytics & A/B Testing
    posthog_api_key: Optional[str] = None
    posthog_host: str = "https://app.posthog.com"

    # BKT (Bayesian Knowledge Tracing) Parameters
    bkt_p_l0: float = 0.1    # Initial mastery probability
    bkt_p_t: float = 0.3     # Learn rate
    bkt_p_g: float = 0.25    # Guess rate
    bkt_p_s: float = 0.1     # Slip rate

    # Legacy EMA (kept for backward compatibility)
    ema_alpha: float = 0.3
    initial_mastery: float = 0.5

    # Question Generation
    question_timeout_seconds: int = 3
    max_distractors: int = 3
    enable_story_generation: bool = True
    enable_visual_generation: bool = True
    default_language: str = "tr"  # Turkish

    # Gamification
    enable_gamification: bool = True
    enable_leaderboard: bool = True
    xp_multiplier: float = 1.0

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period_seconds: int = 60

    # CORS (for mobile app)
    cors_origins: str = "*"  # Comma-separated origins

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_postgres(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.database_url.startswith("postgresql")

    @property
    def cors_origins_list(self) -> list:
        """Get CORS origins as list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
