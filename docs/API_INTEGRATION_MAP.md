# CiteVerify AI — API Integration Map

**Document Version:** 1.0.0  
**Status:** Canonical Reference for Backend-Frontend Compatibility  
**Author:** Agent 2 (Backend Architect)

---

## 1. Master Frontend-to-Backend Integration Matrix

| Frontend File / Component | User Action | Call Type | Backend Endpoint / Supabase Call | Request Shape | Response Shape | Status |
|---|---|---|---|---|---|---|
| `app/login/page.tsx` | Submit email/password login | Supabase JS Client | `supabase.auth.signInWithPassword()` | `{ email, password }` | `{ data: { session, user }, error }` | Client-Side Auth |
| `app/login/page.tsx` | Sign in with GitHub/Google | Supabase JS Client | `supabase.auth.signInWithOAuth()` | `{ provider: 'github'\|'google', options: { redirectTo } }` | Redirects to OAuth | Client-Side Auth |
| `app/login/page.tsx` | Enter as Guest / Demo | Local State | None (Simulated guest mode) | None | Sets local guest session | Client-Only |
| `app/signup/page.tsx` | Register new user account | Supabase JS Client | `supabase.auth.signUp()` | `{ email, password, options: { data: { full_name, institution } } }` | `{ data: { user, session }, error }` | Client-Side Auth |
| `app/forgot-password/page.tsx` | Request password reset email | Supabase JS Client | `supabase.auth.resetPasswordForEmail()` | `email, { redirectTo }` | `{ data, error }` | Client-Side Auth |
| `app/reset-password/page.tsx` | Confirm new password | Supabase JS Client | `supabase.auth.updateUser()` | `{ password }` | `{ data: { user }, error }` | Client-Side Auth |
| `app/auth/callback/page.tsx` | Handle OAuth redirect code | Supabase JS Client | `supabase.auth.getSession()` | URL hash/query session tokens | `{ data: { session }, error }` | Client-Side Auth |
| `app/settings/page.tsx` | Update profile (name, institution) | Supabase JS Client | `supabase.auth.updateUser()` | `{ data: { full_name, institution } }` | `{ data: { user }, error }` | Client-Side Auth |
| `app/settings/page.tsx` | Change password | Supabase JS Client | `supabase.auth.updateUser()` | `{ password: newPassword }` | `{ data: { user }, error }` | Client-Side Auth |
| `components/layout/top-nav.tsx` | Sign out / Logout | Supabase JS Client | `supabase.auth.signOut()` | None | Void | Client-Side Auth |
| `frontend/services/api.ts` | Backend Health Check | HTTP GET | `GET /api/health` | None | `{ status: "ok", service, version, timestamp }` | Verified Contract |
| `app/verify/page.tsx` (`FileUploader`) | Upload academic PDF | HTTP POST | `POST /api/documents/upload` | Multipart: `file: binary` (max 25MB) | `Document` object (`id`, `filename`, `file_size_bytes`, `status`, `pipeline_stage`, etc.) | Verified Contract |
| `app/verify/page.tsx` | Start verification pipeline | HTTP POST | `POST /api/documents/{id}/analyze` | Path: `id: uuid` | `DocumentAnalyzeResponse` (`document_id`, `status: PROCESSING`, `pipeline_stage: TEXT_EXTRACTION`, `message`) | Verified Contract |
| `app/verify/[id]/[stage]/page.tsx` | Poll pipeline status (every 2s) | HTTP GET | `GET /api/documents/{id}/status` | Path: `id: uuid` | `DocumentStatusResponse` (`document_id`, `status`, `pipeline_stage`, `progress_percent`, `total_claims_found`, `verified_claims_count`, `error_message`) | Verified Contract |
| `app/verify/[id]/[stage]/page.tsx` | List extracted claims | HTTP GET | `GET /api/documents/{id}/claims` | Query: `verdict?`, `needs_review?`, `page=1`, `page_size=20` | `ClaimListResponse` (`items: Claim[]`, `page`, `page_size`, `total`) | Verified Contract |
| `hooks/use-claim.ts` | Inspect single claim detail | HTTP GET | `GET /api/claims/{claim_id}` | Path: `claim_id: uuid` | `Claim` (`id`, `claim_text`, `char_span`, `citations`, `verdict`, `verification_state`, `confidence`, `rationale`, `evidence`, `needs_human_review`, `review_reasons`) | Verified Contract |
| `components/verification/human-review-panel.tsx` | Submit human review decision | HTTP POST | `POST /api/claims/{claim_id}/review` | Body: `{ reviewer_name, updated_verdict, notes }` | `Claim` (updated with review verdict and cleared `needs_human_review`) | Verified Contract |
| `app/reports/[id]/page.tsx` | Fetch final report | HTTP GET | `GET /api/documents/{id}/report` | Path: `id: uuid` | `VerificationReport` (`document_id`, `filename`, `generated_at`, `total_claims`, `reliability_score`, `verdict_counts`, `evidence_level_counts`, `human_review_required_count`, `claims`) | Verified Contract (Returns 409 if in progress) |
| `app/reports/[id]/page.tsx` | Export report as JSON | Client-Side Blob | None (Generates file from report object in memory) | `VerificationReport` | JSON file download `citeverify_report_<id>.json` | Client-Side Feature |
| `app/reports/[id]/page.tsx` | Print / Save as PDF | Browser Print API | `window.print()` | `@media print` CSS layout | Browser-rendered PDF | Client-Side Feature |
| `app/dashboard/page.tsx` | Aggregate metrics & dashboard cards | Client Aggregation | Loops registered document IDs calling `GET /api/documents/{id}/report` and `GET /api/documents/{id}/status` | Aggregate counts: docs, claims, supported, contradictory, etc. | Rendered StatCards and activity list | Client-Side Aggregated (Backend provides `GET /api/dashboard/stats` in Gap resolution) |
| `app/history/page.tsx` | View verification history | Client Registry | Reads `getRegisteredDocuments(userId)` and queries each status/report | Registered docs list | History table | Client-Side Registry (Backend provides `GET /api/documents` in Gap resolution) |
| `app/history/page.tsx` | Remove document from history | Client Registry | `unregisterDocument(id, userId)` | Removes ID from local storage | Updates table | Client-Side Registry (Backend provides `DELETE /api/documents/{id}` in Gap resolution) |
| `app/verify/[id]/extract` | "Edit Claim" button | None | Disabled with tooltip | None | "Editing extracted claims is not supported by API yet" | Frontend Control (No Backend Operation) |
| `app/verify/[id]/map` | "Rematch Citation" button | None | Disabled with tooltip | None | "Manual citation rematching is pending backend support" | Frontend Control (No Backend Operation) |
| `app/verify/[id]/retrieve` | Ad-hoc external paper search | None | Disabled / client filter | None | Displays pipeline-retrieved papers only | Frontend Control (No Backend Operation) |

---

## 2. Authentication Architecture

### 2.1. Client-Side Authentication (Supabase JS Client)
The frontend communicates directly with Supabase Auth for all user lifecycle events:
- **Sign Up:** `supabase.auth.signUp({ email, password, options: { data: { full_name, institution } } })`
- **Sign In:** `supabase.auth.signInWithPassword({ email, password })`
- **OAuth:** `supabase.auth.signInWithOAuth({ provider: 'github' | 'google', options: { redirectTo } })`
- **Password Reset Request:** `supabase.auth.resetPasswordForEmail(email, { redirectTo })`
- **Password Confirmation:** `supabase.auth.updateUser({ password })`
- **Profile Updates:** `supabase.auth.updateUser({ data: { full_name, institution } })`
- **Session Retrieval:** `supabase.auth.getSession()`

### 2.2. Backend JWT Validation
The backend does NOT duplicate signup/login endpoints unless explicitly requested; instead, it enforces security via **JWT verification middleware / FastAPI dependencies**:
1. When making API calls to `/api/documents/**` or `/api/claims/**`, the frontend's `getAuthHeader()` injects:
   ```http
   Authorization: Bearer <access_token>
   ```
2. The backend extracts and cryptographically validates the token:
   - **Scheme A (Modern):** Asymmetric signing keys verified against `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` (cached).
   - **Scheme B (Legacy):** HS256 symmetric signature using `SUPABASE_JWT_SECRET`.
   - **Scheme C (Remote Fallback):** Direct validation via Supabase `auth.get_user(token)`.
3. Validated claims: `sub` (user UUID), `exp` (expiration), `aud` (`authenticated`), `iss` (Supabase project).
4. User identity is derived strictly from the verified JWT `sub`, never from client-provided headers or body payloads.

---

## 3. Pipeline Stages: 11 Backend Stages ↔ 6 Visual Steps

The backend runs an 11-stage pipeline, mapped to 6 visual steps in the frontend UI:

| Visual Step (#, Slug, Name) | Backend Canonical PipelineStage Enum | Description / Work Performed |
|---|---|---|
| **Step 1: `upload`**<br>(Intake & Binary Validation) | `UPLOADED` | PDF uploaded, magic bytes `%PDF-` validated, MIME checked, safe UUID filename generated, stored in storage. |
| **Step 2: `extract`**<br>(Text & Claim Extraction) | `TEXT_EXTRACTION`<br>`CLAIM_EXTRACTION`<br>`CITATION_PARSING`<br>`REFERENCE_PARSING` | PyMuPDF page-by-page extraction, scanned check. Heuristic factual claim extraction with char spans. Numeric `[1]` and author-year citation marker extraction. Reference section bibliography parsing. |
| **Step 3: `map`**<br>(Citation Matching) | `CITATION_MATCHING` | Links in-text citation markers to bibliography reference entries, resolving author, year, and title tokens. |
| **Step 4: `retrieve`**<br>(Scholarly Literature Retrieval) | `PAPER_RETRIEVAL` | Queries Crossref, OpenAlex, Europe PMC. Resolves DOIs, titles, abstracts, open-access full text. Tracks match confidence and source availability level. |
| **Step 5: `compare`**<br>(Evidence Extraction) | `EVIDENCE_EXTRACTION` | Chunks and extracts candidate passages strictly from retrieved text (abstract or full text). Evaluates similarity and aligns passage to claim assertions. |
| **Step 6: `verify`**<br>(Verification & Reporting) | `VERIFICATION`<br>`REPORT_GENERATION`<br>`DONE` | Evaluates evidence vs claim (numbers, direction, findings). Assigns canonical verdict, confidence, rationale. Generates final audit report and marks document status `COMPLETED`. |

### Forward Navigation Gate Rules
- Step $N$ is navigable if `isStageReached(backendStage, N)` is `true`.
- When backend is at `CITATION_MATCHING` (step 3), steps 1, 2, 3 are unlocked; steps 4, 5, 6 are locked.
- When backend reaches `DONE`, all 6 steps are unlocked and the final report is accessible.

---

## 4. Canonical Enums & Allowed Values

### 4.1. Verification Verdict (`VerificationVerdict`)
Exact string literals matching `contracts/schemas/enums.json`:
- `SUPPORTED` — Direct empirical evidence validates the claim.
- `PARTLY_SUPPORTED` — Core assertion supported, but caveats/limitations exist.
- `UNSUPPORTED` — Relevant retrieved evidence does not confirm the claim.
- `CONTRADICTORY` — Retrieved empirical evidence directly conflicts with or refutes the claim.
- `POTENTIALLY_OUTDATED` — Landmark or historical finding superseded by newer consensus literature.
- `null` / `None` — Insufficient evidence retrieved (`needs_human_review = true`). Never coerced to `UNSUPPORTED`.

### 4.2. Verification State (`VerificationState`)
- `VERIFIED`
- `REQUIRES_HUMAN_REVIEW`
- `UNABLE_TO_VERIFY`
- `PENDING`

### 4.3. Evidence Level (`EvidenceLevel`)
- `FULL_TEXT` — Open access full paper text examined.
- `ABSTRACT_ONLY` — Only peer-reviewed abstract examined.
- `METADATA_ONLY` — Only title, authors, venue retrieved (no passages).
- `NONE` — No publication retrieved or paywalled with zero text.

### 4.4. Retrieval Status (`RetrievalStatus`)
- `RETRIEVED`
- `NOT_FOUND`
- `PAYWALLED`
- `API_ERROR`

### 4.5. Processing Status (`ProcessingStatus`)
- `PENDING`
- `PROCESSING`
- `COMPLETED`
- `FAILED`

---

## 5. Report Export Formats
1. **JSON Format:** Standard JSON matching `contracts/schemas/report.schema.json`. Generated via client-side download or backend `GET /api/documents/{id}/report`.
2. **Browser Print / PDF:** Paginated academic layout rendered via `@media print` CSS rules in `frontend/app/reports/[documentId]/page.tsx`.
3. **Server-Side PDF Export (Gap 7):** Binary PDF stream generated by pure-Python ReportLab via `GET /api/documents/{id}/report/pdf` or `GET /api/reports/{id}/export?format=pdf`.
4. **Markdown Export:** Plaintext Markdown summary with citation tables via `GET /api/reports/{id}/export?format=markdown`.

---

## 6. User Settings Specification

The settings page reads/writes the following profile and preference fields:
- **Academic Profile:**
  - `full_name` (string, max 100)
  - `institution` (string, max 150)
- **Security:**
  - `password` (updated via Supabase Auth)
- **Notification Preferences (Stored in `user_settings` table):**
  - `notify_analysis_done` (boolean, default true)
  - `notify_human_review_needed` (boolean, default true)
- **Verification Preferences (Stored in `user_settings` table):**
  - `preferred_research_provider` (string: `ALL`, `CROSSREF`, `OPENALEX`, `EUROPE_PMC`, default `ALL`)
  - `strict_numeric_comparison` (boolean, default true)
  - `auto_flag_outdated_years` (integer, default 10)
  - `allow_external_ai_evaluation` (boolean, default false)

---

## 7. Frontend Controls Without Backend Operations (Gaps)

| UI Component | Location | Current UI Behavior | Backend Resolution Plan |
|---|---|---|---|
| Edit Claim Button | `/verify/[id]/extract` | Button rendered disabled with tooltip: *"Editing extracted claims is not supported by the API yet."* | Provide `PATCH /api/claims/{id}` in backend router for full capability. |
| Rematch Citation Button | `/verify/[id]/map` | Button rendered disabled with tooltip: *"Manual citation rematching is pending backend support."* | Provide `POST /api/citations/{id}/rematch` in backend router. |
| Direct Scholarly Search | `/verify/[id]/retrieve` | Ad-hoc search input filters locally retrieved papers; no external search endpoint. | Implement `GET /api/research/search` querying Crossref/OpenAlex/Europe PMC. |
| Device History Deletion | `/history` | Modal warns: *"Removes document from device history. Does not delete server copy."* | Implement `DELETE /api/documents/{id}` to delete DB records and storage file. |
| Server-Side Document List | `/history`, `/dashboard` | Relies on `localStorage` registry with disclaimer: *"Documents on this device"*. | Implement `GET /api/documents` returning user-scoped paginated documents. |
