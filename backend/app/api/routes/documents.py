"""
Document routes handling upload, analysis scheduling, status, claims, and final reports.
"""
import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, status, Query, Depends
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.core.errors import NotFoundError, ConflictError
from app.database.repository import AbstractRepository, get_repository
from app.processors.upload_validator import validate_pdf_content
from app.schemas.document import (
    Document,
    DocumentStatusResponse,
    DocumentAnalyzeResponse,
)
from app.schemas.enums import ProcessingStatus, PipelineStage, VerificationVerdict
from app.schemas.claim import ClaimListResponse
from app.schemas.report import VerificationReport

router = APIRouter(prefix="/documents", tags=["Documents"])


async def dummy_pipeline_runner(document_id: UUID, repo: AbstractRepository):
    """
    Background worker stub for orchestrating pipeline stages.
    """
    doc = await repo.get_document(document_id)
    if not doc:
        return
    # Mark in progress
    doc.status = ProcessingStatus.PROCESSING
    doc.pipeline_stage = PipelineStage.TEXT_EXTRACTION
    doc.updated_at = datetime.now(timezone.utc)
    await repo.update_document(doc)


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Accepts, validates, and stages an academic PDF document.
    """
    content = await file.read()
    validate_pdf_content(
        filename=file.filename or "unknown.pdf",
        content=content,
        content_type=file.content_type or "application/octet-stream",
        max_size_mb=settings.MAX_UPLOAD_SIZE_MB,
    )

    doc_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # Save to disk
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}.pdf")
    with open(saved_path, "wb") as f:
        f.write(content)

    doc = Document(
        id=doc_id,
        filename=file.filename or "uploaded.pdf",
        file_size_bytes=len(content),
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
    return doc


@router.post(
    "/{document_id}/analyze",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=DocumentAnalyzeResponse,
)
async def analyze_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Initiates asynchronous verification pipeline in background tasks.
    """
    doc = await repo.get_document(document_id)
    if not doc:
        raise NotFoundError(resource="Document", identifier=str(document_id))

    if doc.status == ProcessingStatus.PROCESSING:
        raise ConflictError(message="Document is already actively being processed.")

    background_tasks.add_task(dummy_pipeline_runner, document_id, repo)

    return DocumentAnalyzeResponse(
        document_id=doc.id,
        status=ProcessingStatus.PROCESSING,
        pipeline_stage=PipelineStage.TEXT_EXTRACTION,
        message="Document analysis pipeline started in background.",
    )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: UUID,
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Returns current status and pipeline progress.
    """
    doc = await repo.get_document(document_id)
    if not doc:
        raise NotFoundError(resource="Document", identifier=str(document_id))

    claims, total_claims = await repo.get_claims_by_document(document_id, page=1, page_size=1)
    verified_count = sum(1 for c in claims if c.verdict is not None)

    # Simple stage progress calculation
    progress_map = {
        PipelineStage.UPLOADED: 5,
        PipelineStage.TEXT_EXTRACTION: 15,
        PipelineStage.CLAIM_EXTRACTION: 30,
        PipelineStage.CITATION_PARSING: 40,
        PipelineStage.REFERENCE_PARSING: 50,
        PipelineStage.CITATION_MATCHING: 60,
        PipelineStage.PAPER_RETRIEVAL: 70,
        PipelineStage.EVIDENCE_EXTRACTION: 80,
        PipelineStage.VERIFICATION: 90,
        PipelineStage.REPORT_GENERATION: 95,
        PipelineStage.DONE: 100,
    }
    progress = progress_map.get(doc.pipeline_stage, 0)

    return DocumentStatusResponse(
        document_id=doc.id,
        status=doc.status,
        pipeline_stage=doc.pipeline_stage,
        progress_percent=progress,
        total_claims_found=total_claims,
        verified_claims_count=verified_count,
        error_message=doc.error_message,
    )


@router.get("/{document_id}/claims", response_model=ClaimListResponse)
async def get_document_claims(
    document_id: UUID,
    verdict: Optional[VerificationVerdict] = Query(None),
    needs_review: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Returns paginated claims for a document with optional verdict and review filtering.
    """
    doc = await repo.get_document(document_id)
    if not doc:
        raise NotFoundError(resource="Document", identifier=str(document_id))

    items, total = await repo.get_claims_by_document(
        document_id=document_id,
        verdict=verdict,
        needs_review=needs_review,
        page=page,
        page_size=page_size,
    )
    return ClaimListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{document_id}/report", response_model=VerificationReport)
async def get_document_report(
    document_id: UUID,
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Returns the final synthesized verification report.
    Returns 409 Conflict if analysis is not yet completed.
    """
    doc = await repo.get_document(document_id)
    if not doc:
        raise NotFoundError(resource="Document", identifier=str(document_id))

    if doc.status != ProcessingStatus.COMPLETED:
        raise ConflictError(
            message=f"Document analysis is not completed yet (current status: {doc.status.value}).",
            details={"document_id": str(document_id), "status": doc.status.value},
        )

    claims, total = await repo.get_claims_by_document(document_id, page=1, page_size=1000)
    verdict_counts = {v.value: 0 for v in VerificationVerdict}
    verdict_counts["UNVERIFIED"] = 0
    for c in claims:
        if c.verdict:
            verdict_counts[c.verdict.value] += 1
        else:
            verdict_counts["UNVERIFIED"] += 1

    return VerificationReport(
        document_id=doc.id,
        filename=doc.filename,
        generated_at=datetime.now(timezone.utc),
        total_claims=total,
        reliability_score=100.0 if total == 0 else 0.0,
        verdict_counts=verdict_counts,
        evidence_level_counts={"FULL_TEXT": 0, "ABSTRACT_ONLY": 0, "METADATA_ONLY": 0, "NONE": 0},
        human_review_required_count=sum(1 for c in claims if c.needs_human_review),
        claims=claims,
    )

