"""
Claim schemas matching contracts/schemas/claim.schema.json.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.enums import VerificationVerdict, VerificationState
from app.schemas.citation import Citation
from app.schemas.evidence import Evidence


class ClaimBase(BaseModel):
    document_id: UUID
    claim_text: str
    page_number: int = Field(..., ge=1)
    char_span: List[int] = Field(..., min_length=2, max_length=2)


class Claim(ClaimBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    citations: List[Citation] = Field(default_factory=list)
    verdict: Optional[VerificationVerdict] = None
    verification_state: VerificationState = VerificationState.PENDING
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    rationale: str = ""
    evidence: List[Evidence] = Field(default_factory=list)
    needs_human_review: bool = False
    review_reasons: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ClaimListResponse(BaseModel):
    items: List[Claim]
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    total: int = Field(default=0, ge=0)


class ClaimPatchRequest(BaseModel):
    claim_text: str = Field(..., min_length=5)
    char_span: List[int] = Field(..., min_length=2, max_length=2)


