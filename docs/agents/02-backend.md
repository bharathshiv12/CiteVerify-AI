# 02. Backend Role Specification (Agent 2)

## 1. Responsibility
The Backend Architect owns the FastAPI application, PDF document staging, multi-page text extraction, citation and bibliography parsing, pipeline coordination via BackgroundTasks, and database persistence.

## 2. Directory & Branch Ownership
- **Write Access:** `backend/**`, `scripts/**`
- **Primary Branch:** `feature/backend`
- **Forbidden from Editing:** `frontend/**`, `ai_engine/**`, `research_services/**`.

## 3. Interfaces & Contracts Consumed and Provided
- Exposes REST endpoints documented in `docs/API_CONTRACT.md`.
- Implements schemas in `backend/app/schemas/` derived from `contracts/schemas/`.
- Orchestrates pipeline by invoking:
  - `ai_engine.extract_claims()`
  - `research_services.retrieve_publication()`
  - `ai_engine.verify_claim_against_evidence()`
  - `backend.app.services.report_generator.generate_verification_report()`

## 4. Key Deliverables by Roadmap Window
- **Hours 0-6:** PDF upload validation, text extraction (`document_processor.py`), citation parsing (`citation_parser.py`).
- **Hours 6-12:** Integrate research retriever and publication matcher into pipeline worker.
- **Hours 12-18:** Integrate AI verification engine, complete end-to-end background task flow.
- **Hours 18-24:** Final report generation, reliability scoring, review audit logging.

## 5. Definition of Done
- [ ] `pytest backend/tests -v` passes cleanly.
- [ ] `GET /api/health` returns 200 with accurate version and timestamp.
- [ ] Uploaded PDFs validated for size, extension, MIME, and magic bytes.
- [ ] Database operations adhere to `AbstractRepository` interface.

