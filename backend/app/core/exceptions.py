"""
Core exceptions alias.
Re-exports from app.core.errors.
"""
from app.core.errors import (
    AppException,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    PayloadTooLargeError,
    InvalidFileError,
    RateLimitExceededError,
    ServiceUnavailableError,
)

__all__ = [
    "AppException",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "PayloadTooLargeError",
    "InvalidFileError",
    "RateLimitExceededError",
    "ServiceUnavailableError",
]
