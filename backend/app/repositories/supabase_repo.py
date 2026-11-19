"""
Supabase PostgreSQL repository implementation with Row-Level Security (RLS) enforcement.
Uses supabase-py client with service role key or forwarded user JWT.
Implements complete persistence for documents, claims, citations, claim_citations,
research_papers, evidence, verifications, human_reviews, reports, processing_jobs,
profiles, user_settings, and activity_log.
"""
import logging
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.core.config import settings
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

logger = logging.getLogger("citeverify.supabase_repo")


class SupabaseRepository(AbstractRepository):
    def __init__(self, client: Optional[Any] = None, jwt_token: Optional[str] = None):
        self.jwt_token = jwt_token
        self._client = client
        if self._client is None:
            self._init_client()

    def _init_client(self):
        if not settings.is_supabase_configured:
            raise RuntimeError(
                "CRITICAL: Supabase credentials are missing while REPOSITORY_BACKEND=supabase. "
                "Configure SUPABASE_URL and SUPABASE_SECRET_KEY."
            )

        try:
            from supabase import create_client
            key = settings.effective_supabase_secret_key or settings.effective_supabase_anon_key
            self._client = create_client(settings.SUPABASE_URL, key)
            if self.jwt_token and hasattr(self._client, "postgrest"):
                self._client.postgrest.auth(self.jwt_token)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise RuntimeError(f"Failed to initialize Supabase client: {e}")
            self._client = None

    @property
    def client(self):
        if not self._client:
            raise RuntimeError(
                "Supabase client is unconfigured or unavailable. Set SUPABASE_URL and service keys."
            )
        return self._client

    async def check_connection(self) -> Tuple[bool, str]:
        """
        Tests database readiness by verifying connection to Supabase and checking tables.
        Returns (True, 'OK') or (False, error_message).
        """
        if not settings.is_supabase_configured:
            return False, "Supabase credentials are not configured"
        try:
            res = self.client.table("documents").select("id").limit(1).execute()
            return True, "Connected and schema verified"
        except Exception as e:
            err = str(e)
            if "PGRST205" in err or "schema cache" in err:
                return False, "Database connected, but tables not found. Apply database/migrations/000_all_in_one.sql in Supabase SQL editor."
            return False, f"Database connection error: {err}"

    # --------------------------------------------------------------------------
    # 1. Documents
    # --------------------------------------------------------------------------
    async def create_document(self, document: Document, user_id: Optional[UUID] = None) -> Document:
        payload = document.model_dump(mode="json")
        if user_id:
            payload["user_id"] = str(user_id)
        res = self.client.table("documents").insert(payload).execute()
        created_doc = Document(**res.data[0]) if res.data else document

        # Log activity
        try:
            self.client.table("activity_log").insert({
                "user_id": str(user_id) if user_id else None,
                "document_id": str(document.id),
                "event_type": "DOCUMENT_UPLOAD",
                "description": f"Uploaded manuscript: {document.filename}",
            }).execute()
        except Exception as e:
            logger.warning(f"Could not write to activity_log: {e}")

        return created_doc

    async def get_document(self, document_id: UUID) -> Optional[Document]:
        res = self.client.table("documents").select("*").eq("id", str(document_id)).execute()
        if res.data:
            return Document(**res.data[0])
        return None

    async def get_document_owner(self, document_id: UUID) -> Optional[UUID]:
        res = self.client.table("documents").select("user_id").eq("id", str(document_id)).execute()
        if res.data and res.data[0].get("user_id"):
            return UUID(res.data[0]["user_id"])
        return None

    async def update_document(self, document: Document) -> Document:
        payload = document.model_dump(mode="json")
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = self.client.table("documents").update(payload).eq("id", str(document.id)).execute()
        updated_doc = Document(**res.data[0]) if res.data else document

        # Log activity on completion
        if document.status == ProcessingStatus.COMPLETED:
            try:
                owner_id = await self.get_document_owner(document.id)
                self.client.table("activity_log").insert({
                    "user_id": str(owner_id) if owner_id else None,
                    "document_id": str(document.id),
                    "event_type": "ANALYSIS_COMPLETED",
                    "description": f"Completed verification analysis for: {document.filename}",
                }).execute()
            except Exception as e:
                logger.warning(f"Could not write completion to activity_log: {e}")

        return updated_doc

    async def delete_document(self, document_id: UUID) -> bool:
        res = self.client.table("documents").delete().eq("id", str(document_id)).execute()
        return bool(res.data)

    async def list_documents(
        self, user_id: Optional[UUID] = None, page: int = 1, page_size: int = 20
    ) -> Tuple[List[Document], int]:
        query = self.client.table("documents").select("*", count="exact")
        if user_id:
            query = query.eq("user_id", str(user_id))

        start = (page - 1) * page_size
        end = start + page_size - 1
        res = query.order("created_at", desc=True).range(start, end).execute()
        docs = [Document(**d) for d in res.data]
        total = res.count or len(docs)
        return docs, total

    # --------------------------------------------------------------------------
    # 2. Claims & Hydration
    # --------------------------------------------------------------------------
    async def save_claims(self, claims: List[Claim]) -> List[Claim]:
        if not claims:
            return []

        now_iso = datetime.now(timezone.utc).isoformat()
        # 1. Upsert claims table
        claim_payloads = []
        for c in claims:
            p = c.model_dump(mode="json", exclude={"citations", "evidence"})
            if not p.get("created_at"):
                p["created_at"] = now_iso
            if not p.get("updated_at"):
                p["updated_at"] = now_iso
            claim_payloads.append(p)
        self.client.table("claims").upsert(claim_payloads).execute()

        # 2. Persist attached evidence and claim_citations
        for c in claims:
            if c.evidence:
                await self.save_evidence(c.evidence, claim_id=c.id)

            if c.citations:
                await self.save_citations(c.citations)
                link_payloads = [
                    {
                        "claim_id": str(c.id),
                        "citation_id": str(cit.id),
                        "link_method": "proximity",
                    }
                    for cit in c.citations
                ]
                try:
                    self.client.table("claim_citations").upsert(link_payloads).execute()
                except Exception as e:
                    logger.warning(f"Could not persist claim_citations: {e}")

            # 3. Save audit record in verifications table if evaluated
            if c.verification_state and c.verification_state.value != "PENDING":
                try:
                    self.client.table("verifications").insert({
                        "claim_id": str(c.id),
                        "verdict": c.verdict.value if c.verdict else None,
                        "verification_state": c.verification_state.value,
                        "confidence": c.confidence,
                        "rationale": c.rationale,
                        "needs_human_review": c.needs_human_review,
                        "review_reasons": c.review_reasons,
                        "is_latest": True,
                    }).execute()
                except Exception as e:
                    logger.warning(f"Could not record verification audit entry: {e}")

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

        # Hydrate evidence and citations for returned claims
        if claims:
            claim_ids = [str(c.id) for c in claims]
            try:
                ev_res = self.client.table("evidence").select("*").in_("claim_id", claim_ids).execute()
                ev_map: Dict[str, List[Evidence]] = {}
                for ev_raw in ev_res.data:
                    cid = ev_raw.get("claim_id")
                    if cid:
                        ev_map.setdefault(cid, []).append(Evidence(**ev_raw))
                for c in claims:
                    c.evidence = ev_map.get(str(c.id), [])
            except Exception as e:
                logger.warning(f"Failed to hydrate claim evidence: {e}")

            try:
                cc_res = self.client.table("claim_citations").select("claim_id, citations(*)").in_("claim_id", claim_ids).execute()
                cit_map: Dict[str, List[Citation]] = {}
                for cc in cc_res.data:
                    cid = cc.get("claim_id")
                    cit_data = cc.get("citations")
                    if cid and cit_data:
                        cit_map.setdefault(cid, []).append(Citation(**cit_data))
                for c in claims:
                    c.citations = cit_map.get(str(c.id), [])
            except Exception as e:
                logger.warning(f"Failed to hydrate claim citations: {e}")

        return claims, total

    async def get_claim(self, claim_id: UUID) -> Optional[Claim]:
        res = self.client.table("claims").select("*").eq("id", str(claim_id)).execute()
        if not res.data:
            return None
        claim = Claim(**res.data[0])

        # Hydrate evidence
        try:
            ev_res = self.client.table("evidence").select("*").eq("claim_id", str(claim_id)).execute()
            claim.evidence = [Evidence(**e) for e in ev_res.data]
        except Exception:
            pass

        # Hydrate citations
        try:
            cc_res = self.client.table("claim_citations").select("citations(*)").eq("claim_id", str(claim_id)).execute()
            cits = []
            for cc in cc_res.data:
                cit_data = cc.get("citations")
                if cit_data:
                    cits.append(Citation(**cit_data))
            claim.citations = cits
        except Exception:
            pass

        return claim

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
            return await self.get_claim(claim_id)
        return None

    # --------------------------------------------------------------------------
    # 3. Citations
    # --------------------------------------------------------------------------
    async def save_citation(self, citation: Citation) -> Citation:
        payload = citation.model_dump(mode="json")
        if not payload.get("created_at"):
            payload["created_at"] = datetime.now(timezone.utc).isoformat()
        res = self.client.table("citations").upsert(payload).execute()
        if res.data:
            return Citation(**res.data[0])
        return citation

    async def save_citations(self, citations: List[Citation]) -> List[Citation]:
        if not citations:
            return []
        now_iso = datetime.now(timezone.utc).isoformat()
        payloads = []
        for c in citations:
            p = c.model_dump(mode="json")
            if not p.get("created_at"):
                p["created_at"] = now_iso
            payloads.append(p)
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

    # --------------------------------------------------------------------------
    # 4. Research Papers
    # --------------------------------------------------------------------------
    async def save_paper(self, paper: ResearchPaper) -> ResearchPaper:
        doi = str(paper.doi).strip().lower() if paper.doi and str(paper.doi).strip() else None
        now_iso = datetime.now(timezone.utc).isoformat()

        if doi:
            existing = self.client.table("research_papers").select("*").eq("doi", doi).limit(1).execute()
            if existing.data:
                existing_id = existing.data[0]["id"]
                payload = paper.model_dump(mode="json")
                payload["id"] = existing_id
                payload["doi"] = doi
                payload["retrieved_at"] = now_iso
                res = self.client.table("research_papers").update(payload).eq("id", existing_id).execute()
                if res.data:
                    return ResearchPaper(**res.data[0])
                paper.id = UUID(existing_id)
                return paper

        payload = paper.model_dump(mode="json")
        payload["doi"] = doi
        if not payload.get("retrieved_at"):
            payload["retrieved_at"] = now_iso

        res = self.client.table("research_papers").upsert(payload, on_conflict="id").execute()
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

    # --------------------------------------------------------------------------
    # 5. Evidence
    # --------------------------------------------------------------------------
    async def save_evidence(self, evidence: List[Evidence], claim_id: Optional[UUID] = None) -> List[Evidence]:
        if not evidence:
            return []
        now_iso = datetime.now(timezone.utc).isoformat()
        payloads = []
        for ev in evidence:
            p = ev.model_dump(mode="json")
            if claim_id:
                p["claim_id"] = str(claim_id)
            if not p.get("created_at"):
                p["created_at"] = now_iso
            payloads.append(p)
        self.client.table("evidence").upsert(payloads).execute()
        return evidence

    async def get_evidence_by_claim(self, claim_id: UUID) -> List[Evidence]:
        res = self.client.table("evidence").select("*").eq("claim_id", str(claim_id)).execute()
        return [Evidence(**e) for e in res.data]

    # --------------------------------------------------------------------------
    # 6. Human Reviews
    # --------------------------------------------------------------------------
    async def record_human_review(
        self,
        claim_id: UUID,
        reviewer_name: str,
        updated_verdict: VerificationVerdict,
        notes: str,
        reviewer_id: Optional[UUID] = None,
    ) -> Claim:
        claim = await self.get_claim(claim_id)
        if not claim:
            raise KeyError(f"Claim {claim_id} not found.")

        prev_verdict = claim.verdict.value if claim.verdict else None
        claim.verdict = updated_verdict
        claim.needs_human_review = False
        claim.rationale = f"Human reviewer ({reviewer_name}) updated verdict: {notes}"
        claim.updated_at = datetime.now(timezone.utc)
        await self.update_claim(claim)

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

        try:
            self.client.table("activity_log").insert({
                "user_id": str(reviewer_id) if reviewer_id else None,
                "document_id": str(claim.document_id),
                "event_type": "HUMAN_REVIEW",
                "description": f"{reviewer_name} confirmed verdict '{updated_verdict.value}'",
            }).execute()
        except Exception as e:
            logger.warning(f"Could not log human review activity: {e}")

        return claim

    async def get_reviews_by_document(self, document_id: UUID) -> List[Dict]:
        claims_res = self.client.table("claims").select("id").eq("document_id", str(document_id)).execute()
        claim_ids = [str(c["id"]) for c in claims_res.data]
        if not claim_ids:
            return []
        res = self.client.table("human_reviews").select("*").in_("claim_id", claim_ids).execute()
        return res.data

    # --------------------------------------------------------------------------
    # 7. Reports
    # --------------------------------------------------------------------------
    async def save_report(self, report: VerificationReport) -> VerificationReport:
        doc_id_str = str(report.document_id)
        existing = (
            self.client.table("reports")
            .select("id")
            .eq("document_id", doc_id_str)
            .limit(1)
            .execute()
        )
        payload = {
            "document_id": doc_id_str,
            "filename": report.filename,
            "total_claims": report.total_claims,
            "reliability_score": report.reliability_score,
            "verdict_counts": report.verdict_counts,
            "evidence_level_counts": report.evidence_level_counts,
            "human_review_required_count": report.human_review_required_count,
            "claims_snapshot": [c.model_dump(mode="json") for c in report.claims],
            "generated_at": report.generated_at.isoformat(),
        }
        if existing.data:
            report_id = existing.data[0]["id"]
            self.client.table("reports").update(payload).eq("id", report_id).execute()
        else:
            payload["id"] = str(uuid4())
            self.client.table("reports").insert(payload).execute()
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
        if user_id:
            docs_res = self.client.table("documents").select("id").eq("user_id", str(user_id)).execute()
            doc_ids = [str(d["id"]) for d in docs_res.data]
            if not doc_ids:
                return []
            res = self.client.table("reports").select("*").in_("document_id", doc_ids).execute()
        else:
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

    # --------------------------------------------------------------------------
    # 8. Processing Jobs
    # --------------------------------------------------------------------------
    async def create_processing_job(
        self,
        document_id: UUID,
        status: ProcessingStatus = ProcessingStatus.PENDING,
        current_stage: PipelineStage = PipelineStage.UPLOADED,
        progress_percent: int = 0,
    ) -> Dict:
        now = datetime.now(timezone.utc).isoformat()
        doc_id_str = str(document_id)
        existing = (
            self.client.table("processing_jobs")
            .select("id")
            .eq("document_id", doc_id_str)
            .limit(1)
            .execute()
        )
        payload = {
            "document_id": doc_id_str,
            "status": status.value,
            "current_stage": current_stage.value,
            "progress_percent": progress_percent,
            "error_message": None,
            "started_at": now if status == ProcessingStatus.PROCESSING else None,
            "completed_at": now if status == ProcessingStatus.COMPLETED else None,
            "updated_at": now,
        }
        if existing.data:
            job_id = existing.data[0]["id"]
            res = self.client.table("processing_jobs").update(payload).eq("id", job_id).execute()
        else:
            payload["id"] = str(uuid4())
            payload["created_at"] = now
            res = self.client.table("processing_jobs").insert(payload).execute()
        return res.data[0] if res.data else payload

    async def update_processing_job(
        self,
        document_id: UUID,
        status: ProcessingStatus,
        current_stage: PipelineStage,
        progress_percent: int,
        error_message: Optional[str] = None,
    ) -> Dict:
        now = datetime.now(timezone.utc).isoformat()
        doc_id_str = str(document_id)
        payload = {
            "status": status.value,
            "current_stage": current_stage.value,
            "progress_percent": progress_percent,
            "error_message": error_message,
            "updated_at": now,
        }
        if status == ProcessingStatus.PROCESSING:
            payload["started_at"] = now
        elif status in (ProcessingStatus.COMPLETED, ProcessingStatus.FAILED):
            payload["completed_at"] = now

        res = self.client.table("processing_jobs").update(payload).eq("document_id", doc_id_str).execute()
        if res.data:
            return res.data[0]

        # If job didn't exist yet, insert it
        payload["id"] = str(uuid4())
        payload["document_id"] = doc_id_str
        payload["created_at"] = now
        res = self.client.table("processing_jobs").insert(payload).execute()
        return res.data[0] if res.data else payload

    async def get_processing_job_by_document(self, document_id: UUID) -> Optional[Dict]:
        res = self.client.table("processing_jobs").select("*").eq("document_id", str(document_id)).execute()
        if res.data:
            return res.data[0]
        return None

    # --------------------------------------------------------------------------
    # 9. User Profiles
    # --------------------------------------------------------------------------
    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        res = self.client.table("profiles").select("*").eq("id", str(user_id)).execute()
        if res.data:
            return UserProfile(**res.data[0])
        return None

    async def update_user_profile(self, user_id: UUID, profile: UserProfile) -> UserProfile:
        payload = profile.model_dump(mode="json")
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = self.client.table("profiles").upsert(payload).execute()
        if res.data:
            return UserProfile(**res.data[0])
        return profile

    # --------------------------------------------------------------------------
    # 10. Dashboard & User Settings
    # --------------------------------------------------------------------------
    async def get_dashboard_stats(self, user_id: Optional[UUID] = None) -> DashboardStats:
        docs_res = self.client.table("documents").select("id", count="exact")
        if user_id:
            docs_res = docs_res.eq("user_id", str(user_id))
        docs_data = docs_res.execute()
        total_docs = docs_data.count or len(docs_data.data)

        # Scoped claims and reports count
        if user_id:
            doc_ids = [str(d["id"]) for d in docs_data.data]
            if doc_ids:
                claims_res = self.client.table("claims").select("verdict, needs_human_review").in_("document_id", doc_ids).execute()
                reports_res = self.client.table("reports").select("reliability_score").in_("document_id", doc_ids).execute()
            else:
                claims_res = self.client.table("claims").select("verdict").eq("id", "00000000-0000-0000-0000-000000000000").execute()
                reports_res = self.client.table("reports").select("reliability_score").eq("id", "00000000-0000-0000-0000-000000000000").execute()
        else:
            claims_res = self.client.table("claims").select("verdict, needs_human_review").execute()
            reports_res = self.client.table("reports").select("reliability_score").execute()

        claims = claims_res.data
        total_claims = len(claims)

        supported = sum(1 for c in claims if c.get("verdict") == "SUPPORTED")
        partly = sum(1 for c in claims if c.get("verdict") == "PARTLY_SUPPORTED")
        unsupported = sum(1 for c in claims if c.get("verdict") == "UNSUPPORTED")
        contradictory = sum(1 for c in claims if c.get("verdict") == "CONTRADICTORY")
        outdated = sum(1 for c in claims if c.get("verdict") == "POTENTIALLY_OUTDATED")
        needs_review = sum(1 for c in claims if c.get("needs_human_review"))

        scores = [r.get("reliability_score", 0.0) for r in reports_res.data if r.get("reliability_score") is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

        return DashboardStats(
            total_documents=total_docs,
            total_claims=total_claims,
            supported_claims=supported,
            partly_supported_claims=partly,
            unsupported_claims=unsupported,
            contradictory_claims=contradictory,
            outdated_claims=outdated,
            needs_review_claims=needs_review,
            average_reliability_score=avg_score,
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
