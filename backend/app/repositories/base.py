"""
Abstract repository interface defining the data contract for CiteVerify AI.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from uuid import UUID

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


class AbstractRepository(ABC):
    # Documents
    @abstractmethod
    async def create_document(self, document: Document, user_id: Optional[UUID] = None) -> Document:
        pass

    @abstractmethod
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        pass

    @abstractmethod
    async def get_document_owner(self, document_id: UUID) -> Optional[UUID]:
        pass

    @abstractmethod
    async def update_document(self, document: Document) -> Document:
        pass

    @abstractmethod
    async def delete_document(self, document_id: UUID) -> bool:
        pass

    @abstractmethod
    async def list_documents(self, user_id: Optional[UUID] = None, page: int = 1, page_size: int = 20) -> Tuple[List[Document], int]:
        pass

    # Claims
    @abstractmethod
    async def save_claims(self, claims: List[Claim]) -> List[Claim]:
        pass

    @abstractmethod
    async def get_claims_by_document(
        self,
        document_id: UUID,
        verdict: Optional[VerificationVerdict] = None,
        needs_review: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Claim], int]:
        pass

    @abstractmethod
    async def get_claim(self, claim_id: UUID) -> Optional[Claim]:
        pass

    @abstractmethod
    async def update_claim(self, claim: Claim) -> Claim:
        pass

    @abstractmethod
    async def patch_claim(self, claim_id: UUID, claim_text: str, char_span: List[int]) -> Optional[Claim]:
        pass

    # Citations
    @abstractmethod
    async def save_citation(self, citation: Citation) -> Citation:
        pass

    @abstractmethod
    async def save_citations(self, citations: List[Citation]) -> List[Citation]:
        pass

    @abstractmethod
    async def get_citations_by_document(self, document_id: UUID) -> List[Citation]:
        pass

    @abstractmethod
    async def rematch_citation(self, citation_id: UUID, matched_paper_id: UUID) -> Optional[Citation]:
        pass

    # Research Papers
    @abstractmethod
    async def save_paper(self, paper: ResearchPaper) -> ResearchPaper:
        pass

    @abstractmethod
    async def get_paper(self, paper_id: UUID) -> Optional[ResearchPaper]:
        pass

    @abstractmethod
    async def get_paper_by_doi(self, doi: str) -> Optional[ResearchPaper]:
        pass

    # Evidence
    @abstractmethod
    async def save_evidence(self, evidence: List[Evidence], claim_id: Optional[UUID] = None) -> List[Evidence]:
        pass

    @abstractmethod
    async def get_evidence_by_claim(self, claim_id: UUID) -> List[Evidence]:
        pass

    # Human Reviews & Verifications
    @abstractmethod
    async def record_human_review(
        self,
        claim_id: UUID,
        reviewer_name: str,
        updated_verdict: VerificationVerdict,
        notes: str,
        reviewer_id: Optional[UUID] = None,
    ) -> Claim:
        pass

    @abstractmethod
    async def get_reviews_by_document(self, document_id: UUID) -> List[Dict]:
        pass

    # Reports
    @abstractmethod
    async def save_report(self, report: VerificationReport) -> VerificationReport:
        pass

    @abstractmethod
    async def get_report_by_document(self, document_id: UUID) -> Optional[VerificationReport]:
        pass

    @abstractmethod
    async def list_reports(self, user_id: Optional[UUID] = None) -> List[VerificationReport]:
        pass

    # Processing Jobs
    @abstractmethod
    async def create_processing_job(
        self,
        document_id: UUID,
        status: ProcessingStatus = ProcessingStatus.PENDING,
        current_stage: PipelineStage = PipelineStage.UPLOADED,
        progress_percent: int = 0,
    ) -> Dict:
        pass

    @abstractmethod
    async def update_processing_job(
        self,
        document_id: UUID,
        status: ProcessingStatus,
        current_stage: PipelineStage,
        progress_percent: int,
        error_message: Optional[str] = None,
    ) -> Dict:
        pass

    @abstractmethod
    async def get_processing_job_by_document(self, document_id: UUID) -> Optional[Dict]:
        pass

    # User Profiles
    @abstractmethod
    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        pass

    @abstractmethod
    async def update_user_profile(self, user_id: UUID, profile: UserProfile) -> UserProfile:
        pass

    # Dashboard & Settings
    @abstractmethod
    async def get_dashboard_stats(self, user_id: Optional[UUID] = None) -> DashboardStats:
        pass

    @abstractmethod
    async def get_dashboard_activity(self, user_id: Optional[UUID] = None, limit: int = 10) -> List[DashboardActivity]:
        pass

    @abstractmethod
    async def get_user_settings(self, user_id: UUID) -> UserSettings:
        pass

    @abstractmethod
    async def update_user_settings(self, user_id: UUID, settings_update: UserSettingsUpdate) -> UserSettings:
        pass
