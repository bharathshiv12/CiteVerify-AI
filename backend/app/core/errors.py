"""
Standardized error hierarchy and FastAPI exception handlers returning ErrorEnvelope.
Complies with contracts/schemas/error.schema.json.
"""
import uuid
import logging
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("citeverify.errors")


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class BadRequestError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="BAD_REQUEST",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details or {},
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication credentials were not provided or are invalid.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details or {},
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "You do not have permission to access this resource.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details or {},
        )


class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier},
        )


class ConflictError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details or {},
        )


class PayloadTooLargeError(AppException):
    def __init__(self, message: str = "Uploaded file exceeds maximum allowed size.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="PAYLOAD_TOO_LARGE",
            message=message,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details=details or {},
        )


class InvalidFileError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="INVALID_FILE",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details or {},
        )


class RateLimitExceededError(AppException):
    def __init__(self, message: str = "Rate limit exceeded. Please retry after some time.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details or {},
        )


class ServiceUnavailableError(AppException):
    def __init__(self, message: str = "Service is temporarily unconfigured or unavailable.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details or {},
        )


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", str(uuid.uuid4()))


def _attach_cors_headers(request: Request, response: JSONResponse) -> JSONResponse:
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = get_request_id(request)
    resp = JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            }
        },
    )
    return _attach_cors_headers(request, resp)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    request_id = get_request_id(request)
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        413: "PAYLOAD_TOO_LARGE",
        422: "UNPROCESSABLE_ENTITY",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    details = exc.detail if isinstance(exc.detail, dict) else {}
    if exc.status_code == 404:
        details = {
            **details,
            "path": request.url.path,
            "scope_path": request.scope.get("path", ""),
        }
    resp = JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
                "details": details,
                "request_id": request_id,
            }
        },
    )
    return _attach_cors_headers(request, resp)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = get_request_id(request)
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        errors.append({"field": field, "message": err.get("msg", ""), "type": err.get("type", "")})

    resp = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed against canonical schema.",
                "details": {"validation_errors": errors},
                "request_id": request_id,
            }
        },
    )
    return _attach_cors_headers(request, resp)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = get_request_id(request)
    logger.exception(f"[{request_id}] Unhandled internal exception: {exc}")
    resp = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please contact support with the request ID.",
                "details": {
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                },
                "request_id": request_id,
            }
        },
    )
    return _attach_cors_headers(request, resp)
