"""
Document schemas matching contracts/schemas/document.schema.json.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.enums import ProcessingStatus, PipelineStage


class DocumentBase(BaseModel):
    filename: str
    file_size_bytes: int = Field(..., ge=1)
    mime_type: str = "application/pdf"


class Document(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ProcessingStatus = ProcessingStatus.PENDING
    pipeline_stage: PipelineStage = PipelineStage.UPLOADED
    page_count: Optional[int] = None
    is_scanned: bool = False
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DocumentStatusResponse(BaseModel):
    document_id: UUID
    status: ProcessingStatus
    pipeline_stage: PipelineStage
    progress_percent: int = Field(..., ge=0, le=100)
    total_claims_found: int = Field(default=0, ge=0)
    verified_claims_count: int = Field(default=0, ge=0)
    error_message: Optional[str] = None


class DocumentAnalyzeResponse(BaseModel):
    document_id: UUID
    status: ProcessingStatus
    pipeline_stage: PipelineStage
    message: str

