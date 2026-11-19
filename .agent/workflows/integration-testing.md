# Workflow: Integration & End-to-End Testing

This workflow guides cross-agent integration testing for CiteVerify AI.

---

## 1. Scope & Ownership
- **Directory:** `tests/integration/`, `tests/end_to_end/`, `scripts/validate_repo.py`
- **Ownership:** Shared across all agents, coordinated by Integration Lead.

---

## 2. Test Pyramid
1. **Contract Validation (`scripts/validate_repo.py`):**
   - Validates JSON schemas, OpenAPI spec, and enum synchronization across Python and TypeScript.
2. **Backend Unit & Contract Tests (`backend/tests/`):**
   - Health endpoint shape.
   - Pydantic enum drift against `enums.json`.
   - File upload validation edge cases.
3. **Integration Slices (`tests/integration/`):**
   - Research API mock fixtures -> Publication Matcher -> Evidence Extractor.
   - Extracted claims -> Embedding Service -> Verification Engine.
4. **End-to-End Verification (`tests/end_to_end/`):**
   - Sample open-access paper upload -> full pipeline execution -> final verification report output.

---

## 3. Execution Commands
```bash
# Contract validation
python scripts/validate_repo.py

# Backend unit test suite
backend/.venv/Scripts/pytest backend/tests -v

# Integration tests
backend/.venv/Scripts/pytest tests/integration -v
```

