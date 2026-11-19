"""
Supabase PostgreSQL repository implementation with Row-Level Security (RLS) enforcement.
Uses supabase-py client with service role key or forwarded user JWT.
"""
import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone

from app.core.config import settings
from app.repositories.base import AbstractRepository
from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.citation import Citation
from app.schemas.research_paper import ResearchPaper
from app.schemas.evidence import Evidence
from app.schemas.report import VerificationReport
from app.schemas.enums import VerificationVerdict
from app.schemas.dashboard import DashboardStats, DashboardActivity
from app.schemas.settings import UserSettings, UserSettingsUpdate

logger = logging.getLogger("citeverify.supabase_repo")


class SupabaseRepository(AbstractRepository):
    def __init__(self, jwt_token: Optional[str] = None):
        self.jwt_token = jwt_token
        self._client = None
        self._init_client()

    def _init_client(self):
        if not settings.is_supabase_configured:
            return

        try:
            from supabase import create_client, Client
            key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
            self._client = create_client(settings.SUPABASE_URL, key)
            if self.jwt_token and hasattr(self._client, "postgrest"):
                # Forward user's JWT to postgrest headers for RLS enforcement
                self._client.postgrest.auth(self.jwt_token)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self._client = None

    @property
    def client(self):
        if not self._client:
            raise RuntimeError("Supabase client is unconfigured or unavailable. Set SUPABASE_URL and service keys.")
        return self._client

    # Documents
    async def create_document(self, document: Document, user_id: Optional[UUID] = None) -> Document:
        payload = document.model_dump(mode="json")
        if user_id:
            payload["user_id"] = str(user_id)
        res = self.client.table("documents").insert(payload).execute()
        if res.data:
            return Document(**res.data[0])
        return document

    async def get_document(self, document_id: UUID) -> Optional[Document]:
        res = self.client.table("documents").select("*").eq("id", str(document_id)).execute()
        if res.data:
            return Document(**res.data[0])
        return None

    async def update_document(self, document: Document) -> Document:
        payload = document.model_dump(mode="json")
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = self.client.table("documents").update(payload).eq("id", str(document.id)).execute()
        if res.data:
            return Document(**res.data[0])
        return document

    async def delete_document(self, document_id: UUID) -> bool:
        res = self.client.table("documents").delete().eq("id", str(document_id)).execute()
        return bool(res.data)

    async def list_documents(self, user_id: Optional[UUID] = None, page: int = 1, page_size: int = 20) -> Tuple[List[Document], int]:
        query = self.client.table("documents").select("*", count="exact")
        if user_id:
            query = query.eq("user_id", str(user_id))

        start = (page - 1) * page_size
        end = start + page_size - 1
        res = query.order("created_at", desc=True).range(start, end).execute()
        docs = [Document(**d) for d in res.data]
        total = res.count or len(docs)
        return docs, total

    # Claims
    async def save_claims(self, claims: List[Claim]) -> List[Claim]:
        if not claims:
            return []
        payloads = [c.model_dump(mode="json", exclude={"citations", "evidence"}) for c in claims]
        res = self.client.table("claims").upsert(payloads).execute()
        return claims

    async def get_claims_by_document(
        self,
        document_id: UUID,
        verdict: Optional[VerificationVerdict] = None,
        needs_review: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Claim], int]:
        query = self.client.table("claims").select("*", count="exact").eq("document_id", str(document_id))
        if verdict:
            query = query.eq("verdict", verdict.value)
        if needs_review is not None:
            query = query.eq("needs_human_review", needs_review)

        start = (page - 1) * page_size
        end = start + page_size - 1
        res = query.order("page_number").range(start, end).execute()
        claims = [Claim(**c) for c in res.data]
        total = res.count or len(claims)
        return claims, total

    async def get_claim(self, claim_id: UUID) -> Optional[Claim]:
        res = self.client.table("claims").select("*").eq("id", str(claim_id)).execute()
        if res.data:
            return Claim(**res.data[0])
        return None

    async def update_claim(self, claim: Claim) -> Claim:
        payload = claim.model_dump(mode="json", exclude={"citations", "evidence"})
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = self.client.table("claims").update(payload).eq("id", str(claim.id)).execute()
        if res.data:
            return Claim(**res.data[0])
        return claim

    async def patch_claim(self, claim_id: UUID, claim_text: str, char_span: List[int]) -> Optional[Claim]:
        payload = {
            "claim_text": claim_text,
            "char_span": char_span,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        res = self.client.table("claims").update(payload).eq("id", str(claim_id)).execute()
        if res.data:
            return Claim(**res.data[0])
        return None

    # Citations
    async def save_citation(self, citation: Citation) -> Citation:
        payload = citation.model_dump(mode="json")
        res = self.client.table("citations").upsert(payload).execute()
        if res.data:
            return Citation(**res.data[0])
        return citation

    async def save_citations(self, citations: List[Citation]) -> List[Citation]:
        if not citations:
            return []
        payloads = [c.model_dump(mode="json") for c in citations]
        self.client.table("citations").upsert(payloads).execute()
        return citations

    async def get_citations_by_document(self, document_id: UUID) -> List[Citation]:
        res = self.client.table("citations").select("*").eq("document_id", str(document_id)).order("page_number").execute()
        return [Citation(**c) for c in res.data]

    async def rematch_citation(self, citation_id: UUID, matched_paper_id: UUID) -> Optional[Citation]:
        res = self.client.table("citations").update({"matched_paper_id": str(matched_paper_id)}).eq("id", str(citation_id)).execute()
        if res.data:
            return Citation(**res.data[0])
        return None

    # Research Papers
    async def save_paper(self, paper: ResearchPaper) -> ResearchPaper:
        payload = paper.model_dump(mode="json")
        res = self.client.table("research_papers").upsert(payload).execute()
        if res.data:
            return ResearchPaper(**res.data[0])
        return paper

    async def get_paper(self, paper_id: UUID) -> Optional[ResearchPaper]:
        res = self.client.table("research_papers").select("*").eq("id", str(paper_id)).execute()
        if res.data:
            return ResearchPaper(**res.data[0])
        return None

    async def get_paper_by_doi(self, doi: str) -> Optional[ResearchPaper]:
        res = self.client.table("research_papers").select("*").eq("doi", doi.strip().lower()).execute()
        if res.data:
            return ResearchPaper(**res.data[0])
        return None

    # Evidence
    async def save_evidence(self, evidence: List[Evidence], claim_id: Optional[UUID] = None) -> List[Evidence]:
        if not evidence:
            return []
        payloads = []
        for ev in evidence:
            p = ev.model_dump(mode="json")
            if claim_id:
                p["claim_id"] = str(claim_id)
            payloads.append(p)
        self.client.table("evidence").upsert(payloads).execute()
        return evidence

    async def get_evidence_by_claim(self, claim_id: UUID) -> List[Evidence]:
        res = self.client.table("evidence").select("*").eq("claim_id", str(claim_id)).execute()
        return [Evidence(**e) for e in res.data]

    # Human Reviews
    async def record_human_review(
        self,
        claim_id: UUID,
        reviewer_name: str,
        updated_verdict: VerificationVerdict,
        notes: str,
        reviewer_id: Optional[UUID] = None,
    ) -> Claim:
        # 1. Update claim
        claim = await self.get_claim(claim_id)
        if not claim:
            raise KeyError(f"Claim {claim_id} not found.")

        prev_verdict = claim.verdict.value if claim.verdict else None
        claim.verdict = updated_verdict
        claim.needs_human_review = False
        claim.rationale = f"Human reviewer ({reviewer_name}) updated verdict: {notes}"
        await self.update_claim(claim)

        # 2. Insert review log
        review_payload = {
            "claim_id": str(claim_id),
            "reviewer_name": reviewer_name,
            "previous_verdict": prev_verdict,
            "updated_verdict": updated_verdict.value,
            "notes": notes,
        }
        if reviewer_id:
            review_payload["reviewer_id"] = str(reviewer_id)

        self.client.table("human_reviews").insert(review_payload).execute()
        return claim

    async def get_reviews_by_document(self, document_id: UUID) -> List[Dict]:
        res = self.client.table("human_reviews").select("*, claims!inner(document_id)").eq("claims.document_id", str(document_id)).execute()
        return res.data

    # Reports
    async def save_report(self, report: VerificationReport) -> VerificationReport:
        payload = {
            "document_id": str(report.document_id),
            "filename": report.filename,
            "total_claims": report.total_claims,
            "reliability_score": report.reliability_score,
            "verdict_counts": report.verdict_counts,
            "evidence_level_counts": report.evidence_level_counts,
            "human_review_required_count": report.human_review_required_count,
            "claims_snapshot": [c.model_dump(mode="json") for c in report.claims],
            "generated_at": report.generated_at.isoformat(),
        }
        self.client.table("reports").upsert(payload, on_conflict="document_id").execute()
        return report

    async def get_report_by_document(self, document_id: UUID) -> Optional[VerificationReport]:
        res = self.client.table("reports").select("*").eq("document_id", str(document_id)).execute()
        if res.data:
            data = res.data[0]
            claims = [Claim(**c) for c in data.get("claims_snapshot", [])]
            return VerificationReport(
                document_id=UUID(data["document_id"]),
                filename=data["filename"],
                generated_at=data["generated_at"],
                total_claims=data["total_claims"],
                reliability_score=data["reliability_score"],
                verdict_counts=data["verdict_counts"],
                evidence_level_counts=data["evidence_level_counts"],
                human_review_required_count=data["human_review_required_count"],
                claims=claims,
            )
        return None

    async def list_reports(self, user_id: Optional[UUID] = None) -> List[VerificationReport]:
        res = self.client.table("reports").select("*").execute()
        reports = []
        for data in res.data:
            claims = [Claim(**c) for c in data.get("claims_snapshot", [])]
            reports.append(
                VerificationReport(
                    document_id=UUID(data["document_id"]),
                    filename=data["filename"],
                    generated_at=data["generated_at"],
                    total_claims=data["total_claims"],
                    reliability_score=data["reliability_score"],
                    verdict_counts=data["verdict_counts"],
                    evidence_level_counts=data["evidence_level_counts"],
                    human_review_required_count=data["human_review_required_count"],
                    claims=claims,
                )
            )
        return reports

    # Dashboard & Settings
    async def get_dashboard_stats(self, user_id: Optional[UUID] = None) -> DashboardStats:
        docs_res = self.client.table("documents").select("id", count="exact")
        if user_id:
            docs_res = docs_res.eq("user_id", str(user_id))
        docs_data = docs_res.execute()
        total_docs = docs_data.count or len(docs_data.data)

        claims_res = self.client.table("claims").select("verdict, needs_human_review").execute()
        claims = claims_res.data
        total_claims = len(claims)

        supported = sum(1 for c in claims if c.get("verdict") == "SUPPORTED")
        partly = sum(1 for c in claims if c.get("verdict") == "PARTLY_SUPPORTED")
        unsupported = sum(1 for c in claims if c.get("verdict") == "UNSUPPORTED")
        contradictory = sum(1 for c in claims if c.get("verdict") == "CONTRADICTORY")
        outdated = sum(1 for c in claims if c.get("verdict") == "POTENTIALLY_OUTDATED")
        needs_review = sum(1 for c in claims if c.get("needs_human_review"))

        return DashboardStats(
            total_documents=total_docs,
            total_claims=total_claims,
            supported_claims=supported,
            partly_supported_claims=partly,
            unsupported_claims=unsupported,
            contradictory_claims=contradictory,
            outdated_claims=outdated,
            needs_review_claims=needs_review,
            average_reliability_score=0.0,
        )

    async def get_dashboard_activity(self, user_id: Optional[UUID] = None, limit: int = 10) -> List[DashboardActivity]:
        query = self.client.table("activity_log").select("*").order("created_at", desc=True).limit(limit)
        if user_id:
            query = query.eq("user_id", str(user_id))
        res = query.execute()
        return [DashboardActivity(**a) for a in res.data]

    async def get_user_settings(self, user_id: UUID) -> UserSettings:
        res = self.client.table("user_settings").select("*").eq("user_id", str(user_id)).execute()
        if res.data:
            return UserSettings(**res.data[0])
        return UserSettings(user_id=user_id)

    async def update_user_settings(self, user_id: UUID, settings_update: UserSettingsUpdate) -> UserSettings:
        current = await self.get_user_settings(user_id)
        data = current.model_dump(mode="json")
        data.update({k: v for k, v in settings_update.model_dump(mode="json").items() if v is not None})
        self.client.table("user_settings").upsert(data).execute()
        return UserSettings(**data)
