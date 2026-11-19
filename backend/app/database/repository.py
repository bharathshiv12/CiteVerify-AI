"""
Repository factory and backward-compatibility facade.
Exports AbstractRepository, InMemoryRepository, SupabaseRepository, and get_repository.
"""
import sys
import logging
from typing import Optional

from app.core.config import settings
from app.repositories.base import AbstractRepository
from app.repositories.memory_repo import InMemoryRepository
from app.repositories.supabase_repo import SupabaseRepository

logger = logging.getLogger("citeverify.repository")

# Global in-memory singleton for development and test suites
_in_memory_repository = InMemoryRepository()
_supabase_repository_instance: Optional[SupabaseRepository] = None


def get_repository() -> AbstractRepository:
    """
    FastAPI dependency injecting the configured repository.
    Returns SupabaseRepository if REPOSITORY_BACKEND == 'supabase'.
    In production mode, raises RuntimeError if Supabase is unconfigured.
    Defaults to InMemoryRepository when REPOSITORY_BACKEND == 'memory'.
    """
    global _supabase_repository_instance
    backend = getattr(settings, "REPOSITORY_BACKEND", "memory").lower()

    if backend == "supabase":
        if settings.ENVIRONMENT == "testing":
            return _in_memory_repository

        if not settings.is_supabase_configured:
            raise RuntimeError(
                "CRITICAL: REPOSITORY_BACKEND is set to 'supabase' but Supabase credentials "
                "are not configured. Please set SUPABASE_URL and SUPABASE_SECRET_KEY in environment."
            )

        if _supabase_repository_instance is None:
            _supabase_repository_instance = SupabaseRepository()
        return _supabase_repository_instance

    return _in_memory_repository


__all__ = [
    "AbstractRepository",
    "InMemoryRepository",
    "SupabaseRepository",
    "get_repository",
    "_in_memory_repository",
]
