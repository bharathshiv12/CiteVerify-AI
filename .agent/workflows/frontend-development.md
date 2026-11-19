# Workflow: Frontend Development (Agent 1)

This workflow outlines the step-by-step procedures for the Frontend Developer and Agent 1.

---

## 1. Scope & Ownership
- **Directory:** `frontend/**`
- **Branch:** `feature/frontend`
- **Responsibilities:**
  - Landing page & file upload dropzone.
  - Processing status screen with live stage polling.
  - Claim inspection table with verdict filter pills.
  - Detailed claim drawer/modal showing evidence passages and provenance.
  - Final verification report view with reliability score badge and human-review flags.
  - Human review submission modal.

---

## 2. Development Steps
1. **Isolated UI with Mocks:**
   - In `frontend/.env.local`, set `NEXT_PUBLIC_USE_MOCKS=true`.
   - Verify the "SAMPLE DATA" banner renders.
   - Build UI components against synthetic fixtures in `contracts/examples/`.
2. **Live Backend Integration:**
   - Set `NEXT_PUBLIC_USE_MOCKS=false`.
   - Ensure backend is running (`uvicorn app.main:app --app-dir backend --port 8000`).
   - Test PDF upload (`POST /api/documents/upload`), poll `/api/documents/{id}/status`.
3. **Responsive & Accessible Design:**
   - Verify mobile/tablet layout and keyboard navigation.
   - Ensure ARIA labels on all interactive controls.
4. **Validation Before PR:**
   - Run `npm run build` inside `frontend/`.
   - Check that no absolute URLs or localhost endpoints are hardcoded.

