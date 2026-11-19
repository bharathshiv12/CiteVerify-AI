import asyncio
import time
import sys
import os
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, os.path.abspath("backend"))

from app.database.repository import get_repository
from app.storage.file_storage import get_file_storage
from app.processors.upload_validator import validate_pdf_content
from app.services.pipeline_orchestrator import run_pipeline
from app.services.report_generator import generate_pdf_report
from app.schemas.document import Document
from app.schemas.enums import ProcessingStatus, PipelineStage

async def test_pdf_e2e(filepath: str, label: str):
    print(f"=== Testing {label} ({filepath}) ===")
    content = Path(filepath).read_bytes()
    validate_pdf_content(Path(filepath).name, content, "application/pdf", 25)
    
    doc_id = uuid4()
    user_id = uuid4()
    storage = get_file_storage()
    await storage.save_file(f"{user_id}/{doc_id}.pdf", content)
    
    repo = get_repository()
    now = datetime.now(timezone.utc)
    doc = Document(
        id=doc_id,
        filename=Path(filepath).name,
        file_size_bytes=len(content),
        mime_type="application/pdf",
        status=ProcessingStatus.PENDING,
        pipeline_stage=PipelineStage.UPLOADED,
        created_at=now,
        updated_at=now,
    )
    await repo.create_document(doc, user_id=user_id)
    
    t_start = time.time()
    processed_doc = await run_pipeline(doc_id, repo)
    t_end = time.time()
    
    print(f"Pipeline Status: {processed_doc.status.value}")
    print(f"Pipeline Stage: {processed_doc.pipeline_stage.value}")
    print(f"Pages: {processed_doc.page_count}, Scanned: {processed_doc.is_scanned}")
    print(f"Total Pipeline Duration: {t_end - t_start:.2f}s")
    
    claims, total_claims = await repo.get_claims_by_document(doc_id, page=1, page_size=100)
    print(f"Extracted Claims: {total_claims}")
    for i, claim in enumerate(claims, 1):
        print(f'  Claim {i}: "{claim.claim_text}"')
        print(f"    Verdict: {claim.verdict.value if claim.verdict else 'null'}")
        print(f"    State: {claim.verification_state.value}")
        print(f"    Confidence: {claim.confidence:.2f}")
        print(f"    Evidence count: {len(claim.evidence)}")
        print(f"    Human Review: {claim.needs_human_review} (reasons: {claim.review_reasons})")
    
    report = await repo.get_report_by_document(doc_id)
    if report:
        print(f"Report generated: Reliability score = {report.reliability_score:.1f}%")
        print(f"Verdict counts: {report.verdict_counts}")
        pdf_bytes = generate_pdf_report(report)
        print(f"Generated PDF Report size: {len(pdf_bytes)} bytes")
    else:
        print("No report generated!")
    print()

async def main():
    await test_pdf_e2e("tests/fixtures/pdf_a_simple.pdf", "PDF A (Simple Paper)")
    await test_pdf_e2e("tests/fixtures/pdf_b_complex.pdf", "PDF B (Complex Paper with Tables)")
    await test_pdf_e2e("tests/fixtures/pdf_c_challenging.pdf", "PDF C (Challenging Document)")

if __name__ == "__main__":
    asyncio.run(main())
