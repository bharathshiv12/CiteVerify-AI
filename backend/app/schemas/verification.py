"""
Verification evaluation schemas matching contracts/schemas/verification.schema.json.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.enums import VerificationVerdict, VerificationState


class Verification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    verification_state: VerificationState
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str
    needs_human_review: bool = False
    review_reasons: List[str] = Field(default_factory=list)
    evaluated_at: datetime
    verdict: Optional[VerificationVerdict] = None
    evidence_summary: Optional[str] = None


class ClaimReviewRequest(BaseModel):
    reviewer_name: str = Field(..., min_length=1)
    updated_verdict: VerificationVerdict
    notes: str = Field(..., min_length=1)

