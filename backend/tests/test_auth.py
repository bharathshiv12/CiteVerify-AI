"""
Tests for Supabase JWT authentication and security rules.
Runs with zero external credentials using signed test JWTs.
"""
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_test_jwt, verify_jwt_token
from app.core.errors import UnauthorizedError


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user_id():
    return uuid4()


@pytest.mark.asyncio
async def test_create_and_verify_valid_test_jwt(test_user_id):
    token = create_test_jwt(user_id=test_user_id, email="dr.sharma@example.edu")
    user = await verify_jwt_token(token)
    assert user.id == test_user_id
    assert user.email == "dr.sharma@example.edu"
    assert user.role == "authenticated"


@pytest.mark.asyncio
async def test_expired_jwt_rejected(test_user_id):
    token = create_test_jwt(user_id=test_user_id, expires_in_seconds=-10)
    with pytest.raises(UnauthorizedError, match="expired"):
        await verify_jwt_token(token)


@pytest.mark.asyncio
async def test_wrong_audience_rejected(test_user_id):
    token = create_test_jwt(user_id=test_user_id, aud="wrong_audience")
    with pytest.raises(UnauthorizedError, match="audience"):
        await verify_jwt_token(token)


@pytest.mark.asyncio
async def test_tampered_jwt_rejected(test_user_id):
    token = create_test_jwt(user_id=test_user_id)
    tampered_token = token[:-5] + "XXXXX"
    with pytest.raises(UnauthorizedError):
        await verify_jwt_token(tampered_token)


def test_auth_me_endpoint_with_valid_jwt(client, test_user_id):
    token = create_test_jwt(user_id=test_user_id, email="researcher@institute.ac.in")
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["id"] == str(test_user_id)
    assert data["user"]["email"] == "researcher@institute.ac.in"


def test_auth_me_endpoint_unauthorized(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == "UNAUTHORIZED"
