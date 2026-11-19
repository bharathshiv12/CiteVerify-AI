"""
Service: Evidence Extractor
Responsibility:
    Chunks retrieved abstracts or legitimate open-access full text into atomic
    passages, computes relevance against target claims, and tags every item
    with its authentic evidence_level and retrieval_status.
"""
import re
from typing import List, Optional
from uuid import uuid4

from app.schemas.research_paper import ResearchPaper
from app.schemas.evidence import Evidence
from app.schemas.enums import EvidenceLevel, RetrievalStatus
from app.services.embedding_service import compute_similarities


def split_into_passages(text: str, max_chunk_chars: int = 350) -> List[str]:
    """
    Splits text into coherent atomic passage chunks roughly sentence-aligned.
    """
    clean_text = text.strip()
    if not clean_text:
        return []

    # Split by sentence boundaries (.!? followed by whitespace)
    sentences = re.split(r"(?<=[.!?])\s+", clean_text)
    passages: List[str] = []
    current_chunk: List[str] = []
    current_len = 0

    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue
        if current_len + len(s) > max_chunk_chars and current_chunk:
            passages.append(" ".join(current_chunk))
            current_chunk = [s]
            current_len = len(s)
        else:
            current_chunk.append(s)
            current_len += len(s) + 1

    if current_chunk:
        passages.append(" ".join(current_chunk))

    return passages if passages else [clean_text]


async def extract_candidate_evidence(
    paper: ResearchPaper,
    claim_text: Optional[str] = None,
    full_text: Optional[str] = None,
) -> List[Evidence]:
    """
    Extracts candidate passages from a paper's full text or abstract.
    Tags each passage with authentic evidence_level and calculates semantic relevance
    relative to the claim text if provided.
    """
    evidence_items: List[Evidence] = []

    # 1. Handle unretrieved or paywalled/missing papers honestly
    if paper.retrieval_status != RetrievalStatus.RETRIEVED:
        evidence_items.append(
            Evidence(
                id=uuid4(),
                paper_id=paper.id,
                doi=paper.doi,
                url=paper.open_access_url or paper.pdf_url,
                source_provider=paper.provider,
                passage=paper.match_reason or f"Paper retrieval status: {paper.retrieval_status.value}.",
                evidence_level=EvidenceLevel.NONE,
                retrieval_status=paper.retrieval_status,
                similarity_score=0.0,
                section_name=None,
            )
        )
        return evidence_items

    # 2. Extract from Full Text if available
    if full_text and len(full_text.strip()) > 100:
        raw_passages = split_into_passages(full_text)
        scores = (
            compute_similarities(claim_text, raw_passages)
            if claim_text
            else [0.5] * len(raw_passages)
        )

        for p_text, score in zip(raw_passages, scores):
            evidence_items.append(
                Evidence(
                    id=uuid4(),
                    paper_id=paper.id,
                    doi=paper.doi,
                    url=paper.open_access_url or paper.pdf_url,
                    source_provider=paper.provider,
                    passage=p_text,
                    evidence_level=EvidenceLevel.FULL_TEXT,
                    retrieval_status=RetrievalStatus.RETRIEVED,
                    similarity_score=score,
                    section_name="Open Access Body",
                )
            )

    # 3. Extract from Abstract if available
    elif paper.abstract and len(paper.abstract.strip()) > 30:
        raw_passages = split_into_passages(paper.abstract)
        scores = (
            compute_similarities(claim_text, raw_passages)
            if claim_text
            else [0.5] * len(raw_passages)
        )

        for p_text, score in zip(raw_passages, scores):
            evidence_items.append(
                Evidence(
                    id=uuid4(),
                    paper_id=paper.id,
                    doi=paper.doi,
                    url=paper.open_access_url or paper.pdf_url,
                    source_provider=paper.provider,
                    passage=p_text,
                    evidence_level=EvidenceLevel.ABSTRACT_ONLY,
                    retrieval_status=RetrievalStatus.RETRIEVED,
                    similarity_score=score,
                    section_name="Abstract",
                )
            )

    # 4. Fallback: Metadata Only
    elif paper.title:
        meta_passage = f"Title: {paper.title}."
        if paper.authors:
            meta_passage += f" Authors: {', '.join(paper.authors[:5])}."
        if paper.year:
            meta_passage += f" Year: {paper.year}."
        if paper.venue:
            meta_passage += f" Published in: {paper.venue}."

        score = compute_similarities(claim_text, [meta_passage])[0] if claim_text else 0.2
        evidence_items.append(
            Evidence(
                id=uuid4(),
                paper_id=paper.id,
                doi=paper.doi,
                url=paper.open_access_url or paper.pdf_url,
                source_provider=paper.provider,
                passage=meta_passage,
                evidence_level=EvidenceLevel.METADATA_ONLY,
                retrieval_status=RetrievalStatus.RETRIEVED,
                similarity_score=score,
                section_name="Bibliographic Metadata",
            )
        )

    # 5. Empty record fallback
    else:
        evidence_items.append(
            Evidence(
                id=uuid4(),
                paper_id=paper.id,
                doi=paper.doi,
                url=paper.open_access_url or paper.pdf_url,
                source_provider=paper.provider,
                passage="No text content or metadata available for this publication.",
                evidence_level=EvidenceLevel.NONE,
                retrieval_status=RetrievalStatus.NOT_FOUND,
                similarity_score=0.0,
                section_name=None,
            )
        )

    # Sort passages by similarity score descending
    evidence_items.sort(key=lambda ev: ev.similarity_score or 0.0, reverse=True)
    return evidence_items
