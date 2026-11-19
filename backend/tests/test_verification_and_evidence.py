"""
Tests for evidence extraction, embedding similarities, and verification engine logic.
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.research_paper import ResearchPaper
from app.schemas.evidence import Evidence
from app.schemas.enums import EvidenceLevel, RetrievalStatus, VerificationVerdict, VerificationState
from app.services.embedding_service import compute_similarities
from app.services.evidence_extractor import extract_candidate_evidence, split_into_passages
from app.services.verification_engine import verify_claim_against_evidence


def test_split_into_passages():
    text = "First sentence here. Second sentence follows. Third sentence concludes the thought."
    passages = split_into_passages(text, max_chunk_chars=40)
    assert len(passages) >= 2
    assert "First sentence here." in passages[0]


def test_compute_similarities_tfidf():
    query = "Deep learning achieves 95% accuracy on medical image classification."
    passages = [
        "We demonstrate that deep learning achieves 95% accuracy on clinical medical image analysis.",
        "A study on agricultural crop rotation and soil nitrogen fixation.",
        "Deep convolutional neural networks are commonly used in computer vision.",
    ]
    scores = compute_similarities(query, passages)
    assert len(scores) == 3
    # First passage should have the highest score due to token and numeric overlap
    assert scores[0] > scores[1]
    assert scores[0] > scores[2]
    assert all(0.0 <= s <= 1.0 for s in scores)


@pytest.mark.asyncio
async def test_extract_candidate_evidence_from_abstract():
    paper = ResearchPaper(
        id=uuid4(),
        doi="10.1038/s41586-020-2649-2",
        title="Language Models are Few-Shot Learners",
        authors=["Brown, T.", "Mann, B."],
        year=2020,
        venue="NeurIPS",
        abstract="Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task.",
        is_open_access=True,
        open_access_url="https://arxiv.org/abs/2005.14165",
        pdf_url=None,
        provider="openalex",
        retrieval_status=RetrievalStatus.RETRIEVED,
        match_confidence=1.0,
        retrieved_at=datetime.now(timezone.utc),
    )
    claim = "Pre-training language models on large corpora improves NLP benchmark performance."
    evidence_list = await extract_candidate_evidence(paper, claim_text=claim)

    assert len(evidence_list) >= 1
    assert evidence_list[0].evidence_level == EvidenceLevel.ABSTRACT_ONLY
    assert evidence_list[0].retrieval_status == RetrievalStatus.RETRIEVED
    assert evidence_list[0].similarity_score is not None
    assert evidence_list[0].paper_id == paper.id


@pytest.mark.asyncio
async def test_extract_candidate_evidence_unretrieved_honesty():
    paper = ResearchPaper(
        id=uuid4(),
        doi="10.1000/182",
        title="Missing Study",
        authors=[],
        year=None,
        venue=None,
        abstract=None,
        is_open_access=False,
        provider="none",
        retrieval_status=RetrievalStatus.NOT_FOUND,
        match_confidence=0.0,
        match_reason="Paper not found in scholarly indexes.",
        retrieved_at=datetime.now(timezone.utc),
    )
    evidence_list = await extract_candidate_evidence(paper)
    assert len(evidence_list) == 1
    assert evidence_list[0].evidence_level == EvidenceLevel.NONE
    assert evidence_list[0].retrieval_status == RetrievalStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_verification_engine_supported():
    claim = "Convolutional neural networks achieve 98% accuracy on digit recognition."
    ev = Evidence(
        id=uuid4(),
        source_provider="crossref",
        passage="Our experimental results show convolutional neural networks achieve 98% accuracy on digit recognition benchmarks.",
        evidence_level=EvidenceLevel.ABSTRACT_ONLY,
        retrieval_status=RetrievalStatus.RETRIEVED,
        similarity_score=0.85,
    )
    verif = await verify_claim_against_evidence(claim, [ev], paper_year=2023)
    assert verif.verdict == VerificationVerdict.SUPPORTED
    assert verif.confidence >= 0.70
    assert "corroborates" in verif.rationale.lower()


@pytest.mark.asyncio
async def test_verification_engine_contradictory_numbers():
    claim = "The algorithm achieved 95% accuracy."
    ev = Evidence(
        id=uuid4(),
        source_provider="openalex",
        passage="The evaluated algorithm only achieved 42% accuracy under standard conditions.",
        evidence_level=EvidenceLevel.ABSTRACT_ONLY,
        retrieval_status=RetrievalStatus.RETRIEVED,
        similarity_score=0.55,
    )
    verif = await verify_claim_against_evidence(claim, [ev], paper_year=2023)
    assert verif.verdict == VerificationVerdict.CONTRADICTORY
    assert verif.needs_human_review is True
    assert any("Conflicting quantitative figures" in r for r in verif.review_reasons)


@pytest.mark.asyncio
async def test_verification_engine_unretrieved_honesty_rule():
    claim = "Graphene exhibits extraordinary thermal conductivity."
    ev = Evidence(
        id=uuid4(),
        source_provider="none",
        passage="No publication retrieved.",
        evidence_level=EvidenceLevel.NONE,
        retrieval_status=RetrievalStatus.NOT_FOUND,
        similarity_score=0.0,
    )
    verif = await verify_claim_against_evidence(claim, [ev])
    # Rule 3 & 4: Retrieval failure is not refutation, verdict must be null!
    assert verif.verdict is None
    assert verif.verification_state == VerificationState.UNABLE_TO_VERIFY
    assert verif.needs_human_review is True


@pytest.mark.asyncio
async def test_verification_engine_outdated():
    claim = "The optimal treatment protocol yields sustained remission."
    ev = Evidence(
        id=uuid4(),
        source_provider="europe_pmc",
        passage="The treatment protocol yields sustained remission across clinical cohorts.",
        evidence_level=EvidenceLevel.ABSTRACT_ONLY,
        retrieval_status=RetrievalStatus.RETRIEVED,
        similarity_score=0.75,
    )
    # Published in 2005 (older than 10 years)
    verif = await verify_claim_against_evidence(claim, [ev], auto_flag_outdated_years=10, paper_year=2005)
    assert verif.verdict == VerificationVerdict.POTENTIALLY_OUTDATED
    assert any("threshold" in r.lower() for r in verif.review_reasons)
