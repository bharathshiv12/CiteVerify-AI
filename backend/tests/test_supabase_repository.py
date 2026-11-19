"""
Unit and integration tests for SupabaseRepository.
Tests full CRUD, relational linking, hydration, ownership, and persistence lifecycle
using a mock Supabase/PostgREST client matching Supabase 2024+ schemas.
"""
import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from app.repositories.supabase_repo import SupabaseRepository
from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.citation import Citation
from app.schemas.research_paper import ResearchPaper
from app.schemas.evidence import Evidence
from app.schemas.report import VerificationReport
from app.schemas.enums import (
    ProcessingStatus,
    PipelineStage,
    VerificationVerdict,
    VerificationState,
    EvidenceLevel,
    RetrievalStatus,
)
from app.schemas.settings import UserSettingsUpdate
from app.schemas.user import UserProfile


class MockPostgrestResponse:
    def __init__(self, data: List[Dict[str, Any]], count: Optional[int] = None):
        self.data = data
        self.count = count if count is not None else len(data)


class MockTableQuery:
    def __init__(self, table_name: str, store: Dict[str, List[Dict[str, Any]]]):
        self.table_name = table_name
        self.store = store
        self.filters = []
        self._order_by = None
        self._desc = False
        self._range = None
        self._count_exact = False
        self._limit = None

    def select(self, columns: str = "*", count: Optional[str] = None):
        if count == "exact":
            self._count_exact = True
        return self

    def eq(self, column: str, value: Any):
        self.filters.append((column, "eq", value))
        return self

    def in_(self, column: str, values: List[Any]):
        self.filters.append((column, "in", values))
        return self

    def order(self, column: str, desc: bool = False):
        self._order_by = column
        self._desc = desc
        return self

    def range(self, start: int, end: int):
        self._range = (start, end)
        return self

    def limit(self, limit: int):
        self._limit = limit
        return self

    def insert(self, payload: Any):
        if isinstance(payload, list):
            rows = payload
        else:
            rows = [payload]
        for row in rows:
            r = dict(row)
            if "id" not in r:
                r["id"] = str(uuid4())
            if "created_at" not in r:
                r["created_at"] = datetime.now(timezone.utc).isoformat()
            self.store[self.table_name].append(r)
        return self

    def upsert(self, payload: Any, on_conflict: Optional[str] = None):
        if isinstance(payload, list):
            rows = payload
        else:
            rows = [payload]
        conflict_field = on_conflict or "id"
        for row in rows:
            r = dict(row)
            existing_idx = None
            for idx, existing in enumerate(self.store[self.table_name]):
                if existing.get(conflict_field) == r.get(conflict_field):
                    existing_idx = idx
                    break
            if existing_idx is not None:
                self.store[self.table_name][existing_idx].update(r)
            else:
                if "id" not in r:
                    r["id"] = str(uuid4())
                if "created_at" not in r:
                    r["created_at"] = datetime.now(timezone.utc).isoformat()
                self.store[self.table_name].append(r)
        return self

    def update(self, payload: Dict[str, Any]):
        self._update_payload = payload
        return self

    def delete(self):
        self._is_delete = True
        return self

    def execute(self) -> MockPostgrestResponse:
        rows = self.store.get(self.table_name, [])
        # Apply filters
        matched = []
        for r in rows:
            match = True
            for col, op, val in self.filters:
                if "." in col:
                    col = col.split(".")[-1]
                if op == "eq":
                    if str(r.get(col)) != str(val):
                        match = False
                        break
                elif op == "in":
                    str_vals = [str(v) for v in val]
                    if str(r.get(col)) not in str_vals:
                        match = False
                        break
            if match:
                matched.append(r)

        # Handle update
        if hasattr(self, "_update_payload"):
            for r in matched:
                r.update(self._update_payload)
            return MockPostgrestResponse(data=matched)

        # Handle delete
        if getattr(self, "_is_delete", False):
            self.store[self.table_name] = [r for r in rows if r not in matched]
            return MockPostgrestResponse(data=matched)

        # Handle sort
        if self._order_by:
            matched.sort(key=lambda x: str(x.get(self._order_by, "")), reverse=self._desc)

        total_count = len(matched)
        # Handle range/pagination
        if self._range:
            start, end = self._range
            matched = matched[start : end + 1]
        elif self._limit:
            matched = matched[: self._limit]

        return MockPostgrestResponse(data=matched, count=total_count if self._count_exact else None)


class MockSupabaseClient:
    def __init__(self, initial_store: Optional[Dict[str, List[Dict[str, Any]]]] = None):
        self.store = initial_store if initial_store is not None else {
            "documents": [],
            "claims": [],
            "citations": [],
            "claim_citations": [],
            "research_papers": [],
            "evidence": [],
            "verifications": [],
            "human_reviews": [],
            "reports": [],
            "processing_jobs": [],
            "profiles": [],
            "user_settings": [],
            "activity_log": [],
        }

    def table(self, table_name: str) -> MockTableQuery:
        if table_name not in self.store:
            self.store[table_name] = []
        return MockTableQuery(table_name, self.store)


@pytest.fixture
def mock_supabase():
    client = MockSupabaseClient()
    repo = SupabaseRepository(client=client)
    return repo, client


@pytest.mark.asyncio
async def test_supabase_document_crud(mock_supabase):
    repo, client = mock_supabase
    user_a = uuid4()
    doc_id = uuid4()
    doc = Document(
        id=doc_id,
        filename="test_paper.pdf",
        file_size_bytes=1024,
        mime_type="application/pdf",
        status=ProcessingStatus.PENDING,
        pipeline_stage=PipelineStage.UPLOADED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # 1. Create
    created = await repo.create_document(doc, user_id=user_a)
    assert created.id == doc_id
    assert created.filename == "test_paper.pdf"

    # 2. Get & Owner
    fetched = await repo.get_document(doc_id)
    assert fetched is not None
    assert fetched.filename == "test_paper.pdf"

    owner = await repo.get_document_owner(doc_id)
    assert owner == user_a

    # 3. Update
    fetched.status = ProcessingStatus.COMPLETED
    fetched.pipeline_stage = PipelineStage.DONE
    updated = await repo.update_document(fetched)
    assert updated.status == ProcessingStatus.COMPLETED

    # 4. List Documents
    docs_user_a, total_a = await repo.list_documents(user_id=user_a)
    assert total_a == 1
    assert docs_user_a[0].id == doc_id

    user_b = uuid4()
    docs_user_b, total_b = await repo.list_documents(user_id=user_b)
    assert total_b == 0

    # 5. Delete
    deleted = await repo.delete_document(doc_id)
    assert deleted is True
    assert await repo.get_document(doc_id) is None


@pytest.mark.asyncio
async def test_supabase_claims_and_evidence_hydration(mock_supabase):
    repo, client = mock_supabase
    doc_id = uuid4()
    claim_id = uuid4()
    ev_id = uuid4()
    cit_id = uuid4()

    citation = Citation(
        id=cit_id,
        document_id=doc_id,
        raw_marker="[1]",
        marker_type="NUMERIC",
        page_number=1,
        char_span=[50, 53],
        reference_text="Vaswani et al. (2017)",
    )

    evidence = Evidence(
        id=ev_id,
        claim_id=claim_id,
        source_provider="openalex",
        passage="The Transformer achieves 28.4 BLEU.",
        evidence_level=EvidenceLevel.ABSTRACT_ONLY,
        retrieval_status=RetrievalStatus.RETRIEVED,
        similarity_score=0.89,
    )

    claim = Claim(
        id=claim_id,
        document_id=doc_id,
        claim_text="The Transformer achieves 28.4 BLEU.",
        page_number=1,
        char_span=[10, 48],
        verdict=None,  # Null verdict preserved
        verification_state=VerificationState.UNABLE_TO_VERIFY,
        confidence=0.0,
        rationale="No full text retrieved.",
        citations=[citation],
        evidence=[evidence],
        needs_human_review=True,
        review_reasons=["No publication retrieved"],
    )

    # Save
    saved_claims = await repo.save_claims([claim])
    assert len(saved_claims) == 1

    # Retrieve and verify hydration
    claims, total = await repo.get_claims_by_document(doc_id)
    assert total == 1
    retrieved_claim = claims[0]
    assert retrieved_claim.id == claim_id
    assert retrieved_claim.verdict is None
    assert retrieved_claim.verification_state == VerificationState.UNABLE_TO_VERIFY
    assert len(retrieved_claim.evidence) == 1
    assert retrieved_claim.evidence[0].passage == "The Transformer achieves 28.4 BLEU."


@pytest.mark.asyncio
async def test_supabase_human_review_and_audit(mock_supabase):
    repo, client = mock_supabase
    doc_id = uuid4()
    claim_id = uuid4()

    claim = Claim(
        id=claim_id,
        document_id=doc_id,
        claim_text="BERT pre-training improves deep representations.",
        page_number=1,
        char_span=[0, 45],
        verdict=None,
        verification_state=VerificationState.REQUIRES_HUMAN_REVIEW,
        needs_human_review=True,
    )
    await repo.save_claims([claim])

    # Record review
    updated = await repo.record_human_review(
        claim_id=claim_id,
        reviewer_name="Dr. Smith",
        updated_verdict=VerificationVerdict.SUPPORTED,
        notes="Verified against NeurIPS 2018 proceedings.",
    )

    assert updated.verdict == VerificationVerdict.SUPPORTED
    assert updated.needs_human_review is False
    assert "Dr. Smith" in updated.rationale

    reviews = await repo.get_reviews_by_document(doc_id)
    assert len(reviews) == 1
    assert reviews[0]["reviewer_name"] == "Dr. Smith"


@pytest.mark.asyncio
async def test_supabase_reports_persistence(mock_supabase):
    repo, client = mock_supabase
    doc_id = uuid4()

    report = VerificationReport(
        document_id=doc_id,
        filename="manuscript.pdf",
        generated_at=datetime.now(timezone.utc),
        total_claims=3,
        reliability_score=75.5,
        verdict_counts={"SUPPORTED": 2, "UNSUPPORTED": 1},
        evidence_level_counts={"ABSTRACT_ONLY": 2, "FULL_TEXT": 1},
        human_review_required_count=0,
        claims=[],
    )

    # Save report
    await repo.save_report(report)

    # Fetch report
    fetched = await repo.get_report_by_document(doc_id)
    assert fetched is not None
    assert fetched.document_id == doc_id
    assert fetched.reliability_score == 75.5
    assert fetched.verdict_counts["SUPPORTED"] == 2


@pytest.mark.asyncio
async def test_supabase_processing_job_tracking(mock_supabase):
    repo, client = mock_supabase
    doc_id = uuid4()

    # Create job
    job = await repo.create_processing_job(
        document_id=doc_id,
        status=ProcessingStatus.PROCESSING,
        current_stage=PipelineStage.TEXT_EXTRACTION,
        progress_percent=15,
    )
    assert job["status"] == "PROCESSING"
    assert job["progress_percent"] == 15

    # Update job
    updated_job = await repo.update_processing_job(
        document_id=doc_id,
        status=ProcessingStatus.COMPLETED,
        current_stage=PipelineStage.DONE,
        progress_percent=100,
    )
    assert updated_job["status"] == "COMPLETED"
    assert updated_job["progress_percent"] == 100

    fetched = await repo.get_processing_job_by_document(doc_id)
    assert fetched["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_supabase_persistence_lifecycle_across_restarts(mock_supabase):
    """
    Simulates a backend restart:
    Persists data using Client 1, tears down repo, initializes Client 2
    pointing to the same shared PostgreSQL tables, and retrieves data.
    """
    _, client = mock_supabase
    shared_store = client.store

    # Instance 1 saves data
    repo1 = SupabaseRepository(client=MockSupabaseClient(initial_store=shared_store))
    doc_id = uuid4()
    doc = Document(
        id=doc_id,
        filename="persistent_paper.pdf",
        file_size_bytes=4096,
        mime_type="application/pdf",
        status=ProcessingStatus.COMPLETED,
        pipeline_stage=PipelineStage.DONE,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    await repo1.create_document(doc)

    # Instance 1 shuts down. Instance 2 starts up after backend reboot.
    repo2 = SupabaseRepository(client=MockSupabaseClient(initial_store=shared_store))
    reloaded_doc = await repo2.get_document(doc_id)

    assert reloaded_doc is not None
    assert reloaded_doc.id == doc_id
    assert reloaded_doc.filename == "persistent_paper.pdf"
    assert reloaded_doc.status == ProcessingStatus.COMPLETED
