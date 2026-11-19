"""
Tests for Supabase JWT authentication, security rules, and ownership isolation.
Runs with zero external credentials using signed test JWTs.
"""
from uuid import uuid4
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_test_jwt, verify_jwt_token
from app.core.errors import UnauthorizedError
from app.database.repository import get_repository
from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.report import VerificationReport
from app.schemas.enums import ProcessingStatus, PipelineStage, VerificationVerdict, VerificationState


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user_id():
    return uuid4()


@pytest.fixture
def user_a():
    user_id = uuid4()
    token = create_test_jwt(user_id=user_id, email="user.a@university.edu")
    return {"id": user_id, "token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture
def user_b():
    user_id = uuid4()
    token = create_test_jwt(user_id=user_id, email="user.b@institute.org")
    return {"id": user_id, "token": token, "headers": {"Authorization": f"Bearer {token}"}}


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


def test_logout_endpoint(client):
    resp = client.post("/api/auth/logout")
    assert resp.status_code == 200
    assert "Logged out successfully" in resp.json()["message"]


def test_forgot_password_endpoint(client):
    resp = client.post("/api/auth/forgot-password", json={"email": "researcher@oxford.edu"})
    assert resp.status_code == 200
    assert "dispatched" in resp.json()["message"]


def test_reset_password_endpoint_with_auth(client, user_a):
    resp = client.post(
        "/api/auth/reset-password",
        json={"password": "NewSecurePassword123!"},
        headers=user_a["headers"],
    )
    assert resp.status_code == 200
    assert "successfully updated" in resp.json()["message"]


def test_reset_password_endpoint_unauthorized(client):
    resp = client.post("/api/auth/reset-password", json={"password": "NewPassword123!"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_cross_user_document_isolation(client, user_a, user_b):
    repo = get_repository()
    doc_id = uuid4()
    now = datetime.now(timezone.utc)

    doc = Document(
        id=doc_id,
        filename="user_a_private_paper.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        status=ProcessingStatus.COMPLETED,
        pipeline_stage=PipelineStage.DONE,
        page_count=1,
        is_scanned=False,
        error_message=None,
        created_at=now,
        updated_at=now,
    )
    await repo.create_document(doc, user_id=user_a["id"])

    # 1. User A can access own document
    res_a = client.get(f"/api/documents/{doc_id}", headers=user_a["headers"])
    assert res_a.status_code == 200
    assert res_a.json()["id"] == str(doc_id)

    # 2. Unauthenticated request receives 401 Unauthorized
    res_anon = client.get(f"/api/documents/{doc_id}")
    assert res_anon.status_code == 401
    assert res_anon.json()["error"]["code"] == "UNAUTHORIZED"

    # 3. User B receives non-disclosing 404 Not Found
    res_b = client.get(f"/api/documents/{doc_id}", headers=user_b["headers"])
    assert res_b.status_code == 404
    assert res_b.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_unauthorized_report_and_claims_isolation(client, user_a, user_b):
    repo = get_repository()
    doc_id = uuid4()
    claim_id = uuid4()
    now = datetime.now(timezone.utc)

    doc = Document(
        id=doc_id,
        filename="isolated_report_doc.pdf",
        file_size_bytes=2048,
        mime_type="application/pdf",
        status=ProcessingStatus.COMPLETED,
        pipeline_stage=PipelineStage.DONE,
        page_count=1,
        is_scanned=False,
        error_message=None,
        created_at=now,
        updated_at=now,
    )
    await repo.create_document(doc, user_id=user_a["id"])

    claim = Claim(
        id=claim_id,
        document_id=doc_id,
        claim_text="Private assertion owned by User A.",
        page_number=1,
        char_span=[0, 32],
        verdict=VerificationVerdict.SUPPORTED,
        verification_state=VerificationState.VERIFIED,
    )
    await repo.save_claims([claim])

    report = VerificationReport(
        document_id=doc_id,
        filename=doc.filename,
        generated_at=now,
        total_claims=1,
        reliability_score=100.0,
        verdict_counts={"SUPPORTED": 1},
        evidence_level_counts={"ABSTRACT_ONLY": 1, "FULL_TEXT": 0, "METADATA_ONLY": 0, "NONE": 0},
        human_review_required_count=0,
        claims=[claim],
    )
    await repo.save_report(report)

    # Report: Unauthenticated receives 401
    res_rep_anon = client.get(f"/api/documents/{doc_id}/report")
    assert res_rep_anon.status_code == 401

    # Report: User B receives non-disclosing 404
    res_rep_b = client.get(f"/api/documents/{doc_id}/report", headers=user_b["headers"])
    assert res_rep_b.status_code == 404

    # Report: User A succeeds
    res_rep_a = client.get(f"/api/documents/{doc_id}/report", headers=user_a["headers"])
    assert res_rep_a.status_code == 200

    # Claim: Unauthenticated receives 401
    res_claim_anon = client.get(f"/api/claims/{claim_id}")
    assert res_claim_anon.status_code == 401

    # Claim: User B receives non-disclosing 404
    res_claim_b = client.get(f"/api/claims/{claim_id}", headers=user_b["headers"])
    assert res_claim_b.status_code == 404

    # Claim: User A succeeds
    res_claim_a = client.get(f"/api/claims/{claim_id}", headers=user_a["headers"])
    assert res_claim_a.status_code == 200
