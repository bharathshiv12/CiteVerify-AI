# Workflow: Backend Development (Agent 2)

This workflow outlines the step-by-step procedures for the Backend Architect and Agent 2.

---

## 1. Scope & Ownership
- **Directory:** `backend/**`, `scripts/**`
- **Branch:** `feature/backend`
- **Responsibilities:**
  - PDF upload validation & staging.
  - Multi-page text extraction (`document_processor.py`) using PyMuPDF / pdfplumber.
  - In-text citation parsing & bibliography extraction (`citation_parser.py`).
  - Citation-to-claim linking (`citation_matcher.py`).
  - Pipeline background task orchestration (`BackgroundTasks`).
  - Database repository implementation & persistence.
  - Final verification report compilation (`report_generator.py`).

---

## 2. Development Steps
1. **Local Setup:**
   - Activate `.venv` (`source backend/.venv/Scripts/activate` or `backend\.venv\Scripts\Activate.ps1`).
   - Run existing tests: `pytest -v`.
2. **Implementing Services:**
   - Replace `NotImplementedError` stubs in `backend/app/services/` with tested logic.
   - Maintain adherence to schemas in `backend/app/schemas/`.
3. **Pipeline Orchestrator:**
   - In `backend/app/api/routes/documents.py`, update `dummy_pipeline_runner` to sequentially invoke the 16 pipeline stages.
   - Update document status and pipeline stage at each transition.
4. **Validation Before PR:**
   - Run `pytest backend/tests -v`.
   - Run `python scripts/validate_repo.py`.

