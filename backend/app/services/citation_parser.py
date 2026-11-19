"""
Service: Citation Parser
Owner: Agent 2 (Backend Developer)
Responsibility:
    Parses numeric citation markers (e.g. [1], [1,3], [1-4]) and author-year markers
    (e.g. Smith et al., 2020) from paper text, and parses the bibliography/references section.

Inputs:
    - pages (List[dict]): List of {"page_number": int, "text": str}.
    - document_id (UUID): Identifier of containing document.

Outputs:
    - Tuple[List[Citation], Dict[str, str]]:
        - citations: In-text citation markers found with page & char spans.
        - references: Map of reference keys to parsed bibliographic strings.
"""
from typing import List, Dict, Tuple, Any
from uuid import UUID
from app.schemas.citation import Citation


def parse_citations_and_references(
    pages: List[Dict[str, Any]],
    document_id: UUID,
) -> Tuple[List[Citation], Dict[str, str]]:
    """
    Detects in-text citation markers and extracts the bibliography section.
    Raises NotImplementedError until Agent 2 implements parsing logic.
    """
    raise NotImplementedError("parse_citations_and_references not implemented yet (Assigned to Agent 2).")

