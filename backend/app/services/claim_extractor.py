"""
Service: Claim Extractor
Owner: Agent 3 (AI/ML Engineer)
Responsibility:
    Identifies factual, testable statements in academic paper text that assert
    empirical findings, quantitative measurements, or causal scientific claims.

Inputs:
    - pages (List[dict]): List of {"page_number": int, "text": str}.
    - document_id (UUID): Identifier of containing document.

Outputs:
    - List[Claim]: Extracted claim objects containing claim_text, page_number,
      and char_span coordinates.
"""
from typing import List, Dict, Any
from uuid import UUID
from app.schemas.claim import Claim


def extract_claims(pages: List[Dict[str, Any]], document_id: UUID) -> List[Claim]:
    """
    Extracts citation-worthy factual claims from paper text using LLM / few-shot prompt.
    Raises NotImplementedError until Agent 3 implements claim extraction.
    """
    raise NotImplementedError("extract_claims not implemented yet (Assigned to Agent 3).")

