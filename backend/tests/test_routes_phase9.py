"""
Tests for Phase 9 routes: claims patch/review, dashboard stats/activity, settings, and PDF report export.
"""
import io
import fitz
import pytest
from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.database.repository import get_repository
from app.storage.file_storage import get_file_storage
from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.enums import ProcessingStatus, PipelineStage, VerificationVerdict, VerificationState
from app.schemas.report import VerificationReport
from app.core.security import create_test_jwt


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    token = create_test_jwt(user_id=uuid4(), email="user@test.org")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_claims_patch_and_review(client, auth_headers):
    repo = get_repository()
    doc_id = uuid4()
    claim_id = uuid4()

    doc = Document(
        id=doc_id,
        filename="test_paper.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        status=ProcessingStatus.COMPLETED,
        pipeline_stage=PipelineStage.DONE,
        page_count=1,
        is_scanned=False,
        error_message=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    await repo.create_document(doc)

    claim = Claim(
        id=claim_id,
        document_id=doc_id,
        claim_text="Initial claim assertion about algorithm accuracy.",
        page_number=1,
        char_span=[10, 56],
        verdict=VerificationVerdict.SUPPORTED,
        verification_state=VerificationState.VERIFIED,
        confidence=0.88,
        rationale="Preliminary rationale.",
        needs_human_review=False,
    )
    await repo.save_claims([claim])

    # 1. Test GET /api/claims/{claim_id}
    res = client.get(f"/api/claims/{claim_id}")
    assert res.status_code == 200
    assert res.json()["id"] == str(claim_id)

    # 2. Test PATCH /api/claims/{claim_id} (Gap 3)
    patch_payload = {
        "claim_text": "Updated edited assertion about algorithm accuracy.",
        "char_span": [10, 60],
    }
    res_patch = client.patch(f"/api/claims/{claim_id}", json=patch_payload)
    assert res_patch.status_code == 200
    assert res_patch.json()["claim_text"] == patch_payload["claim_text"]
    assert res_patch.json()["char_span"] == patch_payload["char_span"]

    # 3. Test POST /api/claims/{claim_id}/review
    review_payload = {
        "reviewer_name": "Dr. Peer Reviewer",
        "updated_verdict": "PARTLY_SUPPORTED",
        "notes": "Verified that findings hold only in subset of trials.",
    }
    res_review = client.post(f"/api/claims/{claim_id}/review", json=review_payload)
    assert res_review.status_code == 200
    review_data = res_review.json()
    assert review_data["verdict"] == "PARTLY_SUPPORTED"
    assert "Dr. Peer Reviewer" in review_data["rationale"]


def test_dashboard_stats_and_activity(client):
    res_stats = client.get("/api/dashboard/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert "total_documents" in stats
    assert "total_claims" in stats
    assert "average_reliability_score" in stats

    res_act = client.get("/api/dashboard/activity?limit=5")
    assert res_act.status_code == 200
    assert isinstance(res_act.json(), list)


def test_settings_get_and_put(client, auth_headers):
    # 1. GET settings
    res = client.get("/api/settings", headers=auth_headers)
    assert res.status_code == 200
    settings_data = res.json()
    assert "auto_flag_outdated_years" in settings_data

    # 2. PUT settings
    update_payload = {
        "preferred_research_provider": "OPENALEX",
        "auto_flag_outdated_years": 7,
        "notify_human_review_needed": False,
    }
    res_update = client.put("/api/settings", json=update_payload, headers=auth_headers)
    assert res_update.status_code == 200
    updated = res_update.json()
    assert updated["preferred_research_provider"] == "OPENALEX"
    assert updated["auto_flag_outdated_years"] == 7
    assert updated["notify_human_review_needed"] is False


@pytest.mark.asyncio
async def test_export_pdf_report(client):
    repo = get_repository()
    doc_id = uuid4()
    claim_id = uuid4()
    now = datetime.now(timezone.utc)

    doc = Document(
        id=doc_id,
        filename="export_target.pdf",
        file_size_bytes=2048,
        mime_type="application/pdf",
        status=ProcessingStatus.COMPLETED,
        pipeline_stage=PipelineStage.DONE,
        page_count=2,
        is_scanned=False,
        error_message=None,
        created_at=now,
        updated_at=now,
    )
    await repo.create_document(doc)

    claim = Claim(
        id=claim_id,
        document_id=doc_id,
        claim_text="Deep residual learning achieves super-human accuracy on ImageNet.",
        page_number=1,
        char_span=[0, 68],
        verdict=VerificationVerdict.SUPPORTED,
        verification_state=VerificationState.VERIFIED,
        confidence=0.95,
        rationale="Retrieved CVPR paper directly supports the ImageNet claim.",
        needs_human_review=False,
    )
    await repo.save_claims([claim])

    report = VerificationReport(
        document_id=doc_id,
        filename=doc.filename,
        generated_at=now,
        total_claims=1,
        reliability_score=95.0,
        verdict_counts={"SUPPORTED": 1, "UNVERIFIED": 0},
        evidence_level_counts={"ABSTRACT_ONLY": 1, "NONE": 0, "FULL_TEXT": 0, "METADATA_ONLY": 0},
        human_review_required_count=0,
        claims=[claim],
    )
    await repo.save_report(report)

    # Test PDF Export endpoint
    res_pdf = client.get(f"/api/documents/{doc_id}/report/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in res_pdf.headers["content-disposition"]
    pdf_bytes = res_pdf.content
    assert pdf_bytes.startswith(b"%PDF-")

    # Verify PDF parseable by PyMuPDF
    parsed_pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    assert parsed_pdf.page_count >= 1
    page1_text = parsed_pdf[0].get_text()
    assert "CiteVerify AI" in page1_text
    assert "Verification Audit Report" in page1_text
    parsed_pdf.close()
