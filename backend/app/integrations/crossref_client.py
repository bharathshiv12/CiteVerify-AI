"""
Crossref API Integration Client.
Queries Crossref REST API using polite pool User-Agent with retries and timeout protection.
"""
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from uuid import uuid4
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.schemas.research_paper import ResearchPaper
from app.schemas.enums import RetrievalStatus

logger = logging.getLogger("citeverify.integrations.crossref")


class CrossrefClient:
    def __init__(self, base_url: Optional[str] = None, email: Optional[str] = None):
        self.base_url = (base_url or settings.CROSSREF_API_URL).rstrip("/")
        self.email = email or settings.CROSSREF_EMAIL or settings.CONTACT_EMAIL
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
        Fetches paper metadata directly by DOI.
        """
        clean_doi = doi.strip().lower()
        if clean_doi.startswith("http"):
            clean_doi = clean_doi.split("doi.org/")[-1]

        url = f"{self.base_url}/works/{clean_doi}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    item = data.get("message", {})
                    return self._to_research_paper(item, match_confidence=0.98, reason=f"Exact DOI match: {clean_doi}")
                elif resp.status_code == 404:
                    return None
        except Exception as e:
            logger.warning(f"Crossref DOI query error for {clean_doi}: {e}")
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=3.0),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=False,
    )
    async def search(self, query: str, rows: int = 3) -> List[ResearchPaper]:
        """
        Searches Crossref works by bibliographic query string.
        """
        url = f"{self.base_url}/works"
        params = {"query.bibliographic": query, "rows": rows}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("message", {}).get("items", [])
                    papers = []
                    for idx, item in enumerate(items):
                        conf = max(0.90 - (idx * 0.15), 0.50)
                        paper = self._to_research_paper(item, match_confidence=conf, reason="Crossref title/author search")
                        if paper:
                            papers.append(paper)
                    return papers
        except Exception as e:
            logger.warning(f"Crossref search error for '{query}': {e}")
        return []

    def _to_research_paper(self, item: Dict[str, Any], match_confidence: float, reason: str) -> Optional[ResearchPaper]:
        title_list = item.get("title", [])
        title = title_list[0] if title_list else item.get("container-title", ["Untitled"])[0]

        authors = []
        for author in item.get("author", []):
            name = f"{author.get('given', '')} {author.get('family', '')}".strip()
            if name:
                authors.append(name)

        year = None
        date_parts = item.get("published-print", {}).get("date-parts", []) or item.get("published-online", {}).get("date-parts", [])
        if date_parts and date_parts[0]:
            year = date_parts[0][0]

        venue = None
        containers = item.get("container-title", [])
        if containers:
            venue = containers[0]

        doi = item.get("DOI")
        raw_abstract = item.get("abstract", "")
        clean_abstract = re.sub(r"<[^>]+>", "", raw_abstract).strip() if raw_abstract else None

        # Check links for open access URLs
        open_access_url = None
        pdf_url = None
        for link in item.get("link", []):
            ct = link.get("content-type", "")
            url = link.get("URL", "")
            if "pdf" in ct or url.endswith(".pdf"):
                pdf_url = url
            elif not open_access_url:
                open_access_url = url

        return ResearchPaper(
            id=uuid4(),
            doi=doi,
            title=title,
            authors=authors[:10],
            year=year,
            venue=venue,
            abstract=clean_abstract if clean_abstract else None,
            is_open_access=bool(pdf_url or open_access_url),
            open_access_url=open_access_url,
            pdf_url=pdf_url,
            provider="crossref",
            retrieval_status=RetrievalStatus.RETRIEVED,
            match_confidence=match_confidence,
            match_reason=reason,
            retrieved_at=datetime.now(timezone.utc),
        )


crossref_client = CrossrefClient()
