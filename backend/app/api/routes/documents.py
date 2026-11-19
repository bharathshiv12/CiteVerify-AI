"""
Document routes handling upload, listing, extraction, analysis, status, claims, reports, and deletion.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, status, Query, Depends, Response
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import NotFoundError, ConflictError
from app.core.dependencies import get_optional_user, verify_document_access
from app.database.repository import AbstractRepository, get_repository
from app.storage.file_storage import get_file_storage
from app.processors.upload_validator import validate_pdf_content
from app.services.document_processor import extract_text_from_pdf, PDFProcessingError
from app.services.pipeline_orchestrator import run_pipeline
from app.schemas.document import (
    Document,
    DocumentStatusResponse,
    DocumentAnalyzeResponse,
)
from app.schemas.enums import ProcessingStatus, PipelineStage, VerificationVerdict
from app.schemas.claim import ClaimListResponse
from app.schemas.report import VerificationReport
from app.schemas.common import PaginatedResponse
from app.schemas.user import User

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    user: Optional[User] = Depends(get_optional_user),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Accepts, validates, and stages an academic PDF document into storage.
    Enforces MIME check, %PDF- magic bytes, and size caps.
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
    user_id_str = str(user.id) if user else "anonymous"

    # Store file via storage interface
    storage = get_file_storage()
    relative_path = f"{user_id_str}/{doc_id}.pdf"
    await storage.save_file(relative_path, content)

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
    await repo.create_document(doc, user_id=user.id if user else None)
    return doc


@router.get("", response_model=PaginatedResponse[Document], summary="List user documents")
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: Optional[User] = Depends(get_optional_user),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Lists documents uploaded by the user with pagination (Resolves Gap 1).
    """
    user_id = user.id if user else None
    items, total = await repo.list_documents(user_id=user_id, page=page, page_size=page_size)
    return PaginatedResponse[Document](
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{document_id}", response_model=Document, summary="Get document details")
async def get_document(
    document: Document = Depends(verify_document_access),
):
    """
    Retrieves document metadata by ID with ownership verification.
    """
    return document


@router.post("/{document_id}/extract", summary="Extract text and detect scanned status")
async def extract_document(
    document: Document = Depends(verify_document_access),
    user: Optional[User] = Depends(get_optional_user),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Extracts text per page using PyMuPDF and checks whether the PDF is scanned.
    """
    storage = get_file_storage()
    user_id_str = str(user.id) if user else "anonymous"
    rel_path = f"{user_id_str}/{document.id}.pdf"

    if not await storage.file_exists(rel_path):
        rel_path = f"anonymous/{document.id}.pdf"

    try:
        content = await storage.get_file(rel_path)
    except FileNotFoundError:
        raise NotFoundError("Stored PDF file", str(document.id))

    try:
        extraction = extract_text_from_pdf(content, document.id)
    except PDFProcessingError as e:
        document.status = ProcessingStatus.FAILED
        document.error_message = e.message
        await repo.update_document(document)
        return JSONResponse(status_code=400, content={"error": {"code": e.code, "message": e.message}})

    # Update document record with extraction results
    document.page_count = extraction["page_count"]
    document.is_scanned = extraction["is_scanned"]
    document.pipeline_stage = PipelineStage.TEXT_EXTRACTION
    document.updated_at = datetime.now(timezone.utc)
    await repo.update_document(document)

    return {
        "document_id": str(document.id),
        "page_count": extraction["page_count"],
        "is_scanned": extraction["is_scanned"],
        "pages": extraction["pages"],
        "total_char_count": extraction["total_char_count"],
    }


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete document and stored file")
async def delete_document(
    document_id: UUID,
    user: Optional[User] = Depends(get_optional_user),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Permanently deletes a document, its database cascade records, and its stored binary (Resolves Gap 2).
    """
    doc = await repo.get_document(document_id)
    if not doc:
        raise NotFoundError(resource="Document", identifier=str(document_id))

    # Verify ownership
    if hasattr(repo, "document_owners"):
        owner_id = repo.document_owners.get(doc.id)
        if owner_id and (not user or user.id != owner_id):
            raise NotFoundError(resource="Document", identifier=str(document_id))

    # Delete storage binary
    storage = get_file_storage()
    for user_prefix in [str(user.id) if user else None, "anonymous"]:
        if user_prefix:
            await storage.delete_file(f"{user_prefix}/{document_id}.pdf")

    # Delete repository cascade
    await repo.delete_document(document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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

    background_tasks.add_task(run_pipeline, document_id, repo)

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

    # 11-stage progress percentage calculation
    progress_map = {
        PipelineStage.UPLOADED: 5,
        PipelineStage.TEXT_EXTRACTION: 15,
        PipelineStage.CLAIM_EXTRACTION: 25,
        PipelineStage.CITATION_PARSING: 35,
        PipelineStage.REFERENCE_PARSING: 45,
        PipelineStage.CITATION_MATCHING: 55,
        PipelineStage.PAPER_RETRIEVAL: 70,
        PipelineStage.EVIDENCE_EXTRACTION: 80,
        PipelineStage.VERIFICATION: 90,
        PipelineStage.REPORT_GENERATION: 95,
        PipelineStage.DONE: 100,
    }
    progress = progress_map.get(doc.pipeline_stage, 0)
    if doc.status == ProcessingStatus.COMPLETED:
        progress = 100

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

    report = await repo.get_report_by_document(document_id)
    if report:
        return report

    # Synthesize fallback report from claims if report record not yet written
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
