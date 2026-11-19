"""
Health and liveness route.
"""
from datetime import datetime, timezone
from fastapi import APIRouter
from app.config.settings import settings

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check")
async def health_check():
    """
    Returns liveness status, service identifier, version, and current UTC timestamp.
    """
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

