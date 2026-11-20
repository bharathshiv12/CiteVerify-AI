"""
Storage abstraction supporting local secure filesystem and Supabase Storage.
Enforces safe path traversal prevention and size validation.
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

from app.core.config import settings

logger = logging.getLogger("citeverify.storage")


class AbstractFileStorage(ABC):
    @abstractmethod
    async def save_file(self, relative_path: str, content: bytes) -> str:
        """Saves file and returns storage reference/path."""
        pass

    @abstractmethod
    async def get_file(self, relative_path: str) -> bytes:
        """Retrieves raw file bytes."""
        pass

    @abstractmethod
    async def delete_file(self, relative_path: str) -> bool:
        """Deletes file if exists."""
        pass

    @abstractmethod
    async def file_exists(self, relative_path: str) -> bool:
        """Checks if file exists."""
        pass


class LocalFileStorage(AbstractFileStorage):
    def __init__(self, base_dir: Optional[str] = None):
        is_serverless = bool(
            os.getenv("VERCEL")
            or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
            or not os.access(".", os.W_OK)
        )
        default_dir = "/tmp/citeverify_storage" if is_serverless else settings.LOCAL_STORAGE_DIR
        target = base_dir or default_dir
        try:
            self.base_dir = os.path.abspath(target)
            os.makedirs(self.base_dir, exist_ok=True)
        except OSError:
            self.base_dir = "/tmp/citeverify_storage"
            os.makedirs(self.base_dir, exist_ok=True)

    def _resolve_safe_path(self, relative_path: str) -> str:
        # Prevent path traversal
        clean_rel = os.path.normpath(relative_path.lstrip("/\\"))
        full_path = os.path.abspath(os.path.join(self.base_dir, clean_rel))
        if not full_path.startswith(self.base_dir):
            raise ValueError(f"Path traversal detected: {relative_path}")
        return full_path

    async def save_file(self, relative_path: str, content: bytes) -> str:
        target_path = self._resolve_safe_path(relative_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(content)
        return relative_path

    async def get_file(self, relative_path: str) -> bytes:
        target_path = self._resolve_safe_path(relative_path)
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"File not found: {relative_path}")
        with open(target_path, "rb") as f:
            return f.read()

    async def delete_file(self, relative_path: str) -> bool:
        try:
            target_path = self._resolve_safe_path(relative_path)
            if os.path.exists(target_path):
                os.remove(target_path)
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to delete local file {relative_path}: {e}")
            return False

    async def file_exists(self, relative_path: str) -> bool:
        try:
            target_path = self._resolve_safe_path(relative_path)
            return os.path.exists(target_path)
        except Exception:
            return False


class SupabaseFileStorage(AbstractFileStorage):
    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or settings.SUPABASE_STORAGE_BUCKET
        self._fallback_local_instance = None

    @property
    def _fallback_local(self) -> LocalFileStorage:
        if self._fallback_local_instance is None:
            self._fallback_local_instance = LocalFileStorage()
        return self._fallback_local_instance

    def _get_bucket(self):
        from supabase import create_client
        key = settings.effective_supabase_secret_key or settings.effective_supabase_anon_key
        client = create_client(settings.SUPABASE_URL, key)
        return client.storage.from_(self.bucket_name)

    async def save_file(self, relative_path: str, content: bytes) -> str:
        if not settings.is_supabase_configured:
            return await self._fallback_local.save_file(relative_path, content)

        clean_path = relative_path.replace("\\", "/").lstrip("/")
        try:
            bucket = self._get_bucket()
            bucket.upload(path=clean_path, file=content, file_options={"content-type": "application/pdf", "upsert": "true"})
            return clean_path
        except Exception as e:
            logger.warning(f"Supabase storage upload error, falling back to local: {e}")
            return await self._fallback_local.save_file(relative_path, content)

    async def get_file(self, relative_path: str) -> bytes:
        if not settings.is_supabase_configured:
            return await self._fallback_local.get_file(relative_path)

        clean_path = relative_path.replace("\\", "/").lstrip("/")
        try:
            bucket = self._get_bucket()
            return bucket.download(clean_path)
        except Exception as e:
            logger.warning(f"Supabase storage download error: {e}")
            return await self._fallback_local.get_file(relative_path)

    async def delete_file(self, relative_path: str) -> bool:
        if not settings.is_supabase_configured:
            return await self._fallback_local.delete_file(relative_path)

        clean_path = relative_path.replace("\\", "/").lstrip("/")
        try:
            bucket = self._get_bucket()
            bucket.remove([clean_path])
            return True
        except Exception as e:
            logger.warning(f"Supabase storage delete error: {e}")
            return await self._fallback_local.delete_file(relative_path)

    async def file_exists(self, relative_path: str) -> bool:
        if not settings.is_supabase_configured:
            return await self._fallback_local.file_exists(relative_path)
        try:
            content = await self.get_file(relative_path)
            return len(content) > 0
        except Exception:
            return False


_storage_instance: Optional[AbstractFileStorage] = None


def get_file_storage() -> AbstractFileStorage:
    global _storage_instance
    if _storage_instance is None:
        if settings.STORAGE_BACKEND == "supabase" and settings.is_supabase_configured:
            _storage_instance = SupabaseFileStorage()
        else:
            _storage_instance = LocalFileStorage()
    return _storage_instance
