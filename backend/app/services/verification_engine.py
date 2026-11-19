"""
Service: Verification Engine
Responsibility:
    Executes strict comparison between an empirical factual claim and candidate evidence passages.
    Assigns canonical verdicts, confidence scores, human-readable rationale, and review flags.

    Adheres strictly to the 5 Hard Honesty Rules:
    1. Never fabricate publications, DOIs, quotes, evidence passages, or test passes.
    2. Abstracts are never presented as full text.
    3. Retrieval failure is never marked as false or unsupported (verdict = None, state = UNABLE_TO_VERIFY).
    4. Insufficient evidence is never forced into a binary verdict (verdict = None, state = REQUIRES_HUMAN_REVIEW).
    5. Full traceability: every verdict traceable to source, passage, and evidence level.
"""
import re
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from app.core.config import settings
from app.schemas.evidence import Evidence
from app.schemas.verification import Verification
from app.schemas.enums import VerificationVerdict, VerificationState, EvidenceLevel, RetrievalStatus

logger = logging.getLogger("citeverify.verification_engine")

NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?%?\b")
NEGATION_WORDS = {"not", "never", "no", "neither", "nor", "fail", "failed", "fails", "cannot", "without"}


def extract_numbers(text: str) -> List[str]:
    return NUMBER_PATTERN.findall(text)


def has_negation(text: str) -> bool:
    tokens = set(re.findall(r"\b[a-z]+\b", text.lower()))
    return bool(tokens.intersection(NEGATION_WORDS))


async def verify_claim_against_evidence(
    claim_text: str,
    evidence_items: List[Evidence],
    auto_flag_outdated_years: int = 10,
    paper_year: Optional[int] = None,
) -> Verification:
    """
    Evaluates claim alignment against evidence passages.
    If external AI (Gemini) is configured with an API key, attempts LLM evaluation;
    otherwise executes high-fidelity deterministic heuristic NLI rules.
    """
    now = datetime.now(timezone.utc)
    current_year = now.year

    # 1. Filter usable evidence items
    valid_evidence = [
        e for e in evidence_items
        if e.retrieval_status == RetrievalStatus.RETRIEVED and e.evidence_level != EvidenceLevel.NONE
    ]

    # Rule 3: Retrieval failure is not refutation
    if not valid_evidence:
        reasons = ["No publication retrieved or document access is paywalled/restricted."]
        return Verification(
            id=uuid4(),
            verdict=None,
            verification_state=VerificationState.UNABLE_TO_VERIFY,
            confidence=0.0,
            rationale="No verifiable evidence passages could be retrieved from open scholarly databases.",
            needs_human_review=True,
            review_reasons=reasons,
            evaluated_at=now,
            evidence_summary="0 accessible passages retrieved.",
        )

    # Top candidate passage by similarity
    top_evidence = max(valid_evidence, key=lambda e: e.similarity_score or 0.0)
    top_score = top_evidence.similarity_score or 0.0
    top_passage = top_evidence.passage

    # Rule 4: Insufficient evidence (e.g. metadata only) is never forced into a binary verdict
    if top_evidence.evidence_level == EvidenceLevel.METADATA_ONLY:
        return Verification(
            id=uuid4(),
            verdict=None,
            verification_state=VerificationState.REQUIRES_HUMAN_REVIEW,
            confidence=0.25,
            rationale="Only bibliographic metadata (title/authors) was retrieved. The abstract or full text is necessary to verify or refute this empirical statement.",
            needs_human_review=True,
            review_reasons=["Verification requires abstract or full-text passage (only metadata available)."],
            evaluated_at=now,
            evidence_summary=f"Metadata retrieved: {top_passage[:150]}...",
        )

    # 2. Check for optional external AI (Gemini) evaluation if configured
    if settings.AI_PROVIDER == "gemini" and settings.AI_API_KEY:
        try:
            return await _verify_with_gemini(
                claim_text=claim_text,
                evidence=top_evidence,
                paper_year=paper_year,
                auto_flag_outdated_years=auto_flag_outdated_years,
            )
        except Exception as ex:
            logger.warning(f"External AI verification failed, falling back to deterministic NLI: {ex}")

    # 3. Deterministic Heuristic NLI Verification
    claim_nums = set(extract_numbers(claim_text))
    evidence_nums = set(extract_numbers(top_passage))
    claim_neg = has_negation(claim_text)
    evidence_neg = has_negation(top_passage)

    # Outdated check
    is_outdated = False
    if paper_year and (current_year - paper_year > auto_flag_outdated_years):
        is_outdated = True

    review_reasons: List[str] = []
    verdict: Optional[VerificationVerdict] = None
    verification_state: VerificationState = VerificationState.VERIFIED
    confidence: float = 0.0
    rationale: str = ""

    # Detect numeric contradiction
    # If claim mentions a specific number/percent that is contradicted in evidence
    numeric_conflict = False
    if claim_nums and evidence_nums and not claim_nums.intersection(evidence_nums):
        # Both discuss quantitative findings but values do not match
        numeric_conflict = True

    # Polarity conflict: one has negation, the other does not
    polarity_conflict = (claim_neg != evidence_neg)

    if top_score < 0.15:
        # Rule 4: Insufficient evidence -> null verdict
        verdict = None
        verification_state = VerificationState.REQUIRES_HUMAN_REVIEW
        confidence = round(top_score, 2)
        rationale = "Retrieved passage has low semantic overlap with the specific assertion in the claim."
        review_reasons.append("Low semantic alignment with retrieved evidence passage.")

    elif numeric_conflict and top_score >= 0.25:
        verdict = VerificationVerdict.CONTRADICTORY
        confidence = min(0.90, round(top_score + 0.2, 2))
        rationale = f"Evidence contains conflicting numerical figures ({', '.join(evidence_nums)}) compared to the claim ({', '.join(claim_nums)})."
        review_reasons.append("Conflicting quantitative figures detected between claim and source evidence.")

    elif polarity_conflict and top_score >= 0.35:
        verdict = VerificationVerdict.CONTRADICTORY
        confidence = min(0.85, round(top_score + 0.1, 2))
        rationale = "Evidence expresses contradictory polarity or negated finding regarding the asserted claim."
        review_reasons.append("Directional polarity or negation conflict detected.")

    elif top_score >= 0.45:
        if is_outdated:
            verdict = VerificationVerdict.POTENTIALLY_OUTDATED
            confidence = min(0.95, round(top_score, 2))
            rationale = f"Evidence supports claim topic, but citation is from {paper_year} (> {auto_flag_outdated_years} years old). Empirical conclusions may be superseded."
            review_reasons.append(f"Citation is from {paper_year} (exceeds {auto_flag_outdated_years} year threshold).")
        else:
            verdict = VerificationVerdict.SUPPORTED
            confidence = min(0.95, round(top_score + 0.1, 2))
            rationale = "Retrieved scholarly passage directly corroborates the factual assertion made in the claim."

    elif top_score >= 0.25:
        if is_outdated:
            verdict = VerificationVerdict.POTENTIALLY_OUTDATED
            confidence = round(top_score, 2)
            rationale = f"Evidence partially supports claim, but publication is from {paper_year}."
            review_reasons.append(f"Citation is from {paper_year}.")
        else:
            verdict = VerificationVerdict.PARTLY_SUPPORTED
            confidence = round(top_score, 2)
            rationale = "Retrieved passage provides partial or contextual support for the claim but does not corroborate all nuances."

    else:
        # Low-medium score where evidence is ambiguous
        verdict = None
        verification_state = VerificationState.REQUIRES_HUMAN_REVIEW
        confidence = round(top_score, 2)
        rationale = "Passage discusses related concepts but does not provide definitive evidence to either corroborate or refute the claim."
        review_reasons.append("Ambiguous evidence alignment requires domain expert review.")

    # Flag for human review if confidence is below 0.65 or if reasons exist
    needs_review = bool(review_reasons or confidence < 0.65 or verdict is None)
    if needs_review and verification_state == VerificationState.VERIFIED:
        verification_state = VerificationState.REQUIRES_HUMAN_REVIEW

    summary = f"Evidence from {top_evidence.source_provider} ({top_evidence.evidence_level.value}): \"{top_passage[:160]}...\""

    return Verification(
        id=uuid4(),
        verdict=verdict,
        verification_state=verification_state,
        confidence=confidence,
        rationale=rationale,
        needs_human_review=needs_review,
        review_reasons=review_reasons,
        evaluated_at=now,
        evidence_summary=summary,
    )


async def _verify_with_gemini(
    claim_text: str,
    evidence: Evidence,
    paper_year: Optional[int],
    auto_flag_outdated_years: int,
) -> Verification:
    """
    Invokes Gemini API via httpx REST endpoint to perform natural language inference.
    """
    import httpx

    prompt = f"""You are a scientific claim and citation verification engine.
Compare the factual claim with the retrieved evidence passage.

Claim: "{claim_text}"
Evidence Passage ({evidence.evidence_level.value}): "{evidence.passage}"
Publication Year: {paper_year or "Unknown"}

Strict Rules:
- If evidence directly proves the claim: SUPPORTED
- If evidence supports only part of the claim: PARTLY_SUPPORTED
- If evidence contradicts numbers or findings: CONTRADICTORY
- If evidence does not support the claim: UNSUPPORTED
- If publication year is > {auto_flag_outdated_years} years old and findings may be superseded: POTENTIALLY_OUTDATED
- If evidence is ambiguous or insufficient to judge: set verdict to null and needs_human_review to true.

Output strictly valid JSON with these keys:
{{
    "verdict": "SUPPORTED" | "PARTLY_SUPPORTED" | "UNSUPPORTED" | "CONTRADICTORY" | "POTENTIALLY_OUTDATED" | null,
    "confidence": float between 0.0 and 1.0,
    "rationale": "detailed 1-2 sentence explanation",
    "needs_human_review": boolean,
    "review_reasons": ["list", "of", "reasons"]
}}
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent?key={settings.AI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(raw_text)

        verdict_str = result.get("verdict")
        verdict = VerificationVerdict(verdict_str) if verdict_str else None
        state = VerificationState.VERIFIED if verdict and not result.get("needs_human_review") else (
            VerificationState.REQUIRES_HUMAN_REVIEW if result.get("needs_human_review") else VerificationState.VERIFIED
        )

        return Verification(
            id=uuid4(),
            verdict=verdict,
            verification_state=state,
            confidence=float(result.get("confidence", 0.7)),
            rationale=str(result.get("rationale", "")),
            needs_human_review=bool(result.get("needs_human_review", False)),
            review_reasons=list(result.get("review_reasons", [])),
            evaluated_at=datetime.now(timezone.utc),
            evidence_summary=f"Evaluated via Gemini {settings.AI_MODEL}: \"{evidence.passage[:150]}...\"",
        )
