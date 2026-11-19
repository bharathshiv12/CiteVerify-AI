"""
Unit tests for repository implementations, ownership isolation, and cascade deletion.
"""
from uuid import uuid4
from datetime import datetime, timezone
import pytest

from app.repositories.memory_repo import InMemoryRepository
from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.citation import Citation
from app.schemas.enums import ProcessingStatus, PipelineStage, VerificationVerdict


@pytest.mark.asyncio
async def test_repository_crud_and_cascade_delete():
    repo = InMemoryRepository()
    user_a = uuid4()
    user_b = uuid4()
    doc_id = uuid4()
    now = datetime.now(timezone.utc)

    # 1. Create document for user A
    doc = Document(
        id=doc_id,
        filename="manuscript_test.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        status=ProcessingStatus.PENDING,
        pipeline_stage=PipelineStage.UPLOADED,
        created_at=now,
        updated_at=now,
    )
    await repo.create_document(doc, user_id=user_a)

    # 2. List documents with user isolation
    docs_a, total_a = await repo.list_documents(user_id=user_a)
    assert total_a == 1
    assert docs_a[0].id == doc_id

    docs_b, total_b = await repo.list_documents(user_id=user_b)
    assert total_b == 0
    assert len(docs_b) == 0

    # 3. Add claims and citations
    claim_id = uuid4()
    claim = Claim(
        id=claim_id,
        document_id=doc_id,
        claim_text="Transformers improve translation quality.",
        page_number=1,
        char_span=[10, 50],
        verdict=None,
        needs_human_review=True,
    )
    await repo.save_claims([claim])

    citation_id = uuid4()
    citation = Citation(
        id=citation_id,
        document_id=doc_id,
        raw_marker="[1]",
        marker_type="NUMERIC",
        page_number=1,
    )
    await repo.save_citation(citation)

    claims, total_claims = await repo.get_claims_by_document(doc_id)
    assert total_claims == 1
    assert claims[0].id == claim_id

    # 4. Human Review
    updated = await repo.record_human_review(
        claim_id=claim_id,
        reviewer_name="Prof. Sharma",
        updated_verdict=VerificationVerdict.SUPPORTED,
        notes="Validated against paper table 2",
    )
    assert updated.verdict == VerificationVerdict.SUPPORTED
    assert updated.needs_human_review is False

    # 5. Cascade Delete Document
    deleted = await repo.delete_document(doc_id)
    assert deleted is True

    # Document, claim, and citation should be gone
    assert await repo.get_document(doc_id) is None
    assert await repo.get_claim(claim_id) is None
    assert len(await repo.get_citations_by_document(doc_id)) == 0
