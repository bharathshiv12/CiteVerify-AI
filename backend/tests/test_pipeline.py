"""
End-to-end integration tests for the 11-stage verification pipeline orchestrator.
"""
import io
import pytest
import fitz
from datetime import datetime, timezone
from uuid import uuid4

from app.database.repository import get_repository
from app.storage.file_storage import get_file_storage
from app.schemas.document import Document
from app.schemas.enums import ProcessingStatus, PipelineStage
from app.services.pipeline_orchestrator import run_pipeline


def create_sample_paper_pdf() -> bytes:
    doc = fitz.open()
    page1 = doc.new_page()
    text = (
        "Deep Learning in Medical Imaging\n\n"
        "Introduction\n"
        "Recent empirical evaluations show that deep convolutional neural networks achieve 95% accuracy "
        "on clinical radiological image benchmarks [1]. "
        "Furthermore, transformer architectures enhance diagnostic reproducibility across patient cohorts [2].\n\n"
        "References\n"
        "[1] He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep Residual Learning for Image Recognition. "
        "IEEE CVPR. doi:10.1109/CVPR.2016.90\n"
        "[2] Vaswani, A., et al. (2017). Attention is All You Need. NeurIPS. doi:10.48550/arXiv.1706.03762\n"
    )
    page1.insert_text((50, 72), text, fontsize=11)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


@pytest.mark.asyncio
async def test_full_pipeline_orchestration():
    repo = get_repository()
    storage = get_file_storage()

    doc_id = uuid4()
    pdf_bytes = create_sample_paper_pdf()

    # Save to storage
    rel_path = f"anonymous/{doc_id}.pdf"
    await storage.save_file(rel_path, pdf_bytes)

    now = datetime.now(timezone.utc)
    doc = Document(
        id=doc_id,
        filename="medical_imaging.pdf",
        file_size_bytes=len(pdf_bytes),
        mime_type="application/pdf",
        status=ProcessingStatus.PENDING,
        pipeline_stage=PipelineStage.UPLOADED,
        page_count=None,
        is_scanned=False,
        error_message=None,
        created_at=now,
        updated_at=now,
    )
    await repo.create_document(doc)

    # Execute pipeline orchestrator
    completed_doc = await run_pipeline(doc_id, repo)

    assert completed_doc is not None
    assert completed_doc.status == ProcessingStatus.COMPLETED
    assert completed_doc.pipeline_stage == PipelineStage.DONE
    assert completed_doc.page_count == 1
    assert completed_doc.error_message is None

    # Check extracted claims
    claims, total_claims = await repo.get_claims_by_document(doc_id)
    assert total_claims >= 1
    first_claim = claims[0]
    assert len(first_claim.claim_text) > 10

    # Check parsed citations
    citations = await repo.get_citations_by_document(doc_id)
    assert len(citations) >= 1
    assert any("[1]" in c.raw_marker for c in citations)

    # Check report was generated
    report = await repo.get_report_by_document(doc_id)
    assert report is not None
    assert report.document_id == doc_id
    assert report.total_claims == total_claims
    assert 0.0 <= report.reliability_score <= 100.0
    assert "SUPPORTED" in report.verdict_counts
