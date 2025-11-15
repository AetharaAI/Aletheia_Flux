"""Configuration management for Aletheia backend."""
from pydantic_settings import BaseSettings
from typing import Optional
from supabase import create_client, Client


class Settings(BaseSettings):
    """Application settings."""

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # MiniMax API
    minimax_api_key: Optional[str] = None
    minimax_base_url: str = "https://api.minimax.io/anthropic"
    minimax_model: str = "claude-3-5-sonnet-20241022"

    # Tavily API
    tavily_api_key: Optional[str] = None

    # Grok API (Agent Discovery)
    grok_api_key: Optional[str] = None

    # Firecrawl API (Agent Discovery)
    firecrawl_api_key: Optional[str] = None

    # Agent Discovery Configuration
    discovery_enabled: bool = False
    discovery_schedule_hour: int = 2
    discovery_max_results: int = 50
    discovery_auto_verify_threshold: float = 0.9

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_per_minute: int = 20

    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra environment variables


settings = Settings()

# Initialize Supabase Client
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)
