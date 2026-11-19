"""
Application configuration using pydantic-settings.
Reads environment variables with sensible local development defaults.
"""
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server settings
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    PROJECT_NAME: str = "citeverify-backend"
    VERSION: str = "1.0.0"

    # CORS settings
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:3000"

    # Upload constraints
    MAX_UPLOAD_SIZE_MB: int = 25
    UPLOAD_DIR: str = "uploads"

    # Database settings
    DATABASE_URL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # AI / LLM settings
    LLM_PROVIDER: str = "gemini"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Research APIs Polite Pool
    OPENALEX_EMAIL: str = "researcher@example.com"
    CROSSREF_EMAIL: str = "researcher@example.com"

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        if isinstance(self.CORS_ORIGINS, str):
            origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
            return origins if origins else ["http://localhost:3000"]
        return ["http://localhost:3000"]


settings = Settings()

