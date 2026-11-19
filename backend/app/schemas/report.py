"""
Verification report schemas matching contracts/schemas/report.schema.json.
"""
from datetime import datetime
from typing import Dict, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.claim import Claim


class VerificationReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    filename: str
    generated_at: datetime
    total_claims: int = Field(..., ge=0)
    reliability_score: float = Field(..., ge=0.0, le=100.0)
    verdict_counts: Dict[str, int]
    evidence_level_counts: Dict[str, int]
    human_review_required_count: int = Field(..., ge=0)
    claims: List[Claim] = Field(default_factory=list)

