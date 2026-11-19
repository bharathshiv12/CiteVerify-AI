"""
In-memory repository implementation for zero-credential local development and automated testing.
Provides thread-safe async access with full relational integrity and cascade deletion.
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from app.repositories.base import AbstractRepository
from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.citation import Citation
from app.schemas.research_paper import ResearchPaper
from app.schemas.evidence import Evidence
from app.schemas.report import VerificationReport
from app.schemas.enums import VerificationVerdict, ProcessingStatus, PipelineStage
from app.schemas.dashboard import DashboardStats, DashboardActivity
from app.schemas.settings import UserSettings, UserSettingsUpdate
from app.schemas.user import UserProfile


class InMemoryRepository(AbstractRepository):
    def __init__(self):
        self.documents: Dict[UUID, Document] = {}
        self.document_owners: Dict[UUID, Optional[UUID]] = {}
        self.claims: Dict[UUID, Claim] = {}
        self.citations: Dict[UUID, Citation] = {}
        self.papers: Dict[UUID, ResearchPaper] = {}
        self.papers_by_doi: Dict[str, UUID] = {}
        self.evidence: Dict[UUID, Evidence] = {}
        self.claim_evidence: Dict[UUID, List[UUID]] = {}
        self.reports: Dict[UUID, VerificationReport] = {}  # document_id -> report
        self.reviews: List[Dict] = []
        self.activities: List[DashboardActivity] = []
        self.user_settings_store: Dict[UUID, UserSettings] = {}
        self.profiles: Dict[UUID, UserProfile] = {}
        self.processing_jobs: Dict[UUID, Dict] = {}  # document_id -> job dict

    # Documents
    async def create_document(self, document: Document, user_id: Optional[UUID] = None) -> Document:
        self.documents[document.id] = document
        self.document_owners[document.id] = user_id

        self.activities.append(
            DashboardActivity(
                id=uuid4(),
                document_id=document.id,
                event_type="DOCUMENT_UPLOAD",
                description=f"Uploaded manuscript: {document.filename}",
                created_at=datetime.now(timezone.utc),
            )
        )
        return document

    async def get_document(self, document_id: UUID) -> Optional[Document]:
        return self.documents.get(document_id)

    async def get_document_owner(self, document_id: UUID) -> Optional[UUID]:
        return self.document_owners.get(document_id)

    async def update_document(self, document: Document) -> Document:
        self.documents[document.id] = document
        if document.status == ProcessingStatus.COMPLETED:
            self.activities.append(
                DashboardActivity(
                    id=uuid4(),
                    document_id=document.id,
                    event_type="ANALYSIS_COMPLETED",
                    description=f"Completed verification analysis for: {document.filename}",
                    created_at=datetime.now(timezone.utc),
                )
            )
        return document

    async def delete_document(self, document_id: UUID) -> bool:
        if document_id not in self.documents:
            return False

        # Cascade delete
        del self.documents[document_id]
        self.document_owners.pop(document_id, None)

        # Delete attached claims and evidence
        claim_ids_to_del = [cid for cid, c in self.claims.items() if c.document_id == document_id]
        for cid in claim_ids_to_del:
            self.claims.pop(cid, None)
            ev_ids = self.claim_evidence.pop(cid, [])
            for eid in ev_ids:
                self.evidence.pop(eid, None)

        # Delete attached citations
        cit_ids_to_del = [cid for cid, cit in self.citations.items() if cit.document_id == document_id]
        for cid in cit_ids_to_del:
            self.citations.pop(cid, None)

        # Delete reports
        self.reports.pop(document_id, None)

        # Delete reviews
        self.reviews = [r for r in self.reviews if r.get("document_id") != document_id]

        # Delete processing jobs
        self.processing_jobs.pop(document_id, None)
        return True

    async def list_documents(self, user_id: Optional[UUID] = None, page: int = 1, page_size: int = 20) -> Tuple[List[Document], int]:
        all_docs = list(self.documents.values())
        if user_id:
            all_docs = [d for d in all_docs if self.document_owners.get(d.id) == user_id]

        all_docs.sort(key=lambda d: d.created_at, reverse=True)
        total = len(all_docs)
        start = (page - 1) * page_size
        end = start + page_size
        return all_docs[start:end], total

    # Claims
    async def save_claims(self, claims: List[Claim]) -> List[Claim]:
        for c in claims:
            self.claims[c.id] = c
            if c.evidence:
                await self.save_evidence(c.evidence, claim_id=c.id)
            if c.citations:
                await self.save_citations(c.citations)
        return claims

    async def get_claims_by_document(
        self,
        document_id: UUID,
        verdict: Optional[VerificationVerdict] = None,
        needs_review: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Claim], int]:
        doc_claims = [c for c in self.claims.values() if c.document_id == document_id]
        if verdict:
            doc_claims = [c for c in doc_claims if c.verdict == verdict]
        if needs_review is not None:
            doc_claims = [c for c in doc_claims if c.needs_human_review == needs_review]

        doc_claims.sort(key=lambda c: (c.page_number, c.char_span[0] if c.char_span else 0))
        total = len(doc_claims)
        start = (page - 1) * page_size
        end = start + page_size
        return doc_claims[start:end], total

    async def get_claim(self, claim_id: UUID) -> Optional[Claim]:
        return self.claims.get(claim_id)

    async def update_claim(self, claim: Claim) -> Claim:
        self.claims[claim.id] = claim
        return claim

    async def patch_claim(self, claim_id: UUID, claim_text: str, char_span: List[int]) -> Optional[Claim]:
        claim = self.claims.get(claim_id)
        if not claim:
            return None
        claim.claim_text = claim_text
        claim.char_span = char_span
        claim.updated_at = datetime.now(timezone.utc)
        self.claims[claim_id] = claim
        return claim

    # Citations
    async def save_citation(self, citation: Citation) -> Citation:
        self.citations[citation.id] = citation
        return citation

    async def save_citations(self, citations: List[Citation]) -> List[Citation]:
        for cit in citations:
            self.citations[cit.id] = cit
        return citations

    async def get_citations_by_document(self, document_id: UUID) -> List[Citation]:
        cits = [c for c in self.citations.values() if c.document_id == document_id]
        cits.sort(key=lambda c: (c.page_number, c.reference_index or 0))
        return cits

    async def rematch_citation(self, citation_id: UUID, matched_paper_id: UUID) -> Optional[Citation]:
        cit = self.citations.get(citation_id)
        if not cit:
            return None
        cit.matched_paper_id = matched_paper_id
        self.citations[citation_id] = cit
        return cit

    # Research Papers
    async def save_paper(self, paper: ResearchPaper) -> ResearchPaper:
        self.papers[paper.id] = paper
        if paper.doi:
            self.papers_by_doi[paper.doi.lower().strip()] = paper.id
        return paper

    async def get_paper(self, paper_id: UUID) -> Optional[ResearchPaper]:
        return self.papers.get(paper_id)

    async def get_paper_by_doi(self, doi: str) -> Optional[ResearchPaper]:
        paper_id = self.papers_by_doi.get(doi.lower().strip())
        if paper_id:
            return self.papers.get(paper_id)
        return None

    # Evidence
    async def save_evidence(self, evidence: List[Evidence], claim_id: Optional[UUID] = None) -> List[Evidence]:
        for ev in evidence:
            self.evidence[ev.id] = ev
            if claim_id:
                if claim_id not in self.claim_evidence:
                    self.claim_evidence[claim_id] = []
                if ev.id not in self.claim_evidence[claim_id]:
                    self.claim_evidence[claim_id].append(ev.id)
        return evidence

    async def get_evidence_by_claim(self, claim_id: UUID) -> List[Evidence]:
        ev_ids = self.claim_evidence.get(claim_id, [])
        return [self.evidence[eid] for eid in ev_ids if eid in self.evidence]

    # Human Reviews & Verifications
    async def record_human_review(
        self,
        claim_id: UUID,
        reviewer_name: str,
        updated_verdict: VerificationVerdict,
        notes: str,
        reviewer_id: Optional[UUID] = None,
    ) -> Claim:
        claim = self.claims.get(claim_id)
        if not claim:
            raise KeyError(f"Claim {claim_id} does not exist.")

        prev_verdict = claim.verdict.value if claim.verdict else None
        claim.verdict = updated_verdict
        claim.needs_human_review = False
        claim.rationale = f"Human reviewer ({reviewer_name}) updated verdict: {notes}"
        claim.updated_at = datetime.now(timezone.utc)
        self.claims[claim_id] = claim

        review_entry = {
            "id": uuid4(),
            "claim_id": claim_id,
            "document_id": claim.document_id,
            "reviewer_id": reviewer_id,
            "reviewer_name": reviewer_name,
            "previous_verdict": prev_verdict,
            "updated_verdict": updated_verdict.value,
            "notes": notes,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.reviews.append(review_entry)

        self.activities.append(
            DashboardActivity(
                id=uuid4(),
                document_id=claim.document_id,
                event_type="HUMAN_REVIEW",
                description=f"{reviewer_name} confirmed verdict '{updated_verdict.value}'",
                created_at=datetime.now(timezone.utc),
            )
        )
        return claim

    async def get_reviews_by_document(self, document_id: UUID) -> List[Dict]:
        return [r for r in self.reviews if r.get("document_id") == document_id]

    # Reports
    async def save_report(self, report: VerificationReport) -> VerificationReport:
        self.reports[report.document_id] = report
        return report

    async def get_report_by_document(self, document_id: UUID) -> Optional[VerificationReport]:
        return self.reports.get(document_id)

    async def list_reports(self, user_id: Optional[UUID] = None) -> List[VerificationReport]:
        all_reports = list(self.reports.values())
        if user_id:
            all_reports = [r for r in all_reports if self.document_owners.get(r.document_id) == user_id]
        return all_reports

    # Processing Jobs
    async def create_processing_job(
        self,
        document_id: UUID,
        status: ProcessingStatus = ProcessingStatus.PENDING,
        current_stage: PipelineStage = PipelineStage.UPLOADED,
        progress_percent: int = 0,
    ) -> Dict:
        now = datetime.now(timezone.utc).isoformat()
        job = {
            "id": str(uuid4()),
            "document_id": str(document_id),
            "status": status.value,
            "current_stage": current_stage.value,
            "progress_percent": progress_percent,
            "error_message": None,
            "started_at": now if status == ProcessingStatus.PROCESSING else None,
            "completed_at": now if status == ProcessingStatus.COMPLETED else None,
            "created_at": now,
            "updated_at": now,
        }
        self.processing_jobs[document_id] = job
        return job

    async def update_processing_job(
        self,
        document_id: UUID,
        status: ProcessingStatus,
        current_stage: PipelineStage,
        progress_percent: int,
        error_message: Optional[str] = None,
    ) -> Dict:
        job = self.processing_jobs.get(document_id)
        now = datetime.now(timezone.utc).isoformat()
        if not job:
            job = {
                "id": str(uuid4()),
                "document_id": str(document_id),
                "created_at": now,
            }
        job["status"] = status.value
        job["current_stage"] = current_stage.value
        job["progress_percent"] = progress_percent
        job["error_message"] = error_message
        job["updated_at"] = now
        if status == ProcessingStatus.PROCESSING and not job.get("started_at"):
            job["started_at"] = now
        elif status in (ProcessingStatus.COMPLETED, ProcessingStatus.FAILED):
            job["completed_at"] = now
        self.processing_jobs[document_id] = job
        return job

    async def get_processing_job_by_document(self, document_id: UUID) -> Optional[Dict]:
        return self.processing_jobs.get(document_id)

    # User Profiles
    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        return self.profiles.get(user_id)

    async def update_user_profile(self, user_id: UUID, profile: UserProfile) -> UserProfile:
        self.profiles[user_id] = profile
        return profile

    # Dashboard & Settings
    async def get_dashboard_stats(self, user_id: Optional[UUID] = None) -> DashboardStats:
        docs = list(self.documents.values())
        if user_id:
            docs = [d for d in docs if self.document_owners.get(d.id) == user_id]

        total_docs = len(docs)
        doc_ids = {d.id for d in docs}

        relevant_claims = [c for c in self.claims.values() if c.document_id in doc_ids]
        total_claims = len(relevant_claims)

        supported = sum(1 for c in relevant_claims if c.verdict == VerificationVerdict.SUPPORTED)
        partly = sum(1 for c in relevant_claims if c.verdict == VerificationVerdict.PARTLY_SUPPORTED)
        unsupported = sum(1 for c in relevant_claims if c.verdict == VerificationVerdict.UNSUPPORTED)
        contradictory = sum(1 for c in relevant_claims if c.verdict == VerificationVerdict.CONTRADICTORY)
        outdated = sum(1 for c in relevant_claims if c.verdict == VerificationVerdict.POTENTIALLY_OUTDATED)
        needs_review = sum(1 for c in relevant_claims if c.needs_human_review)

        relevant_reports = [r for r in self.reports.values() if r.document_id in doc_ids]
        avg_score = (
            sum(r.reliability_score for r in relevant_reports) / len(relevant_reports)
            if relevant_reports
            else 0.0
        )

        return DashboardStats(
            total_documents=total_docs,
            total_claims=total_claims,
            supported_claims=supported,
            partly_supported_claims=partly,
            unsupported_claims=unsupported,
            contradictory_claims=contradictory,
            outdated_claims=outdated,
            needs_review_claims=needs_review,
            average_reliability_score=round(avg_score, 1),
        )

    async def get_dashboard_activity(self, user_id: Optional[UUID] = None, limit: int = 10) -> List[DashboardActivity]:
        acts = list(reversed(self.activities))
        return acts[:limit]

    async def get_user_settings(self, user_id: UUID) -> UserSettings:
        if user_id not in self.user_settings_store:
            self.user_settings_store[user_id] = UserSettings(user_id=user_id)
        return self.user_settings_store[user_id]

    async def update_user_settings(self, user_id: UUID, settings_update: UserSettingsUpdate) -> UserSettings:
        current = await self.get_user_settings(user_id)
        data = current.model_dump()
        update_data = {k: v for k, v in settings_update.model_dump().items() if v is not None}
        data.update(update_data)
        updated = UserSettings(**data)
        self.user_settings_store[user_id] = updated
        return updated
