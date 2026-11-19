# CiteVerify AI — API Contract Gaps & Frontend Accommodations

**Document Version:** 1.0.0  
**Owner:** Agent 1 (Frontend Architect)  
**Contract Source of Truth:** `contracts/openapi/openapi.yaml` & `contracts/schemas/`  

This document logs every capability or field required by academic research verification UI workflows that is currently absent from the canonical OpenAPI specification or backend schemas. The frontend implements honest fallbacks without fabricating data or endpoints.

---

### Gap 1: User-Scoped Document Listing
- **Missing Capability:** No endpoint exists to list documents previously uploaded by a user (e.g., `GET /api/documents`).
- **Affected Routes:** `/dashboard`, `/reports`, `/history`
- **What Frontend Currently Does:** Maintains a device-scoped local document registry (`frontend/lib/document-registry.ts`) storing `document_id`, `filename`, and `uploaded_at` per user session. Verifications and status are queried live for registered IDs. Displays an honest disclosure: *"Documents on this device"*.
- **Proposed API Shape:**
  ```http
  GET /api/documents?page=1&page_size=20
  Authorization: Bearer <token>
  Response: { "items": Document[], "page": 1, "page_size": 20, "total": 1 }
  ```
- **Responsible Integration Area:** Agent 2 (Backend Architect)

---

### Gap 2: Server-Side Document Deletion
- **Missing Capability:** No `DELETE /api/documents/{id}` endpoint exists to remove documents or purge verification traces.
- **Affected Routes:** `/history`, `/dashboard`
- **What Frontend Currently Does:** Provides a "Remove from this device's history" action with an explicit modal warning: *"This removes the document from your device's history. It does not delete the server copy."*
- **Proposed API Shape:**
  ```http
  DELETE /api/documents/{document_id}
  Response: 204 No Content
  ```
- **Responsible Integration Area:** Agent 2 (Backend Architect)

---

### Gap 3: Editing Extracted Claims
- **Missing Capability:** No endpoint exists to correct, split, or edit extracted claim boundaries or text (e.g., `PATCH /api/claims/{id}`).
- **Affected Routes:** `/verify/[documentId]/extract`
- **What Frontend Currently Does:** "Edit Claim" action is disabled with an explanatory tooltip: *"Editing extracted claims is not supported by the API yet."*
- **Proposed API Shape:**
  ```http
  PATCH /api/claims/{claim_id}
  Request: { "claim_text": string, "char_span": [number, number] }
  Response: Claim
  ```
- **Responsible Integration Area:** Agent 2 (Backend) & Agent 3 (AI/ML)

---

### Gap 4: Manual Citation Rematching
- **Missing Capability:** No endpoint to manually link a citation marker to a different bibliography reference or paper ID.
- **Affected Routes:** `/verify/[documentId]/map`
- **What Frontend Currently Does:** "Rematch Citation" button is rendered disabled with a tooltip indicating manual reference rematching is pending backend support.
- **Proposed API Shape:**
  ```http
  POST /api/citations/{citation_id}/rematch
  Request: { "matched_paper_id": string, "manual_override": true }
  Response: Citation
  ```
- **Responsible Integration Area:** Agent 2 (Backend) & Agent 4 (Research Services)

---

### Gap 5: Direct Publication Search via Scholarly APIs
- **Missing Capability:** No direct endpoint for user-initiated scholarly searches (Crossref/OpenAlex/Europe PMC) independent of document extraction.
- **Affected Routes:** `/verify/[documentId]/retrieve`
- **What Frontend Currently Does:** Displays only the papers retrieved by the automated pipeline for the document's citations. Any ad-hoc search filter operates client-side over already retrieved publications.
- **Proposed API Shape:**
  ```http
  GET /api/research/search?query={query}&provider=openalex|crossref|europe_pmc
  Response: { "items": ResearchPaper[] }
  ```
- **Responsible Integration Area:** Agent 4 (Research Services)

---

### Gap 6: Structured Comparison Breakdown (Methodology, Sample Size, Results)
- **Missing Capability:** `Evidence` schema contains `passage`, `similarity_score`, `section_name`, but does not break down methodology, sample size, or numerical effect sizes into structured sub-fields.
- **Affected Routes:** `/verify/[documentId]/compare`
- **What Frontend Currently Does:** Displays the exact retrieved passage alongside the verification rationale and evidence level, with a note: *"Detailed comparison indicators are not provided by the verification engine yet."*
- **Proposed API Shape:** Add optional `methodology_summary?: string`, `sample_size?: string`, `findings_delta?: string` to `Evidence` schema.
- **Responsible Integration Area:** Agent 3 (AI/ML Verification Engine)

---

### Gap 7: Server-Side PDF Report Export
- **Missing Capability:** No binary PDF generation endpoint (`GET /api/documents/{id}/report/pdf`).
- **Affected Routes:** `/reports/[documentId]`
- **What Frontend Currently Does:** Generates a clean, paginated, academic-formatted print view via client CSS `@media print` allowing users to save as PDF directly from the browser print dialog. Also provides a raw JSON export.
- **Proposed API Shape:**
  ```http
  GET /api/documents/{document_id}/report/pdf
  Response: application/pdf binary stream
  ```
- **Responsible Integration Area:** Agent 2 (Backend Architect)

---

### Gap 8: Backend JWT Authentication Validation
- **Missing Capability:** Backend endpoints currently do not enforce user authentication headers (`Authorization: Bearer <token>`).
- **Affected Routes:** Global API client (`frontend/services/api.ts`)
- **What Frontend Currently Does:** Injects the Supabase access token in `Authorization: Bearer` whenever a session exists, preparing for seamless transition once backend middleware activates JWT checking.
- **Responsible Integration Area:** Agent 2 (Backend Architect)

---

### Gap 9: Human Review Action Enums vs Verdict Update
- **Missing Capability:** The review endpoint (`POST /api/claims/{id}/review`) takes `updated_verdict: VerificationVerdict`, `reviewer_name: string`, `notes: string`. It does not have an explicit `review_action` enum (e.g. `APPROVE_RESULT`, `REJECT_RESULT`, `REQUEST_FURTHER_REVIEW`).
- **Affected Routes:** `/verify/[documentId]/verify`, `/reports/[documentId]`
- **What Frontend Currently Does:** Maps user UI review intents (e.g., confirm verdict, update verdict) to `updated_verdict` with the reviewer's notes and name according to the exact contract.
- **Responsible Integration Area:** Agent 2 (Backend Architect)
