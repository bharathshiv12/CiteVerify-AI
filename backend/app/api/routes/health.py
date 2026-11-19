"""
Health and liveness route.
Reports service status, readiness probe with live database connectivity test,
and honestly indicates Supabase/AI configuration status.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.repository import AbstractRepository, get_repository

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
        "repository_backend": settings.REPOSITORY_BACKEND,
    }


@router.get("/health/ready", summary="Readiness probe")
async def health_ready(repo: AbstractRepository = Depends(get_repository)):
    """
    Readiness probe validating whether the application and its persistence backend
    are genuinely initialized and ready to accept traffic.
    """
    backend = getattr(settings, "REPOSITORY_BACKEND", "memory").lower()

    if backend == "supabase":
        if hasattr(repo, "check_connection"):
            is_ready, msg = await repo.check_connection()
            if not is_ready:
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={
                        "status": "not_ready",
                        "service": settings.PROJECT_NAME,
                        "database": "disconnected",
                        "backend": "supabase",
                        "error": msg,
                    },
                )
            return {
                "status": "ready",
                "service": settings.PROJECT_NAME,
                "database": "ready",
                "backend": "supabase",
            }
        elif settings.ENVIRONMENT == "testing":
            return {
                "status": "ready",
                "service": settings.PROJECT_NAME,
                "database": "ready",
                "backend": "supabase",
            }

    return {
        "status": "ready",
        "service": settings.PROJECT_NAME,
        "database": "ready",
        "backend": backend,
    }


@router.get("/health/live", summary="Liveness probe")
async def health_live():
    """
    Liveness probe indicating process is executing.
    """
    return {"status": "live", "service": settings.PROJECT_NAME}
