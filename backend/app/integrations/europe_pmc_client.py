"""
Europe PMC API Integration Client.
Queries Europe PMC REST API for biomedical research metadata, abstracts, and open-access full text.
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

logger = logging.getLogger("citeverify.integrations.europe_pmc")


class EuropePMCClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.EUROPE_PMC_API_URL).rstrip("/")
        self.headers = {
            "User-Agent": "CiteVerify/1.0 (Academic Verification Engine)",
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
        Fetches paper metadata directly by DOI from Europe PMC search.
        """
        clean_doi = doi.strip().lower()
        if clean_doi.startswith("http"):
            clean_doi = clean_doi.split("doi.org/")[-1]

        query = f'DOI:"{clean_doi}"'
        url = f"{self.base_url}/search"
        params = {"query": query, "format": "json", "resultType": "core", "pageSize": 1}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("resultList", {}).get("result", [])
                    if results:
                        return self._to_research_paper(results[0], match_confidence=0.98, reason=f"Exact Europe PMC DOI match: {clean_doi}")
        except Exception as e:
            logger.warning(f"Europe PMC DOI query error for {clean_doi}: {e}")
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=3.0),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=False,
    )
    async def search(self, query: str, page_size: int = 3) -> List[ResearchPaper]:
        """
        Searches Europe PMC works by query terms.
        """
        url = f"{self.base_url}/search"
        params = {"query": query, "format": "json", "resultType": "core", "pageSize": page_size}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("resultList", {}).get("result", [])
                    papers = []
                    for idx, item in enumerate(results):
                        conf = max(0.90 - (idx * 0.15), 0.50)
                        paper = self._to_research_paper(item, match_confidence=conf, reason="Europe PMC keyword search")
                        if paper:
                            papers.append(paper)
                    return papers
        except Exception as e:
            logger.warning(f"Europe PMC search error for '{query}': {e}")
        return []

    async def get_open_access_full_text(self, pmcid: str) -> Optional[str]:
        """
        Attempts to fetch full text XML for legally open-access publications in Europe PMC.
        Never accesses paywalled content.
        """
        clean_pmcid = pmcid.strip()
        if not clean_pmcid.startswith("PMC"):
            clean_pmcid = f"PMC{clean_pmcid}"

        url = f"{self.base_url}/{clean_pmcid}/fullTextXML"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers={"Accept": "application/xml"})
                if resp.status_code == 200:
                    raw_xml = resp.text
                    # Strip tags to get readable body text
                    text = re.sub(r"<[^>]+>", " ", raw_xml)
                    clean_text = re.sub(r"\s+", " ", text).strip()
                    return clean_text if len(clean_text) > 200 else None
        except Exception as e:
            logger.debug(f"Could not retrieve full text XML for {clean_pmcid}: {e}")
        return None

    def _to_research_paper(self, item: Dict[str, Any], match_confidence: float, reason: str) -> Optional[ResearchPaper]:
        title = item.get("title", "Untitled").rstrip(".")

        authors = []
        author_str = item.get("authorString", "")
        if author_str:
            authors = [a.strip() for a in author_str.split(",") if a.strip()]

        year = None
        pub_year = item.get("pubYear")
        if pub_year and pub_year.isdigit():
            year = int(pub_year)

        venue = item.get("journalTitle")
        doi = item.get("doi")
        abstract = item.get("abstractText")
        if abstract:
            abstract = re.sub(r"<[^>]+>", "", abstract).strip()

        is_oa = item.get("isOpenAccess", "N") == "Y"
        pmcid = item.get("pmcid")
        oa_url = f"https://europepmc.org/article/PMC/{pmcid}" if pmcid else None
        pdf_url = f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmcid}&blobtype=pdf" if (pmcid and is_oa) else None

        return ResearchPaper(
            id=uuid4(),
            doi=doi,
            title=title,
            authors=authors[:10],
            year=year,
            venue=venue,
            abstract=abstract if abstract else None,
            is_open_access=is_oa,
            open_access_url=oa_url,
            pdf_url=pdf_url,
            provider="europe_pmc",
            retrieval_status=RetrievalStatus.RETRIEVED,
            match_confidence=match_confidence,
            match_reason=reason,
            retrieved_at=datetime.now(timezone.utc),
        )


europe_pmc_client = EuropePMCClient()
