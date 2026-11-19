# 01. Frontend Role Specification (Agent 1)

## 1. Responsibility
The Frontend Engineer owns all client-side UI/UX, responsive views, interactive components, state management, accessibility, and integration with the backend API.

## 2. Directory & Branch Ownership
- **Write Access:** `frontend/**`
- **Primary Branch:** `feature/frontend`
- **Forbidden from Editing:** `backend/**`, `ai_engine/**`, `research_services/**`, `contracts/**` (without contract-change PR).

## 3. Interfaces & Contracts Consumed
- Consumes types from `frontend/types/index.ts`.
- Calls endpoints defined in `docs/API_CONTRACT.md` via `frontend/services/api.ts`:
  - `GET /api/health`
  - `POST /api/documents/upload`
  - `POST /api/documents/{id}/analyze`
  - `GET /api/documents/{id}/status`
  - `GET /api/documents/{id}/claims`
  - `GET /api/documents/{id}/report`
  - `GET /api/claims/{id}`
  - `POST /api/claims/{id}/review`

## 4. Key Deliverables by Roadmap Window
- **Hours 0-6:** Setup mock loading via `NEXT_PUBLIC_USE_MOCKS=true`, build file upload drag-and-drop zone.
- **Hours 6-12:** Build polling processing screen showing current `pipeline_stage`.
- **Hours 12-18:** Build claim inspection table, verdict filter tabs, evidence drawer.
- **Hours 18-24:** Build final report dashboard with reliability score and human-review feedback modal.

## 5. Definition of Done
- [ ] `npm run build` passes with 0 TypeScript and ESLint errors.
- [ ] No hardcoded localhost URLs (uses `NEXT_PUBLIC_API_BASE_URL`).
- [ ] Shows "SAMPLE DATA" banner whenever mocks are enabled.
- [ ] Responsive across mobile, tablet, and desktop viewports.

