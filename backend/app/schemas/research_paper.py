"""
Research paper schemas matching contracts/schemas/research_paper.schema.json.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.enums import RetrievalStatus


class ResearchPaper(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    provider: str = Field(..., description="crossref, openalex, europe_pmc")
    retrieval_status: RetrievalStatus = RetrievalStatus.RETRIEVED
    match_confidence: float = Field(..., ge=0.0, le=1.0)
    retrieved_at: datetime
    doi: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    abstract: Optional[str] = None
    is_open_access: bool = False
    open_access_url: Optional[str] = None
    pdf_url: Optional[str] = None
    match_reason: Optional[str] = None

