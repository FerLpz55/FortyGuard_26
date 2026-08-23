from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and configuration.
    
    Reads from .env file. Sensitive variables like secret_key must not be hardcoded
    and should be provided via environment variables.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    environment: str = "development"
    secret_key: str
    api_v1_prefix: str = "/api/v1"
    
    # Database
    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # FortyGuard Integration
    fortyguard_api_key: str
    fortyguard_base_url: str = "https://api.fortyguard.com"
    fortyguard_poll_interval: int = 3
    fortyguard_max_wait: int = 300
    
    # AI / Gemini
    google_api_key: str
    gemini_model: str = "gemini-2.0-flash"
    chroma_path: str = "./chroma_db"
    
    # Security & JWT
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"
    
    # Scheduled Tasks
    scheduler_interval_minutes: int = 15
    
    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Parses the comma-separated cors_origins string into a list of origins.
        """
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()
