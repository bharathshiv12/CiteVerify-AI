"""
Application configuration using pydantic-settings.
Reads environment variables with sensible defaults for development and testing.
"""
from typing import List, Union
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
    ENVIRONMENT: str = "development"

    # CORS settings
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:3000"

    # Upload constraints
    MAX_UPLOAD_SIZE_MB: int = 25
    UPLOAD_DIR: str = "backend/uploads"

    # Storage Backend: supabase | local
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_DIR: str = "backend/storage_data"
    SUPABASE_STORAGE_BUCKET: str = "sapthack-documents"

    # Repository Backend: memory | supabase
    REPOSITORY_BACKEND: str = "memory"

    # Database / Supabase settings
    DATABASE_URL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_PUBLISHABLE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_SECRET_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # Research APIs & Polite Pool
    CROSSREF_API_URL: str = "https://api.crossref.org"
    OPENALEX_API_URL: str = "https://api.openalex.org"
    EUROPE_PMC_API_URL: str = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    CONTACT_EMAIL: str = "researcher@example.com"
    OPENALEX_EMAIL: str = "researcher@example.com"
    CROSSREF_EMAIL: str = "researcher@example.com"

    # AI / LLM settings (default: none)
    AI_PROVIDER: str = "none"  # "none" | "gemini" | "groq" | "ollama"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gemini-1.5-flash"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    AUTH_RATE_LIMIT: int = 30  # per minute
    UPLOAD_RATE_LIMIT: int = 15  # per minute
    RESEARCH_RATE_LIMIT: int = 60  # per minute

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            origins = list(self.CORS_ORIGINS)
        elif isinstance(self.CORS_ORIGINS, str):
            origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        else:
            origins = ["http://localhost:3000"]

        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins if origins else ["http://localhost:3000"]

    @property
    def effective_supabase_secret_key(self) -> str:
        return self.SUPABASE_SECRET_KEY or self.SUPABASE_SERVICE_ROLE_KEY

    @property
    def effective_supabase_anon_key(self) -> str:
        return self.SUPABASE_PUBLISHABLE_KEY or self.SUPABASE_ANON_KEY

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.SUPABASE_URL and (self.effective_supabase_anon_key or self.effective_supabase_secret_key))

    @property
    def is_ai_configured(self) -> bool:
        return self.AI_PROVIDER != "none" and bool(self.AI_API_KEY)


settings = Settings()
