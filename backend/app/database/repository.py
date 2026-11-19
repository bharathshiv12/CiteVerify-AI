"""
Repository factory and backward-compatibility facade.
Exports AbstractRepository, InMemoryRepository, and get_repository.
"""
from typing import Optional
from fastapi import Request

from app.core.config import settings
from app.repositories.base import AbstractRepository
from app.repositories.memory_repo import InMemoryRepository
from app.repositories.supabase_repo import SupabaseRepository

# Global in-memory singleton for development and test suites
_in_memory_repository = InMemoryRepository()


def get_repository() -> AbstractRepository:
    """
    FastAPI dependency injecting the appropriate repository.
    Returns SupabaseRepository if configured, otherwise InMemoryRepository.
    """
    if settings.is_supabase_configured:
        return SupabaseRepository()
    return _in_memory_repository


__all__ = [
    "AbstractRepository",
    "InMemoryRepository",
    "SupabaseRepository",
    "get_repository",
    "_in_memory_repository",
]
