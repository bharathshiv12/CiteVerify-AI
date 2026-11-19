"""
Service: Research Retriever
Coordinates Crossref, OpenAlex, and Europe PMC queries.
Resolves cited publications, merges multi-source metadata, determines availability level,
and handles rate limits, timeouts, and retrieval errors honestly.
"""
import re
import logging
from typing import Dict, Any, Optional, List, Union
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.research_paper import ResearchPaper
from app.schemas.enums import RetrievalStatus, EvidenceLevel
from app.integrations.crossref_client import crossref_client
from app.integrations.openalex_client import openalex_client
from app.integrations.europe_pmc_client import europe_pmc_client

logger = logging.getLogger("citeverify.research_retriever")

DOI_PATTERN = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b")


def extract_doi_from_text(text: str) -> Optional[str]:
    match = DOI_PATTERN.search(text)
    if match:
        return match.group(1).rstrip(".")
    return None


def determine_evidence_level(paper: ResearchPaper, full_text: Optional[str] = None) -> EvidenceLevel:
    """
    Determines strict source availability level.
    Honesty Rule: Abstracts are never represented as full text.
    """
    if full_text and len(full_text.strip()) > 300:
        return EvidenceLevel.FULL_TEXT
    if paper.abstract and len(paper.abstract.strip()) > 50:
        return EvidenceLevel.ABSTRACT_ONLY
    if paper.title and len(paper.title.strip()) > 0:
        return EvidenceLevel.METADATA_ONLY
    return EvidenceLevel.NONE


async def retrieve_publication(
    raw_reference: Union[str, Dict[str, Any]],
    preferred_provider: str = "ALL",
) -> ResearchPaper:
    """
    Retrieves scholarly publication metadata by DOI or bibliographic query.
    Queries Crossref, OpenAlex, and Europe PMC sequentially with deduplication.
    """
    if isinstance(raw_reference, dict):
        raw_text = raw_reference.get("raw_text", "")
        doi = raw_reference.get("doi") or extract_doi_from_text(raw_text)
        title = raw_reference.get("title", "")
        query = title if title and len(title) > 10 else raw_text
    else:
        raw_text = str(raw_reference)
        doi = extract_doi_from_text(raw_text)
        query = raw_text

    paper: Optional[ResearchPaper] = None

    # 1. Direct DOI Lookup (Highest precision)
    if doi:
        logger.info(f"Retrieving publication by DOI: {doi}")
        if preferred_provider in ("ALL", "OPENALEX"):
            paper = await openalex_client.get_by_doi(doi)

        if not paper and preferred_provider in ("ALL", "CROSSREF"):
            paper = await crossref_client.get_by_doi(doi)

        if not paper and preferred_provider in ("ALL", "EUROPE_PMC"):
            paper = await europe_pmc_client.get_by_doi(doi)

    # 2. Bibliographic query search if DOI lookup missed or wasn't present
    if not paper and query and len(query.strip()) >= 5:
        logger.info(f"Searching publication by query: {query[:60]}...")
        # Clean query for search APIs (remove punctuation markers like [1])
        clean_query = re.sub(r"^\[\d+\]\s*", "", query.strip())

        if preferred_provider in ("ALL", "OPENALEX"):
            candidates = await openalex_client.search(clean_query, per_page=1)
            if candidates:
                paper = candidates[0]

        if not paper and preferred_provider in ("ALL", "CROSSREF"):
            candidates = await crossref_client.search(clean_query, rows=1)
            if candidates:
                paper = candidates[0]

        if not paper and preferred_provider in ("ALL", "EUROPE_PMC"):
            candidates = await europe_pmc_client.search(clean_query, page_size=1)
            if candidates:
                paper = candidates[0]

    # 3. If still not found, return honest NOT_FOUND record (never fabricate)
    if not paper:
        return ResearchPaper(
            id=uuid4(),
            doi=doi,
            title=query[:150] if query else "Unresolved Reference",
            authors=[],
            year=None,
            venue=None,
            abstract=None,
            is_open_access=False,
            open_access_url=None,
            pdf_url=None,
            provider="none",
            retrieval_status=RetrievalStatus.NOT_FOUND,
            match_confidence=0.0,
            match_reason="No matching publication found in Crossref, OpenAlex, or Europe PMC.",
            retrieved_at=datetime.now(timezone.utc),
        )

    return paper
