"""
Repository abstraction and in-memory default implementation.
Enables full local development without external database credentials.
PostgreSQL/Supabase implementations can plug in behind this interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.citation import Citation
from app.schemas.research_paper import ResearchPaper
from app.schemas.evidence import Evidence
from app.schemas.verification import Verification
from app.schemas.enums import VerificationVerdict


class AbstractRepository(ABC):
    @abstractmethod
    async def create_document(self, document: Document) -> Document:
        pass

    @abstractmethod
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        pass

    @abstractmethod
    async def update_document(self, document: Document) -> Document:
        pass

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
    ) -> (List[Claim], int):
        pass

    @abstractmethod
    async def get_claim(self, claim_id: UUID) -> Optional[Claim]:
        pass

    @abstractmethod
    async def update_claim(self, claim: Claim) -> Claim:
        pass

    @abstractmethod
    async def save_citation(self, citation: Citation) -> Citation:
        pass

    @abstractmethod
    async def get_citations_by_document(self, document_id: UUID) -> List[Citation]:
        pass

    @abstractmethod
    async def save_paper(self, paper: ResearchPaper) -> ResearchPaper:
        pass

    @abstractmethod
    async def get_paper(self, paper_id: UUID) -> Optional[ResearchPaper]:
        pass

    @abstractmethod
    async def record_human_review(
        self,
        claim_id: UUID,
        reviewer_name: str,
        updated_verdict: VerificationVerdict,
        notes: str,
    ) -> Claim:
        pass


class InMemoryRepository(AbstractRepository):
    """
    Default in-memory repository store with dictionary indexes.
    Thread-safe for single-process async event loops.
    """
    def __init__(self):
        self.documents: Dict[UUID, Document] = {}
        self.claims: Dict[UUID, Claim] = {}
        self.citations: Dict[UUID, Citation] = {}
        self.papers: Dict[UUID, ResearchPaper] = {}
        self.evidence: Dict[UUID, Evidence] = {}
        self.reviews: List[Dict] = []

    async def create_document(self, document: Document) -> Document:
        self.documents[document.id] = document
        return document

    async def get_document(self, document_id: UUID) -> Optional[Document]:
        return self.documents.get(document_id)

    async def update_document(self, document: Document) -> Document:
        self.documents[document.id] = document
        return document

    async def save_claims(self, claims: List[Claim]) -> List[Claim]:
        for claim in claims:
            self.claims[claim.id] = claim
        return claims

    async def get_claims_by_document(
        self,
        document_id: UUID,
        verdict: Optional[VerificationVerdict] = None,
        needs_review: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> (List[Claim], int):
        matched = [
            c for c in self.claims.values()
            if c.document_id == document_id
        ]
        if verdict is not None:
            matched = [c for c in matched if c.verdict == verdict]
        if needs_review is not None:
            matched = [c for c in matched if c.needs_human_review == needs_review]

        total = len(matched)
        start = (page - 1) * page_size
        end = start + page_size
        return matched[start:end], total

    async def get_claim(self, claim_id: UUID) -> Optional[Claim]:
        return self.claims.get(claim_id)

    async def update_claim(self, claim: Claim) -> Claim:
        self.claims[claim.id] = claim
        return claim

    async def save_citation(self, citation: Citation) -> Citation:
        self.citations[citation.id] = citation
        return citation

    async def get_citations_by_document(self, document_id: UUID) -> List[Citation]:
        return [c for c in self.citations.values() if c.document_id == document_id]

    async def save_paper(self, paper: ResearchPaper) -> ResearchPaper:
        self.papers[paper.id] = paper
        return paper

    async def get_paper(self, paper_id: UUID) -> Optional[ResearchPaper]:
        return self.papers.get(paper_id)

    async def record_human_review(
        self,
        claim_id: UUID,
        reviewer_name: str,
        updated_verdict: VerificationVerdict,
        notes: str,
    ) -> Claim:
        claim = self.claims.get(claim_id)
        if not claim:
            raise KeyError(f"Claim {claim_id} not found.")
        claim.verdict = updated_verdict
        claim.needs_human_review = False
        self.reviews.append({
            "claim_id": str(claim_id),
            "reviewer_name": reviewer_name,
            "updated_verdict": updated_verdict.value,
            "notes": notes,
        })
        return claim


# Global repository instance selection
_repo_instance: Optional[AbstractRepository] = None


def get_repository() -> AbstractRepository:
    global _repo_instance
    if _repo_instance is None:
        # If DATABASE_URL is set later, PostgresRepository will be instantiated here.
        _repo_instance = InMemoryRepository()
    return _repo_instance

