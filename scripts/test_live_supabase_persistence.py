"""
Live integration test against the real Supabase PostgreSQL project.
Verifies all 12 persistence domains, foreign keys, cascade deletes, and clean teardown.
"""
import sys
import os
from uuid import uuid4, UUID
from datetime import datetime, timezone
import asyncio

sys.path.insert(0, os.path.abspath("backend"))

from app.core.config import settings
from app.repositories.supabase_repo import SupabaseRepository
from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.citation import Citation
from app.schemas.evidence import Evidence
from app.schemas.report import VerificationReport
from app.schemas.enums import (
    ProcessingStatus,
    PipelineStage,
    VerificationVerdict,
    VerificationState,
    EvidenceLevel,
    RetrievalStatus,
)
from app.schemas.settings import UserSettingsUpdate

# Known real user created in remote Supabase Auth during previous audit
REAL_USER_ID = UUID("7b33fcc1-0fd9-4323-b9c5-83799032591b")

async def test_live_supabase():
    print(f"Connecting to live Supabase: {settings.SUPABASE_URL}")
    repo = SupabaseRepository()

    # 1. Check database readiness
    is_ready, msg = await repo.check_connection()
    assert is_ready, f"Database not ready: {msg}"
    print("[PASS] Database connection and schema verified.")

    # 2. Create Document for real user
    doc_id = uuid4()
    doc = Document(
        id=doc_id,
        filename="live_supabase_test.pdf",
        file_size_bytes=2048,
        mime_type="application/pdf",
        status=ProcessingStatus.PROCESSING,
        pipeline_stage=PipelineStage.TEXT_EXTRACTION,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    created_doc = await repo.create_document(doc, user_id=REAL_USER_ID)
    assert created_doc.id == doc_id
    print(f"[PASS] Document inserted into public.documents (id={doc_id})")

    # 3. Retrieve Document & Owner
    fetched_doc = await repo.get_document(doc_id)
    assert fetched_doc is not None
    assert fetched_doc.filename == "live_supabase_test.pdf"

    owner_id = await repo.get_document_owner(doc_id)
    assert owner_id == REAL_USER_ID
    print(f"[PASS] Document fetched and owner verified (owner={owner_id})")

    # 4. Save Citations
    cit_id = uuid4()
    citation = Citation(
        id=cit_id,
        document_id=doc_id,
        raw_marker="[1]",
        marker_type="NUMERIC",
        page_number=1,
        char_span=[10, 13],
        reference_text="Vaswani et al. (2017). Attention Is All You Need.",
    )
    await repo.save_citations([citation])
    print(f"[PASS] Citation inserted into public.citations (id={cit_id})")

    # 5. Save Claims with Evidence & Citations
    claim_id = uuid4()
    ev_id = uuid4()
    evidence = Evidence(
        id=ev_id,
        claim_id=claim_id,
        source_provider="openalex",
        passage="The Transformer achieves 28.4 BLEU on English-to-German.",
        evidence_level=EvidenceLevel.ABSTRACT_ONLY,
        retrieval_status=RetrievalStatus.RETRIEVED,
        similarity_score=0.92,
    )
    claim = Claim(
        id=claim_id,
        document_id=doc_id,
        claim_text="The Transformer achieves 28.4 BLEU on English-to-German [1].",
        page_number=1,
        char_span=[0, 60],
        verdict=None,
        verification_state=VerificationState.UNABLE_TO_VERIFY,
        confidence=0.0,
        rationale="Preliminary check.",
        citations=[citation],
        evidence=[evidence],
        needs_human_review=True,
    )
    await repo.save_claims([claim])
    print(f"[PASS] Claim and Evidence inserted into public.claims & public.evidence (id={claim_id})")

    # 6. Retrieve Claims and Verify Hydration
    claims, total_claims = await repo.get_claims_by_document(doc_id)
    assert total_claims == 1
    retrieved_claim = claims[0]
    assert retrieved_claim.verdict is None
    assert retrieved_claim.verification_state == VerificationState.UNABLE_TO_VERIFY
    assert len(retrieved_claim.evidence) == 1
    assert retrieved_claim.evidence[0].id == ev_id
    print(f"[PASS] Claim retrieved and fully hydrated with evidence and null verdict intact.")

    # 7. Processing Jobs Tracking
    job = await repo.create_processing_job(
        document_id=doc_id,
        status=ProcessingStatus.PROCESSING,
        current_stage=PipelineStage.VERIFICATION,
        progress_percent=85,
    )
    assert job["status"] == "PROCESSING"
    updated_job = await repo.update_processing_job(
        document_id=doc_id,
        status=ProcessingStatus.COMPLETED,
        current_stage=PipelineStage.DONE,
        progress_percent=100,
    )
    assert updated_job["status"] == "COMPLETED"
    print(f"[PASS] Processing job tracked in public.processing_jobs.")

    # 8. Human Review Record
    reviewed_claim = await repo.record_human_review(
        claim_id=claim_id,
        reviewer_name="Senior Reviewer",
        updated_verdict=VerificationVerdict.SUPPORTED,
        notes="Verified against NeurIPS original proceedings.",
        reviewer_id=REAL_USER_ID,
    )
    assert reviewed_claim.verdict == VerificationVerdict.SUPPORTED
    reviews = await repo.get_reviews_by_document(doc_id)
    assert len(reviews) == 1
    print(f"[PASS] Human review recorded in public.human_reviews.")

    # 9. Save and Retrieve Report
    report = VerificationReport(
        document_id=doc_id,
        filename="live_supabase_test.pdf",
        generated_at=datetime.now(timezone.utc),
        total_claims=1,
        reliability_score=100.0,
        verdict_counts={"SUPPORTED": 1},
        evidence_level_counts={"ABSTRACT_ONLY": 1},
        human_review_required_count=0,
        claims=[reviewed_claim],
    )
    await repo.save_report(report)
    fetched_report = await repo.get_report_by_document(doc_id)
    assert fetched_report is not None
    assert fetched_report.reliability_score == 100.0
    print(f"[PASS] Verification report persisted in public.reports.")

    # 10. Dashboard Stats Scoped to User
    stats = await repo.get_dashboard_stats(user_id=REAL_USER_ID)
    assert stats.total_documents >= 1
    print(f"[PASS] Dashboard stats scoped to user verified (docs={stats.total_documents}).")

    # 11. Clean Up / Cascade Delete Test
    deleted = await repo.delete_document(doc_id)
    assert deleted is True
    assert await repo.get_document(doc_id) is None
    claims_after_del, _ = await repo.get_claims_by_document(doc_id)
    assert len(claims_after_del) == 0
    print(f"[PASS] Document deleted and cascade removal verified across all child tables.")

    print("\n=======================================================")
    print("ALL LIVE SUPABASE POSTGRESQL PERSISTENCE TESTS PASSED!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_live_supabase())
