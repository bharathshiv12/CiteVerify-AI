"""
Dashboard metrics and activity feed schemas.
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    total_documents: int = Field(default=0, ge=0)
    total_claims: int = Field(default=0, ge=0)
    supported_claims: int = Field(default=0, ge=0)
    partly_supported_claims: int = Field(default=0, ge=0)
    unsupported_claims: int = Field(default=0, ge=0)
    contradictory_claims: int = Field(default=0, ge=0)
    outdated_claims: int = Field(default=0, ge=0)
    needs_review_claims: int = Field(default=0, ge=0)
    average_reliability_score: float = Field(default=0.0, ge=0.0, le=100.0)


class DashboardActivity(BaseModel):
    id: UUID
    document_id: Optional[UUID] = None
    event_type: str  # "DOCUMENT_UPLOAD", "ANALYSIS_COMPLETED", "HUMAN_REVIEW"
    description: str
    created_at: datetime
