"""
Evidence schemas matching contracts/schemas/evidence.schema.json.
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.enums import EvidenceLevel, RetrievalStatus


class Evidence(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_provider: str
    passage: str
    evidence_level: EvidenceLevel
    retrieval_status: RetrievalStatus
    paper_id: Optional[UUID] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    similarity_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    section_name: Optional[str] = None

