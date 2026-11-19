"""
Service: Pipeline Orchestrator
Responsibility:
    Executes the complete 11-stage verification pipeline sequentially for an uploaded document:
    1. UPLOADED
    2. TEXT_EXTRACTION
    3. CLAIM_EXTRACTION
    4. CITATION_PARSING
    5. REFERENCE_PARSING
    6. CITATION_MATCHING
    7. PAPER_RETRIEVAL
    8. EVIDENCE_EXTRACTION
    9. VERIFICATION
    10. REPORT_GENERATION
    11. DONE

    Updates progress and persisted state at each step and handles errors with full auditability.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from app.database.repository import AbstractRepository
from app.storage.file_storage import get_file_storage
from app.schemas.enums import ProcessingStatus, PipelineStage, RetrievalStatus
from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.citation import Citation
from app.schemas.research_paper import ResearchPaper
from app.services.document_processor import extract_text_from_pdf, PDFProcessingError
from app.services.claim_extractor import extract_claims
from app.services.citation_parser import parse_in_text_citations, parse_bibliography_references
from app.services.citation_matcher import match_claims_to_citations
from app.services.research_retriever import retrieve_publication
from app.services.evidence_extractor import extract_candidate_evidence
from app.services.verification_engine import verify_claim_against_evidence
from app.services.report_generator import generate_verification_report

logger = logging.getLogger("citeverify.pipeline_orchestrator")


async def run_pipeline(document_id: UUID, repo: AbstractRepository) -> Document:
    """
    Executes the full 11-stage pipeline for a given document.
    """
    doc = await repo.get_document(document_id)
    if not doc:
        logger.error(f"Cannot run pipeline: Document {document_id} not found.")
        return None

    storage = get_file_storage()
    # Try anonymous and user storage locations
    rel_path = f"anonymous/{document_id}.pdf"
    if hasattr(repo, "document_owners"):
        owner_id = repo.document_owners.get(document_id)
        if owner_id:
            user_path = f"{owner_id}/{document_id}.pdf"
            if await storage.file_exists(user_path):
                rel_path = user_path

    try:
        content = await storage.get_file(rel_path)
    except Exception as e:
        logger.error(f"Failed to read file for document {document_id}: {e}")
        doc.status = ProcessingStatus.FAILED
        doc.error_message = f"Storage read error: {str(e)}"
        doc.updated_at = datetime.now(timezone.utc)
        return await repo.update_document(doc)

    try:
        # --- Stage 1: Mark processing & TEXT_EXTRACTION ---
        doc.status = ProcessingStatus.PROCESSING
        doc.pipeline_stage = PipelineStage.TEXT_EXTRACTION
        doc.updated_at = datetime.now(timezone.utc)
        await repo.update_document(doc)

        logger.info(f"Pipeline [1/10] TEXT_EXTRACTION for doc {document_id}")
        pdf_data = extract_text_from_pdf(content, document_id)
        pages = pdf_data["pages"]
        doc.page_count = pdf_data["page_count"]
        doc.is_scanned = pdf_data["is_scanned"]
        await repo.update_document(doc)

        # If scanned with no OCR text, fail gracefully
        if doc.is_scanned and pdf_data["total_char_count"] < 100:
            doc.status = ProcessingStatus.FAILED
            doc.error_message = "Scanned image PDF detected with insufficient extractable text."
            doc.updated_at = datetime.now(timezone.utc)
            return await repo.update_document(doc)

        # --- Stage 2: CLAIM_EXTRACTION ---
        doc.pipeline_stage = PipelineStage.CLAIM_EXTRACTION
        doc.updated_at = datetime.now(timezone.utc)
        await repo.update_document(doc)
        logger.info(f"Pipeline [2/10] CLAIM_EXTRACTION for doc {document_id}")
        claims: List[Claim] = extract_claims(pages, document_id)

        # --- Stage 3: CITATION_PARSING ---
        doc.pipeline_stage = PipelineStage.CITATION_PARSING
        doc.updated_at = datetime.now(timezone.utc)
        await repo.update_document(doc)
        logger.info(f"Pipeline [3/10] CITATION_PARSING for doc {document_id}")
        citations: List[Citation] = parse_in_text_citations(pages, document_id)

        # --- Stage 4: REFERENCE_PARSING ---
        doc.pipeline_stage = PipelineStage.REFERENCE_PARSING
        doc.updated_at = datetime.now(timezone.utc)
        await repo.update_document(doc)
        logger.info(f"Pipeline [4/10] REFERENCE_PARSING for doc {document_id}")
        references = parse_bibliography_references(pages)

        # --- Stage 5: CITATION_MATCHING ---
        doc.pipeline_stage = PipelineStage.CITATION_MATCHING
        doc.updated_at = datetime.now(timezone.utc)
        await repo.update_document(doc)
        logger.info(f"Pipeline [5/10] CITATION_MATCHING for doc {document_id}")
        claims = match_claims_to_citations(claims, citations, references)
        await repo.save_citations(citations)

        # --- Stage 6: PAPER_RETRIEVAL ---
        doc.pipeline_stage = PipelineStage.PAPER_RETRIEVAL
        doc.updated_at = datetime.now(timezone.utc)
        await repo.update_document(doc)
        logger.info(f"Pipeline [6/10] PAPER_RETRIEVAL for doc {document_id}")

        # Retrieve publication for citations with reference text
        paper_cache: Dict[str, ResearchPaper] = {}
        for cit in citations:
            ref_key = cit.reference_text or cit.raw_marker
            if not ref_key:
                continue

            if ref_key not in paper_cache:
                paper = await retrieve_publication(ref_key)
                await repo.save_paper(paper)
                paper_cache[ref_key] = paper

            resolved_paper = paper_cache[ref_key]
            cit.matched_paper_id = resolved_paper.id
            await repo.save_citation(cit)

        # --- Stage 7: EVIDENCE_EXTRACTION ---
        doc.pipeline_stage = PipelineStage.EVIDENCE_EXTRACTION
        doc.updated_at = datetime.now(timezone.utc)
        await repo.update_document(doc)
        logger.info(f"Pipeline [7/10] EVIDENCE_EXTRACTION for doc {document_id}")

        for claim in claims:
            candidate_evidence = []
            for cit in claim.citations:
                matched_id = cit.matched_paper_id
                if not matched_id:
                    continue
                paper = await repo.get_paper(matched_id)
                if not paper:
                    continue
                extracted_ev = await extract_candidate_evidence(paper, claim_text=claim.claim_text)
                candidate_evidence.extend(extracted_ev)

            # Deduplicate and sort by similarity score
            candidate_evidence.sort(key=lambda e: e.similarity_score or 0.0, reverse=True)
            claim.evidence = candidate_evidence[:5]  # Keep top 5 relevant passages
            await repo.save_evidence(claim.evidence, claim_id=claim.id)

        # --- Stage 8: VERIFICATION ---
        doc.pipeline_stage = PipelineStage.VERIFICATION
        doc.updated_at = datetime.now(timezone.utc)
        await repo.update_document(doc)
        logger.info(f"Pipeline [8/10] VERIFICATION for doc {document_id}")

        for claim in claims:
            # Determine paper year if available
            paper_year = None
            if claim.citations:
                for cit in claim.citations:
                    if cit.matched_paper_id:
                        p = await repo.get_paper(cit.matched_paper_id)
                        if p and p.year:
                            paper_year = p.year
                            break

            verification = await verify_claim_against_evidence(
                claim_text=claim.claim_text,
                evidence_items=claim.evidence,
                paper_year=paper_year,
            )

            claim.verdict = verification.verdict
            claim.verification_state = verification.verification_state
            claim.confidence = verification.confidence
            claim.rationale = verification.rationale
            claim.needs_human_review = verification.needs_human_review
            claim.review_reasons = verification.review_reasons
            claim.updated_at = datetime.now(timezone.utc)

        await repo.save_claims(claims)

        # --- Stage 9: REPORT_GENERATION ---
        doc.pipeline_stage = PipelineStage.REPORT_GENERATION
        doc.updated_at = datetime.now(timezone.utc)
        await repo.update_document(doc)
        logger.info(f"Pipeline [9/10] REPORT_GENERATION for doc {document_id}")

        report = generate_verification_report(doc, claims)
        await repo.save_report(report)

        # --- Stage 10: DONE ---
        doc.pipeline_stage = PipelineStage.DONE
        doc.status = ProcessingStatus.COMPLETED
        doc.error_message = None
        doc.updated_at = datetime.now(timezone.utc)
        await repo.update_document(doc)
        logger.info(f"Pipeline completed successfully for doc {document_id}")

        return doc

    except Exception as e:
        logger.exception(f"Unhandled error in verification pipeline for doc {document_id}: {e}")
        doc.status = ProcessingStatus.FAILED
        doc.error_message = f"Pipeline execution error: {str(e)}"
        doc.updated_at = datetime.now(timezone.utc)
        return await repo.update_document(doc)
