"""
Health and liveness route.
Reports service status and honestly indicates Supabase/AI configuration status.
"""
from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check")
async def health_check():
    """
    Returns liveness status, service identifier, version, current UTC timestamp,
    and honest configuration status for Supabase, Storage, and AI provider.
    """
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "supabase_configured": settings.is_supabase_configured,
        "ai_configured": settings.is_ai_configured,
        "storage_backend": settings.STORAGE_BACKEND,
    }
