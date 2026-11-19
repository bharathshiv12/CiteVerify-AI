"""
Service: Evidence Extractor
Owner: Agent 4 & Agent 3 (Research Integration & AI/ML)
Responsibility:
    Retrieves accessible abstract or legitimate open-access full text, chunks text
    into atomic passages, and tags each with its authentic evidence_level.

Inputs:
    - paper (ResearchPaper): The resolved publication record.

Outputs:
    - List[Evidence]: Candidate evidence passages tagged with provenance and evidence_level.
"""
from typing import List
from app.schemas.research_paper import ResearchPaper
from app.schemas.evidence import Evidence


async def extract_candidate_evidence(paper: ResearchPaper) -> List[Evidence]:
    """
    Extracts passages from paper abstract or legitimate open-access text.
    Raises NotImplementedError until implementation is completed.
    """
    raise NotImplementedError("extract_candidate_evidence not implemented yet.")

