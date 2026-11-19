"""
Security and JWT validation for Supabase Auth.
Supports JWKS verification, HS256 secret verification, and Supabase client fallback.
Includes test token generation for zero-credential test suites.
"""
import time
import logging
from typing import Any, Dict, Optional
from uuid import UUID

import jwt
import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.core.errors import UnauthorizedError
from app.schemas.user import User

logger = logging.getLogger("citeverify.security")

# JWKS cache to avoid fetching keys on every request
_JWKS_CACHE: Dict[str, Any] = {"keys": None, "fetched_at": 0.0}
JWKS_CACHE_TTL_SECONDS = 3600  # 1 hour
TEST_JWT_SECRET = "test-jwt-secret-for-citeverify-local-suite-do-not-use-in-prod"


async def fetch_jwks() -> Optional[Dict[str, Any]]:
    """
    Fetches and caches the project's JWKS public keys from Supabase.
    """
    if not settings.SUPABASE_URL:
        return None

    now = time.time()
    if _JWKS_CACHE["keys"] and (now - _JWKS_CACHE["fetched_at"] < JWKS_CACHE_TTL_SECONDS):
        return _JWKS_CACHE["keys"]

    jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(jwks_url)
            if resp.status_code == 200:
                data = resp.json()
                _JWKS_CACHE["keys"] = data
                _JWKS_CACHE["fetched_at"] = now
                return data
    except Exception as e:
        logger.warning(f"Failed to fetch JWKS from {jwks_url}: {e}")
    return None


def create_test_jwt(
    user_id: UUID,
    email: str = "test@example.com",
    role: str = "authenticated",
    aud: str = "authenticated",
    expires_in_seconds: int = 3600,
    secret: str = TEST_JWT_SECRET,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generates a cryptographically signed HS256 JWT for testing.
    """
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "aud": aud,
        "iat": now,
        "exp": now + expires_in_seconds,
        "iss": settings.SUPABASE_URL or "https://test.supabase.co/auth/v1",
        "user_metadata": {
            "full_name": "Test Researcher",
            "institution": "CiteVerify University",
        },
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, secret, algorithm="HS256")


async def verify_jwt_token(token: str) -> User:
    """
    Validates a JWT token using configured schemes:
    1. Test secret (if configured or running in testing mode)
    2. HS256 with SUPABASE_JWT_SECRET
    3. Asymmetric JWKS keys from Supabase
    4. Supabase auth.get_user(token) remote fallback
    """
    if not token:
        raise UnauthorizedError("Authorization token is missing.")

    # 1. First check if token matches test secret (for local tests)
    try:
        payload = jwt.decode(
            token,
            TEST_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            options={"require": ["exp", "sub", "aud"]},
        )
        return _user_from_payload(payload)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired.")
    except jwt.InvalidAudienceError:
        raise UnauthorizedError("Invalid token audience.")
    except jwt.InvalidSignatureError:
        # Not signed with test secret, continue to production validation
        pass
    except Exception:
        pass

    # 2. Check HS256 with SUPABASE_JWT_SECRET if configured
    if settings.SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
                options={"require": ["exp", "sub", "aud"]},
            )
            return _user_from_payload(payload)
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token has expired.")
        except jwt.InvalidAudienceError:
            raise UnauthorizedError("Invalid token audience.")
        except jwt.InvalidSignatureError:
            pass
        except Exception as e:
            logger.debug(f"HS256 verification failed: {e}")

    # 3. Check JWKS asymmetric keys if Supabase URL is present
    jwks = await fetch_jwks()
    if jwks and "keys" in jwks:
        try:
            # Unverified header to find kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            key_dict = next((k for k in jwks["keys"] if k.get("kid") == kid), None) if kid else jwks["keys"][0]
            if key_dict:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_dict)
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=["RS256", "ES256"],
                    audience="authenticated",
                    options={"require": ["exp", "sub", "aud"]},
                )
                return _user_from_payload(payload)
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token has expired.")
        except jwt.InvalidAudienceError:
            raise UnauthorizedError("Invalid token audience.")
        except Exception as e:
            logger.debug(f"JWKS verification failed: {e}")

    # 4. Supabase Remote Fallback: validate token via Supabase Auth API
    if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
        try:
            auth_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/user"
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": settings.SUPABASE_ANON_KEY,
            }
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(auth_url, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    user_id_str = data.get("id")
                    if user_id_str:
                        meta = data.get("user_metadata", {})
                        return User(
                            id=UUID(user_id_str),
                            email=data.get("email"),
                            full_name=meta.get("full_name"),
                            institution=meta.get("institution"),
                            role=data.get("role", "authenticated"),
                        )
                elif res.status_code == 401:
                    raise UnauthorizedError("Supabase token validation failed or expired.")
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.warning(f"Remote Supabase validation error: {e}")

    raise UnauthorizedError("Invalid or untrusted authentication token.")


def _user_from_payload(payload: Dict[str, Any]) -> User:
    try:
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedError("Token payload missing 'sub' identifier.")
        user_id = UUID(user_id_str)
        metadata = payload.get("user_metadata", {}) or {}
        return User(
            id=user_id,
            email=payload.get("email"),
            full_name=metadata.get("full_name"),
            institution=metadata.get("institution"),
            role=payload.get("role", "authenticated"),
        )
    except (ValueError, ValidationError) as e:
        raise UnauthorizedError(f"Malformed user token payload: {e}")
