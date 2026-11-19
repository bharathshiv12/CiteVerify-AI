"""
Service: Report Generator
Owner: Agent 2 (Backend Developer)
Responsibility:
    Synthesizes claims, evidence levels, and verification verdicts into a
    cohesive structured report with overall citation reliability scoring.

Inputs:
    - document (Document): Parent document record.
    - claims (List[Claim]): All verified and unverified claims.

Outputs:
    - VerificationReport: Complete report envelope with aggregate counts and score.
"""
from typing import List
from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.report import VerificationReport


def generate_verification_report(
    document: Document,
    claims: List[Claim],
) -> VerificationReport:
    """
    Computes summary metrics, reliability score, and compiles the final report.
    Raises NotImplementedError until Agent 2 implements report aggregation.
    """
    raise NotImplementedError("generate_verification_report not implemented yet (Assigned to Agent 2).")

