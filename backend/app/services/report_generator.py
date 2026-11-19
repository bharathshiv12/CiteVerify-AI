"""
Service: Report Generator
Responsibility:
    Synthesizes claims, evidence levels, and verification verdicts into a
    cohesive structured report with overall citation reliability scoring.

Formula:
    Reliability Score = (
        1.0 * count(SUPPORTED) +
        0.7 * count(PARTLY_SUPPORTED) +
        0.5 * count(POTENTIALLY_OUTDATED) +
        0.3 * count(UNVERIFIED) +
        0.0 * count(UNSUPPORTED) -
        0.2 * count(CONTRADICTORY)
    ) / total_claims * 100.0, clamped to [0.0, 100.0].
"""
from datetime import datetime, timezone
from typing import Dict, List

from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.report import VerificationReport
from app.schemas.enums import VerificationVerdict, EvidenceLevel


def calculate_reliability_score(claims: List[Claim]) -> float:
    """
    Computes weighted reliability score on a 0.0 - 100.0 scale.
    """
    if not claims:
        return 100.0

    score_weights = {
        VerificationVerdict.SUPPORTED: 1.0,
        VerificationVerdict.PARTLY_SUPPORTED: 0.7,
        VerificationVerdict.POTENTIALLY_OUTDATED: 0.5,
        VerificationVerdict.UNSUPPORTED: 0.0,
        VerificationVerdict.CONTRADICTORY: -0.2,
    }

    total_weight = 0.0
    for claim in claims:
        if claim.verdict and claim.verdict in score_weights:
            total_weight += score_weights[claim.verdict]
        else:
            # Unverified / unable to verify / null
            total_weight += 0.3

    raw_percentage = (total_weight / len(claims)) * 100.0
    return round(max(0.0, min(100.0, raw_percentage)), 1)


def generate_verification_report(
    document: Document,
    claims: List[Claim],
) -> VerificationReport:
    """
    Synthesizes metrics, aggregate counts, and compiles the final VerificationReport.
    """
    now = datetime.now(timezone.utc)
    total_claims = len(claims)

    verdict_counts: Dict[str, int] = {v.value: 0 for v in VerificationVerdict}
    verdict_counts["UNVERIFIED"] = 0

    evidence_level_counts: Dict[str, int] = {
        EvidenceLevel.FULL_TEXT.value: 0,
        EvidenceLevel.ABSTRACT_ONLY.value: 0,
        EvidenceLevel.METADATA_ONLY.value: 0,
        EvidenceLevel.NONE.value: 0,
    }

    human_review_count = 0

    for claim in claims:
        if claim.verdict:
            verdict_counts[claim.verdict.value] += 1
        else:
            verdict_counts["UNVERIFIED"] += 1

        if claim.needs_human_review:
            human_review_count += 1

        if claim.evidence:
            for ev in claim.evidence:
                lvl = ev.evidence_level.value
                evidence_level_counts[lvl] = evidence_level_counts.get(lvl, 0) + 1
        else:
            evidence_level_counts[EvidenceLevel.NONE.value] += 1

    reliability = calculate_reliability_score(claims)

    return VerificationReport(
        document_id=document.id,
        filename=document.filename,
        generated_at=now,
        total_claims=total_claims,
        reliability_score=reliability,
        verdict_counts=verdict_counts,
        evidence_level_counts=evidence_level_counts,
        human_review_required_count=human_review_count,
        claims=claims,
    )
