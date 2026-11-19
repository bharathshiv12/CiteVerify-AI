"""
Services package exports.
"""
from app.services.document_processor import extract_text_from_pdf
from app.services.claim_extractor import extract_claims
from app.services.citation_parser import parse_citations_and_references
from app.services.citation_matcher import match_claims_to_citations
from app.services.research_retriever import retrieve_publication
from app.services.evidence_extractor import extract_candidate_evidence
from app.services.embedding_service import compute_similarities
from app.services.verification_engine import verify_claim_against_evidence
from app.services.report_generator import generate_verification_report

__all__ = [
    "extract_text_from_pdf",
    "extract_claims",
    "parse_citations_and_references",
    "match_claims_to_citations",
    "retrieve_publication",
    "extract_candidate_evidence",
    "compute_similarities",
    "verify_claim_against_evidence",
    "generate_verification_report",
]
