"""
Unit tests for Citation Parser, Bibliography Extractor, Claim Extractor, and Citation Matcher.
"""
from uuid import uuid4
import pytest

from app.services.citation_parser import (
    parse_in_text_citations,
    parse_bibliography_references,
    expand_numeric_range,
    parse_citations_and_references,
)
from app.services.claim_extractor import extract_claims, is_empirical_claim
from app.services.citation_matcher import match_claims_to_citations


def test_expand_numeric_range():
    assert expand_numeric_range("[1]") == [1]
    assert expand_numeric_range("[1, 3]") == [1, 3]
    assert expand_numeric_range("[1-4]") == [1, 2, 3, 4]
    assert expand_numeric_range("[1, 3-5, 8]") == [1, 3, 4, 5, 8]


def test_parse_in_text_citations():
    doc_id = uuid4()
    pages = [
        {
            "page_number": 1,
            "text": "Recent advances demonstrate superior translation quality [1]. Other studies confirm this (Vaswani et al., 2017). Multi-citations [2-4] also agree.",
        }
    ]

    citations = parse_in_text_citations(pages, doc_id)
    assert len(citations) >= 3
    numeric_cits = [c for c in citations if c.marker_type == "NUMERIC"]
    author_cits = [c for c in citations if c.marker_type == "AUTHOR_YEAR"]

    assert any(c.raw_marker == "[1]" and c.reference_index == 1 for c in numeric_cits)
    assert any("[2-4]" in c.raw_marker for c in numeric_cits)
    assert any("Vaswani" in c.raw_marker for c in author_cits)


def test_parse_bibliography_references():
    pages = [
        {
            "page_number": 1,
            "text": "Some introduction text [1].",
        },
        {
            "page_number": 2,
            "text": """
References
1. Vaswani, A., Shazeer, N., Parmar, N. Attention is all you need. NeurIPS, 2017. https://doi.org/10.5555/3295222.3295349
2. Devlin, J. et al. BERT: Pre-training of deep bidirectional transformers. NAACL, 2019. doi:10.18653/v1/N19-1423
            """,
        },
    ]

    refs = parse_bibliography_references(pages)
    assert "1" in refs
    assert "2" in refs
    assert "Vaswani" in refs["1"]["raw_text"]
    assert refs["1"]["year"] == 2017
    assert "10.5555/3295222.3295349" in refs["1"]["doi"] or "10.5555" in refs["1"]["raw_text"]
    assert "10.18653/v1/N19-1423" in refs["2"]["doi"]


def test_claim_extractor_identifies_empirical_findings():
    doc_id = uuid4()
    pages = [
        {
            "page_number": 1,
            "text": "Transformers achieve a 28.4 BLEU score on English-to-German translation [1]. We observed that latency decreased by 14% compared to RNN baselines.",
        }
    ]

    claims = extract_claims(pages, doc_id)
    assert len(claims) >= 1
    texts = " ".join(c.claim_text for c in claims)
    assert "28.4 BLEU" in texts or "latency decreased" in texts


def test_match_claims_to_citations():
    doc_id = uuid4()
    pages = [
        {
            "page_number": 1,
            "text": "Transformers achieve state-of-the-art BLEU score of 28.4 [1]. Earlier models were slower.",
        },
        {
            "page_number": 2,
            "text": "References\n1. Vaswani, A. et al. Attention is all you need. 2017.",
        },
    ]

    citations, references = parse_citations_and_references(pages, doc_id)
    claims = extract_claims(pages, doc_id, all_citations=citations)
    matched = match_claims_to_citations(claims, citations, references)

    # First claim should have citation [1] attached
    assert len(matched) >= 1
    assert len(matched[0].citations) >= 1
    attached = matched[0].citations[0]
    assert attached.raw_marker == "[1]"
    assert attached.reference_text is not None
    assert "Vaswani" in attached.reference_text
