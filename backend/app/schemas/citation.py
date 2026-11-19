"""
Citation schemas matching contracts/schemas/citation.schema.json.
"""
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class Citation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    raw_marker: str = Field(..., description="In-text marker string like [1] or (Smith, 2020)")
    marker_type: str = Field(..., description="NUMERIC or AUTHOR_YEAR")
    page_number: int = Field(..., ge=1)
    char_span: Optional[List[int]] = Field(default=None, min_length=2, max_length=2)
    reference_text: Optional[str] = None
    reference_index: Optional[int] = None
    matched_paper_id: Optional[UUID] = None

