"""
API routes package exports.
"""
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router
from app.api.routes.claims import router as claims_router
from app.api.routes.research import router as research_router

__all__ = [
    "health_router",
    "auth_router",
    "documents_router",
    "claims_router",
    "research_router",
]
