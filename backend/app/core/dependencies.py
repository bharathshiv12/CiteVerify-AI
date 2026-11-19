"""
FastAPI dependency injection utilities for authentication, repository access, and rate limiting.
"""
from typing import Optional
from uuid import UUID
from fastapi import Depends, Header, Request, status

from app.core.config import settings
from app.core.errors import UnauthorizedError, NotFoundError, ForbiddenError
from app.core.security import verify_jwt_token
from app.core.rate_limit import limiter
from app.database.repository import AbstractRepository, get_repository
from app.schemas.user import User
from app.schemas.document import Document


async def get_optional_user(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[User]:
    """
    Extracts and validates JWT if Authorization header is provided.
    Does not raise UnauthorizedError if missing (allows public/guest access).
    """
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    try:
        user = await verify_jwt_token(token)
        request.state.user_id = str(user.id)
        request.state.jwt_token = token
        return user
    except UnauthorizedError:
        return None


async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> User:
    """
    Strict authentication dependency. Raises 401 Unauthorized if token is missing or invalid.
    """
    if not authorization:
        raise UnauthorizedError("Authorization header is required (Bearer <token>).")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedError("Invalid Authorization header format. Expected 'Bearer <token>'.")

    user = await verify_jwt_token(token)
    request.state.user_id = str(user.id)
    request.state.jwt_token = token
    return user


async def verify_document_access(
    document_id: UUID,
    user: Optional[User] = Depends(get_optional_user),
    repo: AbstractRepository = Depends(get_repository),
) -> Document:
    """
    Retrieves document and checks ownership.
    - If document has an owner and user is not authenticated: returns 401 Unauthorized.
    - If document has an owner and caller is not the owner: returns 404 (non-disclosing).
    """
    doc = await repo.get_document(document_id)
    if not doc:
        raise NotFoundError(resource="Document", identifier=str(document_id))

    # If document has an owner, ensure caller is the owner
    owner_id = await repo.get_document_owner(doc.id)
    if owner_id:
        if not user:
            raise UnauthorizedError("Authentication required to access this document.")
        if user.id != owner_id:
            raise NotFoundError(resource="Document", identifier=str(document_id))

    return doc


async def verify_claim_access(
    claim_id: UUID,
    user: Optional[User] = Depends(get_optional_user),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Retrieves claim and checks owning document ownership.
    - If document has an owner and user is not authenticated: returns 401 Unauthorized.
    - If document has an owner and caller is not the owner: returns 404 (non-disclosing).
    """
    claim = await repo.get_claim(claim_id)
    if not claim:
        raise NotFoundError(resource="Claim", identifier=str(claim_id))

    owner_id = await repo.get_document_owner(claim.document_id)
    if owner_id:
        if not user:
            raise UnauthorizedError("Authentication required to access this claim.")
        if user.id != owner_id:
            raise NotFoundError(resource="Claim", identifier=str(claim_id))

    return claim


def rate_limit(bucket: str, max_requests: int, window_seconds: int = 60):
    """
    Dependency generating a rate limit checker.
    """
    async def dependency(request: Request):
        limiter.check(request, bucket, max_requests, window_seconds)
    return dependency
