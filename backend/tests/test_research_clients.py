"""
Unit tests for scholarly API clients (Crossref, OpenAlex, Europe PMC) and Research Retriever.
Uses mocked HTTP requests for deterministic offline execution.
"""
import pytest
import httpx
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock

from app.integrations.openalex_client import (
    OpenAlexClient,
    reconstruct_abstract_inverted_index,
)
from app.integrations.crossref_client import CrossrefClient
from app.integrations.europe_pmc_client import EuropePMCClient
from app.services.research_retriever import (
    retrieve_publication,
    determine_evidence_level,
    extract_doi_from_text,
)
from app.schemas.enums import RetrievalStatus, EvidenceLevel
from app.schemas.research_paper import ResearchPaper


def test_reconstruct_abstract_inverted_index():
    inverted = {
        "Attention": [0],
        "is": [1],
        "all": [2],
        "you": [3],
        "need.": [4],
    }
    reconstructed = reconstruct_abstract_inverted_index(inverted)
    assert reconstructed == "Attention is all you need."


def test_extract_doi_from_text():
    text1 = "See Vaswani et al. https://doi.org/10.1038/s41586-020-2649-2 for details."
    assert extract_doi_from_text(text1) == "10.1038/s41586-020-2649-2"

    text2 = "No doi here at all in this reference."
    assert extract_doi_from_text(text2) is None


@pytest.mark.asyncio
async def test_crossref_client_doi_lookup_mocked():
    client = CrossrefClient()
    mock_resp = {
        "status": "ok",
        "message": {
            "DOI": "10.1000/182",
            "title": ["A Digital Object Identifier Primer"],
            "author": [{"given": "Norman", "family": "Paskin"}],
            "published-print": {"date-parts": [[2002]]},
            "container-title": ["D-Lib Magazine"],
            "abstract": "<jats:p>An overview of the DOI system.</jats:p>",
        },
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = httpx.Response(200, json=mock_resp)
        paper = await client.get_by_doi("10.1000/182")
        assert paper is not None
        assert paper.doi == "10.1000/182"
        assert paper.title == "A Digital Object Identifier Primer"
        assert "Norman Paskin" in paper.authors
        assert paper.year == 2002
        assert paper.abstract == "An overview of the DOI system."


@pytest.mark.asyncio
async def test_openalex_client_search_mocked():
    client = OpenAlexClient()
    mock_resp = {
        "results": [
            {
                "id": "https://openalex.org/W12345",
                "doi": "https://doi.org/10.1145/3295222.3295349",
                "title": "Attention Is All You Need",
                "publication_year": 2017,
                "authorships": [{"author": {"display_name": "Ashish Vaswani"}}],
                "abstract_inverted_index": {"The": [0], "dominant": [1], "sequence": [2]},
                "open_access": {"is_oa": True, "oa_url": "https://arxiv.org/abs/1706.03762"},
            }
        ]
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = httpx.Response(200, json=mock_resp)
        papers = await client.search("Attention Is All You Need", per_page=1)
        assert len(papers) == 1
        assert papers[0].title == "Attention Is All You Need"
        assert papers[0].year == 2017
        assert papers[0].is_open_access is True
        assert papers[0].abstract == "The dominant sequence"


def test_determine_evidence_level():
    now = datetime.now(timezone.utc)
    p1 = ResearchPaper(
        id=uuid4(),
        title="Test",
        provider="crossref",
        retrieval_status=RetrievalStatus.RETRIEVED,
        match_confidence=1.0,
        match_reason="test",
        retrieved_at=now,
        abstract="A substantial abstract with more than fifty characters of empirical scientific findings.",
    )
    assert determine_evidence_level(p1) == EvidenceLevel.ABSTRACT_ONLY
    assert determine_evidence_level(p1, full_text="Full text content " * 30) == EvidenceLevel.FULL_TEXT

    p2 = ResearchPaper(
        id=uuid4(),
        title="Test",
        provider="crossref",
        retrieval_status=RetrievalStatus.RETRIEVED,
        match_confidence=1.0,
        match_reason="test",
        retrieved_at=now,
        abstract=None,
    )
    assert determine_evidence_level(p2) == EvidenceLevel.METADATA_ONLY
