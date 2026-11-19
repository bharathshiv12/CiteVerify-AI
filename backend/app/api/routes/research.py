"""
Research discovery routes for querying scholarly repositories.
Resolves Gap 5: Direct user-initiated scholarly searches.
"""
from typing import List, Optional
from fastapi import APIRouter, Query, Depends

from app.core.dependencies import get_optional_user, rate_limit
from app.schemas.research_paper import ResearchPaper
from app.integrations.crossref_client import crossref_client
from app.integrations.openalex_client import openalex_client
from app.integrations.europe_pmc_client import europe_pmc_client
from app.services.research_retriever import retrieve_publication

router = APIRouter(prefix="/research", tags=["Research"])


@router.get("/search", response_model=List[ResearchPaper], summary="Search scholarly publications")
async def search_publications(
    query: str = Query(..., min_length=3, description="Search terms, paper title, or DOI"),
    provider: str = Query("ALL", pattern="^(ALL|OPENALEX|CROSSREF|EUROPE_PMC)$"),
    limit: int = Query(5, ge=1, le=20),
    _limit_check=Depends(rate_limit("research_search", max_requests=60, window_seconds=60)),
):
    """
    Directly queries Crossref, OpenAlex, and Europe PMC for academic publications (Resolves Gap 5).
    """
    prov = provider.upper()
    results: List[ResearchPaper] = []

    if prov in ("ALL", "OPENALEX"):
        openalex_results = await openalex_client.search(query, per_page=limit)
        results.extend(openalex_results)

    if (prov == "CROSSREF" or (prov == "ALL" and len(results) < limit)):
        crossref_results = await crossref_client.search(query, rows=limit)
        results.extend(crossref_results)

    if (prov == "EUROPE_PMC" or (prov == "ALL" and len(results) < limit)):
        epmc_results = await europe_pmc_client.search(query, page_size=limit)
        results.extend(epmc_results)

    # Deduplicate by DOI or normalized title
    deduped: List[ResearchPaper] = []
    seen = set()
    for p in results:
        key = p.doi.lower().strip() if p.doi else p.title.lower().strip()
        if key not in seen:
            seen.add(key)
            deduped.append(p)

    return deduped[:limit]
