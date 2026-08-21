from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    secret_key: str
    api_v1_prefix: str = "/api/v1"

    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20

    fortyguard_api_key: str
    fortyguard_base_url: str = "https://api.fortyguard.com"
    fortyguard_poll_interval: int = 3
    fortyguard_max_wait: int = 300

    google_api_key: str
    gemini_model: str = "gemini-2.0-flash"

    chroma_path: str = "./chroma_db"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"

    scheduler_interval_minutes: int = 15

    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()