"""
Main FastAPI application entry point for CiteVerify AI backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config.settings import settings
from app.core.errors import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.core.middleware import RequestIdAndLoggingMiddleware
from app.api.routes import (
    health_router,
    auth_router,
    documents_router,
    claims_router,
    research_router,
    dashboard_router,
    settings_router,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="CiteVerify AI Backend",
        description="Scientific Claim and Citation Verification System API",
        version=settings.VERSION,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # 1. Request ID and Access Logging Middleware
    app.add_middleware(RequestIdAndLoggingMiddleware)

    # 2. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time-Ms"],
    )

    # 3. Global Exception Handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # 4. Route Registration under /api prefix
    app.include_router(health_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    app.include_router(documents_router, prefix="/api")
    app.include_router(claims_router, prefix="/api")
    app.include_router(research_router, prefix="/api")
    app.include_router(dashboard_router, prefix="/api")
    app.include_router(settings_router, prefix="/api")

    return app


app = create_app()

