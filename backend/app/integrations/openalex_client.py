"""
OpenAlex API Integration Client.
Queries OpenAlex REST API with inverted index abstract reconstruction and open-access PDF resolution.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from uuid import uuid4
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.schemas.research_paper import ResearchPaper
from app.schemas.enums import RetrievalStatus

logger = logging.getLogger("citeverify.integrations.openalex")


def reconstruct_abstract_inverted_index(inverted_index: Optional[Dict[str, List[int]]]) -> Optional[str]:
    """
    Reconstructs full linear abstract text from OpenAlex inverted index structure.
    """
    if not inverted_index:
        return None

    pos_to_word: Dict[int, str] = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            pos_to_word[pos] = word

    if not pos_to_word:
        return None

    sorted_positions = sorted(pos_to_word.keys())
    return " ".join(pos_to_word[pos] for pos in sorted_positions)


class OpenAlexClient:
    def __init__(self, base_url: Optional[str] = None, email: Optional[str] = None):
        self.base_url = (base_url or settings.OPENALEX_API_URL).rstrip("/")
        self.email = email or settings.OPENALEX_EMAIL or settings.CONTACT_EMAIL
        self.headers = {
            "User-Agent": f"CiteVerify/1.0 (mailto:{self.email})",
            "Accept": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=3.0),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=False,
    )
    async def get_by_doi(self, doi: str) -> Optional[ResearchPaper]:
        """
        Fetches paper metadata directly by DOI from OpenAlex works endpoint.
        """
        clean_doi = doi.strip().lower()
        if not clean_doi.startswith("http"):
            clean_doi = f"https://doi.org/{clean_doi}"

        url = f"{self.base_url}/works/{clean_doi}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return self._to_research_paper(data, match_confidence=0.99, reason=f"Exact OpenAlex DOI match: {doi}")
                elif resp.status_code == 404:
                    return None
        except Exception as e:
            logger.warning(f"OpenAlex DOI query error for {doi}: {e}")
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=3.0),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=False,
    )
    async def search(self, query: str, per_page: int = 3) -> List[ResearchPaper]:
        """
        Searches OpenAlex works by natural language query string.
        """
        url = f"{self.base_url}/works"
        params = {"search": query, "per_page": per_page, "mailto": self.email}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    papers = []
                    for idx, item in enumerate(results):
                        conf = max(0.92 - (idx * 0.12), 0.50)
                        paper = self._to_research_paper(item, match_confidence=conf, reason="OpenAlex semantic search")
                        if paper:
                            papers.append(paper)
                    return papers
        except Exception as e:
            logger.warning(f"OpenAlex search error for '{query}': {e}")
        return []

    def _to_research_paper(self, item: Dict[str, Any], match_confidence: float, reason: str) -> Optional[ResearchPaper]:
        title = item.get("title") or item.get("display_name") or "Untitled"

        authors = []
        for authorship in item.get("authorships", []):
            author_obj = authorship.get("author", {})
            name = author_obj.get("display_name")
            if name:
                authors.append(name)

        year = item.get("publication_year")

        venue = None
        primary_loc = item.get("primary_location") or {}
        source = primary_loc.get("source") or {}
        if source:
            venue = source.get("display_name")

        raw_doi = item.get("doi")
        clean_doi = raw_doi.split("doi.org/")[-1] if raw_doi else None

        inverted_abstract = item.get("abstract_inverted_index")
        abstract = reconstruct_abstract_inverted_index(inverted_abstract)

        open_access = item.get("open_access", {}) or {}
        is_oa = open_access.get("is_oa", False)
        oa_url = open_access.get("oa_url")

        best_loc = item.get("best_oa_location") or {}
        pdf_url = best_loc.get("pdf_url")

        return ResearchPaper(
            id=uuid4(),
            doi=clean_doi,
            title=title,
            authors=authors[:10],
            year=year,
            venue=venue,
            abstract=abstract,
            is_open_access=bool(is_oa or pdf_url or oa_url),
            open_access_url=oa_url,
            pdf_url=pdf_url,
            provider="openalex",
            retrieval_status=RetrievalStatus.RETRIEVED,
            match_confidence=match_confidence,
            match_reason=reason,
            retrieved_at=datetime.now(timezone.utc),
        )


openalex_client = OpenAlexClient()
