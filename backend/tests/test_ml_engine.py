"""
Comprehensive tests for ML engine:
- SentenceTransformer semantic evidence retrieval (with TF-IDF fallback)
- Pretrained NLI classification (entailment, contradiction, neutral)
- Numerical verification (percentages, sample sizes, units, statistical significance)
- Model unavailability handling and fallback behaviour
- End-to-end integration with verification engine
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.evidence import Evidence
from app.schemas.enums import EvidenceLevel, RetrievalStatus, VerificationVerdict, VerificationState
from app.services.ml_engine import (
    NumericalVerifier,
    SentenceTransformerRetriever,
    PretrainedNLIClassifier,
    get_semantic_similarities,
    evaluate_nli,
    check_numerical_consistency,
    get_ml_engine_status,
)
from app.services.verification_engine import verify_claim_against_evidence


# =====================================================================
# 1. Numerical Verifier Tests
# =====================================================================

def test_numerical_percentage_corroboration():
    claim = "The proposed classifier achieved 94.5% sensitivity across patient groups."
    evidence = "In multi-center validation, the model reached 94.5% sensitivity (95% CI [92.1, 96.8])."
    result = NumericalVerifier.verify(claim, evidence)
    assert not result.has_discrepancy
    assert any("Percentage corroborated: 94.5%" in m for m in result.matched_facts)


def test_numerical_percentage_discrepancy():
    claim = "Our neural architecture achieved 98.2% test accuracy on ImageNet."
    evidence = "The evaluated architecture achieved 74.1% test accuracy under identical hyperparameters."
    result = NumericalVerifier.verify(claim, evidence)
    assert result.has_discrepancy
    assert result.severity == "HIGH_CONTRADICTION"
    assert any("Percentage mismatch" in r for r in result.discrepancy_reasons)


def test_numerical_sample_size_conflict():
    claim = "The clinical trial evaluated 2,500 participants across three sites."
    evidence = "We conducted a pilot trial on n = 45 participants to assess feasibility."
    result = NumericalVerifier.verify(claim, evidence)
    assert result.has_discrepancy
    assert any("Sample size discrepancy" in r for r in result.discrepancy_reasons)


def test_numerical_unit_conflict():
    claim = "Patients received an initial dosage of 50 mg daily."
    evidence = "The safety profile was assessed with an initial dosage of 50 g daily."
    result = NumericalVerifier.verify(claim, evidence)
    assert result.has_discrepancy
    assert result.severity == "HIGH_CONTRADICTION"
    assert any("Unit conflict" in r for r in result.discrepancy_reasons)


def test_statistical_significance_inversion():
    claim = "The intervention yielded a statistically significant reduction in symptom score."
    evidence = "Between group differences showed no statistically significant difference in symptom score (p = 0.42)."
    result = NumericalVerifier.verify(claim, evidence)
    assert result.has_discrepancy
    assert result.severity == "HIGH_CONTRADICTION"
    assert any("Statistical contradiction" in r for r in result.discrepancy_reasons)


# =====================================================================
# 2. Semantic Evidence Retrieval & Fallback Tests
# =====================================================================

def test_semantic_retrieval_relevant_vs_irrelevant():
    query = "Graphene exhibits extraordinary electron mobility at room temperature."
    passages = [
        "Measurements reveal graphene has electron mobility exceeding 15,000 cm^2/(V*s) at room temperature.",
        "Soil bacterial diversity correlates with nitrogen application in monoculture maize farming.",
    ]
    scores = get_semantic_similarities(query, passages)
    assert len(scores) == 2
    assert scores[0] > scores[1]
    assert scores[0] >= 0.35
    assert scores[1] <= 0.20


def test_retriever_model_unavailable_fallback():
    retriever = SentenceTransformerRetriever()
    # Force unavailable state
    retriever._load_attempted = True
    retriever._is_available = False
    retriever._model = None

    query = "RNA sequencing reveals differential gene expression."
    passages = [
        "RNA sequencing of cardiac tissue identified 120 differentially expressed genes.",
        "A study on concrete curing temperatures and compressive strength.",
    ]
    scores = retriever.compute_similarities(query, passages)
    assert len(scores) == 2
    assert scores[0] > scores[1]
    assert all(0.0 <= s <= 1.0 for s in scores)


# =====================================================================
# 3. NLI Classification Tests (Entailment, Contradiction, Neutral)
# =====================================================================

def test_nli_entailment():
    premise = "Transformer networks achieved state-of-the-art results on language translation benchmarks."
    hypothesis = "Transformers improve language translation performance."
    result = evaluate_nli(premise, hypothesis)
    assert result["label"] == "ENTAILMENT"
    assert result["confidence"] > 0.4


def test_nli_contradiction():
    premise = "The experimental drug failed to show efficacy and caused adverse reactions."
    hypothesis = "The experimental drug is safe and effective."
    result = evaluate_nli(premise, hypothesis)
    assert result["label"] == "CONTRADICTION"


def test_nli_neutral_or_insufficient():
    premise = "The study was conducted in a laboratory setting in Switzerland during 2021."
    hypothesis = "The therapeutic regimen cured 95% of patients with advanced lymphoma."
    result = evaluate_nli(premise, hypothesis)
    assert result["label"] == "NEUTRAL"


def test_nli_classifier_unavailable_fallback():
    classifier = PretrainedNLIClassifier()
    classifier._load_attempted = True
    classifier._is_available = False
    classifier._classifier = None

    # Should fall back cleanly without raising exceptions
    res = classifier.classify(
        premise="Deep learning models achieve high accuracy on clinical imaging.",
        hypothesis="Deep learning models perform well on medical image analysis.",
    )
    assert res["mode"] == "heuristic_fallback"
    assert res["label"] == "ENTAILMENT"


# =====================================================================
# 4. Integrated Verification Engine Tests with ML Components
# =====================================================================

@pytest.mark.asyncio
async def test_integrated_verification_with_numerical_contradiction():
    claim = "The algorithm achieved 98% accuracy on digit recognition."
    ev = Evidence(
        id=uuid4(),
        source_provider="openalex",
        passage="Under empirical evaluation, the algorithm achieved 54% accuracy on digit recognition.",
        evidence_level=EvidenceLevel.ABSTRACT_ONLY,
        retrieval_status=RetrievalStatus.RETRIEVED,
        similarity_score=0.60,
    )
    verif = await verify_claim_against_evidence(claim, [ev])
    assert verif.verdict == VerificationVerdict.CONTRADICTORY
    assert verif.needs_human_review is True
    assert any("Percentage mismatch" in r for r in verif.review_reasons)


@pytest.mark.asyncio
async def test_integrated_verification_with_neutral_insufficient_evidence():
    claim = "Quantum annealing solves NP-hard problems in polynomial time."
    ev = Evidence(
        id=uuid4(),
        source_provider="crossref",
        passage="We review the theoretical foundations of quantum computing hardware and cryostat cooling.",
        evidence_level=EvidenceLevel.ABSTRACT_ONLY,
        retrieval_status=RetrievalStatus.RETRIEVED,
        similarity_score=0.10,
    )
    verif = await verify_claim_against_evidence(claim, [ev])
    # Rule 4: Insufficient/neutral evidence must have null verdict and request human review
    assert verif.verdict is None
    assert verif.verification_state == VerificationState.REQUIRES_HUMAN_REVIEW
    assert verif.needs_human_review is True


@pytest.mark.asyncio
async def test_integrated_verification_missing_evidence():
    claim = "CRISPR-Cas9 edits human embryonic genomes with zero off-target cuts."
    ev = Evidence(
        id=uuid4(),
        source_provider="none",
        passage="Document paywalled or not found in scholarly indices.",
        evidence_level=EvidenceLevel.NONE,
        retrieval_status=RetrievalStatus.NOT_FOUND,
        similarity_score=0.0,
    )
    verif = await verify_claim_against_evidence(claim, [ev])
    assert verif.verdict is None
    assert verif.verification_state == VerificationState.UNABLE_TO_VERIFY
    assert verif.needs_human_review is True


def test_ml_engine_status_report():
    status = get_ml_engine_status()
    assert "semantic_retriever" in status
    assert "nli_classifier" in status
    assert "numerical_verifier" in status
    assert status["semantic_retriever"]["model_name"] == "sentence-transformers/all-MiniLM-L6-v2"
    assert status["nli_classifier"]["model_name"] == "cross-encoder/nli-deberta-v3-small"
    assert "scientific_disclaimer" in status["nli_classifier"]
