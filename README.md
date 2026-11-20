# CiteVerify AI
### Automated Scientific Claim & Citation Verification System
**INNOVEDGE 2026 Hackathon | Problem Statement 03**

[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.165-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL%20%7C%20Auth%20%7C%20Storage-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![Vercel Deployment](https://img.shields.io/badge/Deployed-Vercel-000000?logo=vercel&logoColor=white)](https://citeverify-frontend.vercel.app)
[![Tests Passing](https://img.shields.io/badge/Backend%20Tests-82%2F82%20Passing-brightgreen?logo=pytest&logoColor=white)](backend/tests/)
[![Frontend Tests](https://img.shields.io/badge/Frontend%20Tests-25%2F25%20Passing-brightgreen)](frontend/scripts/run-tests.mjs)
[![API Tests](https://img.shields.io/badge/API%20Endpoints-41%2F41%20Passing-brightgreen)](scripts/test_all_endpoints.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. Live Deployments & Quick Links

| Resource | URL | Description |
|---|---|---|
| **Live Frontend Application** | [https://citeverify-frontend.vercel.app](https://citeverify-frontend.vercel.app) | Production Next.js 14 web workspace |
| **Live Backend API** | [https://citeverify-backend-delta.vercel.app](https://citeverify-backend-delta.vercel.app) | Production FastAPI serverless runtime |
| **Interactive Swagger Docs** | [https://citeverify-backend-delta.vercel.app/api/docs](https://citeverify-backend-delta.vercel.app/api/docs) | Interactive OpenAPI 3.1.0 test console |
| **OpenAPI Schema JSON** | [https://citeverify-backend-delta.vercel.app/api/openapi.json](https://citeverify-backend-delta.vercel.app/api/openapi.json) | Raw canonical API specification |
| **GitHub Repository** | [https://github.com/bharathshiv12/CiteVerify-AI](https://github.com/bharathshiv12/CiteVerify-AI) | Monorepo source code & issue tracker |

---

## 2. Executive Summary & Core Principle

In academic literature, citations are frequently taken as implicit proof of factual assertions. However, scientific integrity audits reveal widespread citation discrepancies: papers citing sources that do not contain the asserted findings, misrepresenting secondary reviews as primary data, or citing superseded results.

**CiteVerify AI** is an automated, evidence-grounded scientific claim verification platform. An academic researcher or evaluator uploads a research paper PDF; the platform extracts empirical assertions, identifies attached citations, retrieves cited publications across free public scholarly APIs (**Crossref**, **OpenAlex**, **Europe PMC**), extracts candidate evidence passages, semantically ranks them, and evaluates whether the cited publication genuinely supports the factual assertion.

> [!IMPORTANT]
> **Core Principle:** A real citation does not automatically support its claim. We verify the claim against the evidence.

### The 5 Hard Scientific Honesty Rules
1. **Never Fabricate:** The system never invents publications, DOIs, quotes, evidence passages, citations, or benchmark results.
2. **Abstracts vs. Full-Text:** An abstract is never presented as full text. Every evidence item explicitly sets `evidence_level` (`FULL_TEXT`, `ABSTRACT_ONLY`, `METADATA_ONLY`, `NONE`).
3. **Retrieval Failure is Not Refutation:** A paper that cannot be retrieved or is paywalled is never marked false or unsupported. It is categorized as `UNABLE_TO_VERIFY` or flagged for human review.
4. **No Coerced Verdicts:** If retrieved text does not address the claim, `verdict` remains `null` rather than forced into a binary classification.
5. **Source Traceability:** Every verdict traces directly back to a verifiable source (DOI/URL, provider, chunk passage, evidence level, confidence score).

---

## 3. System Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend Client (Next.js 14 App Router)"]
        UI["Academic Dashboard & Research Workspace\n(Tailwind CSS • Warm Academic Palette • Recharts)"]
        AUTH_UI["Supabase Auth Client\n(Email/Password • Google OAuth)"]
        API_CLIENT["Canonical API Client\n(TanStack Query • Polling • Error Envelope Handling)"]
    end

    subgraph Hosting["Cloud Infrastructure (Vercel Serverless)"]
        FE_DEPLOY["Frontend Project\n(citeverify-frontend.vercel.app)"]
        BE_DEPLOY["Backend Project\n(citeverify-backend-delta.vercel.app)"]
    end

    subgraph Backend["FastAPI Backend Application"]
        ROUTER["FastAPI Router (/api)\n(Documents • Claims • Research • Dashboard • Settings)"]
        MW["Middleware Stack\n(CORS Allowlist • Request ID Tracing • Path Rewriter)"]
        ORCH["Pipeline Orchestrator\n(11-Stage Background Verification Engine)"]
        PDF_PROC["PDF Processor (PyMuPDF)\n(Text Extraction • Scanned PDF Detection)"]
        CLAIM_EXT["Claim Extractor & Citation Parser\n(Numeric [1] • Author-Year • Bibliography Matcher)"]
        NLI["Verification Engine\n(Pretrained NLI • Semantic Cosine Matcher • Numerical Guard)"]
        PDF_REP["ReportLab PDF Engine\n(Publication-Ready Verification Reports)"]
    end

    subgraph Supabase["Persistent Backend (Supabase Free Tier)"]
        S_AUTH["Supabase Auth (JWT JWKS / Remote Verification)"]
        S_DB[("PostgreSQL Database\n(13 Tables • Cascading Foreign Keys • RLS Policies)")]
        S_STOR["Supabase Storage (sapthack-documents Bucket)\n(Fallback to Serverless /tmp on Read-Only FS)"]
    end

    subgraph Scholarly["Scholarly Literature APIs (Free / Polite Pool)"]
        CROSSREF["Crossref REST API\n(Metadata • Works • DOIs)"]
        OPENALEX["OpenAlex Polite Pool\n(Open Access • Inverted Abstracts • Citations)"]
        EPMC["Europe PMC REST API\n(Biomedical • Open Access Full-Text Chunks)"]
    end

    UI --> API_CLIENT
    AUTH_UI --> S_AUTH
    API_CLIENT --> BE_DEPLOY
    BE_DEPLOY --> ROUTER
    ROUTER --> MW
    ROUTER --> ORCH
    ORCH --> PDF_PROC
    ORCH --> CLAIM_EXT
    ORCH --> Scholarly
    ORCH --> NLI
    ORCH --> S_DB
    ORCH --> S_STOR
    ORCH --> PDF_REP
```

---

## 4. The 11-Stage Pipeline / 16-Step Verification Workflow

```mermaid
flowchart TD
    S1["1. User Uploads PDF"] --> S2["2. Validate File (%PDF- magic bytes, MIME, size cap)"]
    S2 --> S3["3. PDF Processor Extracts Page Text (detects scanned/image PDFs)"]
    S3 --> S4["4. Claim Extractor Isolates Factual Empirical Claims"]
    S4 --> S5["5. Citation Parser Detects In-Text Markers ([1], Smith et al., 2020)"]
    S5 --> S6["6. Reference Parser Extracts Bibliography Section"]
    S6 --> S7["7. Citation Matcher Links Claims to Reference Entries"]
    S7 --> S8["8. Research Services Query Crossref & OpenAlex (Europe PMC)"]
    S8 --> S9["9. Publication Metadata Matched with Confidence & Reason"]
    S9 --> S10["10. Accessible Abstracts or Legitimate OA Full-Text Retrieved"]
    S10 --> S11["11. Evidence Extractor Isolates & Chunks Relevant Passages"]
    S11 --> S12["12. Embedding Service Ranks Passages Semantically Against Claim"]
    S12 --> S13["13. Verification Engine Compares Exact Claim with Evidence"]
    S13 --> S14["14. Structured JSON Results Produced & Validated Against Contract"]
    S14 --> S15["15. Human-Review Flags Assigned for Inconclusive Cases"]
    S15 --> S16["16. Final Verification Report & Interactive Dashboard Rendered"]
```

### Pipeline Stages & Mapping
The 11 backend execution stages map cleanly into 6 sequential user experience stages:

| Stage ID | Backend `PipelineStage` | Frontend UI Stage | Description |
|---|---|---|---|
| 01 | `UPLOADED` | Document Intake | Magic bytes validation (`%PDF-`), MIME check, storage staging |
| 02 | `TEXT_EXTRACTION` | Text Extraction | Multi-page text extraction via PyMuPDF, scanned PDF heuristic detection |
| 03 | `CLAIM_EXTRACTION` | Claim Extraction | Natural language sentence tokenization and empirical assertion isolation |
| 04 | `CITATION_PARSING` | Citation Graph | Regex detection of numeric (`[1]`) and author-year markers (`Smith 2020`) |
| 05 | `REFERENCE_PARSING` | Citation Graph | Structured parsing of the bibliography/references section |
| 06 | `CITATION_MATCHING` | Citation Graph | Graph linking in-text citations to parsed bibliography entries |
| 07 | `PAPER_RETRIEVAL` | Research Retrieval | Concurrent polite pool querying across Crossref, OpenAlex, and Europe PMC |
| 08 | `EVIDENCE_EXTRACTION`| Evidence Workspace | Passage chunking and TF-IDF / semantic cosine relevance ranking |
| 09 | `VERIFICATION` | Verdict Evaluation | Pretrained NLI classification, numerical contradiction checks |
| 10 | `REPORT_GENERATION` | Verification Report | Synthesis of document reliability score and audit log entries |
| 11 | `DONE` | Verification Report | Final structured envelope and downloadable ReportLab PDF report ready |

---

## 5. Processing Statuses vs. Verification Verdicts

Processing state and scientific verdict are strictly decoupled to preserve truth in representation:

### `ProcessingStatus` (Document Pipeline State)
- `PENDING`: Uploaded, awaiting queue pickup.
- `PROCESSING`: Pipeline actively running in background.
- `COMPLETED`: Pipeline finished; verification report ready.
- `FAILED`: Pipeline halted due to an unrecoverable validation error.

### `VerificationVerdict` (Claim Evaluation Outcome)
- `SUPPORTED`: Source empirical evidence directly confirms the claim assertion.
- `PARTLY_SUPPORTED`: Source confirms partially or with unmentioned caveats.
- `UNSUPPORTED`: Source does not provide empirical evidence for this claim.
- `CONTRADICTORY`: Source evidence directly refutes or contradicts the claim.
- `POTENTIALLY_OUTDATED`: Source supported it when written, but newer literature supersedes it.
- `null`: When evidence is inconclusive or retrieval is incomplete, `verdict = null` and `verification_state = UNABLE_TO_VERIFY` or `REQUIRES_HUMAN_REVIEW`.

---

## 6. Monorepo Structure & Ownership

CiteVerify AI follows a clean monorepo architecture divided among four specialized engineering roles:

```
CiteVerify-AI/
├── frontend/               # Next.js 14 App Router, TypeScript, Tailwind CSS (Agent 1: Frontend)
│   ├── app/                # Pages: Landing (/), Workspace (/dashboard), Verify (/verify), Reports (/reports)
│   ├── components/         # Brand, UI, Verification components, Layouts, Providers
│   ├── hooks/              # TanStack Query React hooks (useDocumentStatus, useDocumentClaims, etc.)
│   ├── lib/                # Supabase SSR auth client, document registry, test fixtures
│   ├── services/           # Canonical API client (api.ts)
│   └── types/              # TypeScript contract definitions synchronized with contracts/
│
├── backend/                # FastAPI application, DB repository, orchestrator (Agent 2: Backend)
│   ├── api/                # Vercel serverless entrypoint (index.py) & path rewriter
│   ├── app/                # Core FastAPI app (main.py), config, middleware, error handlers
│   │   ├── api/routes/     # Health, Auth, Documents, Claims, Research, Dashboard, Settings
│   │   ├── database/       # Repository interface & Supabase PostgreSQL repository (13 tables)
│   │   ├── processors/     # PDF validator, PyMuPDF extractor, citation/claim parsers
│   │   ├── services/       # 11-stage pipeline orchestrator, ReportLab PDF report generator
│   │   └── storage/        # Supabase Storage client with fallback to /tmp on serverless
│   └── tests/              # 82 pytest unit, integration, and contract tests
│
├── ai_engine/              # Machine Learning & Verification Engine (Agent 3: AI/ML)
│   ├── claim_extractor.py  # Factual statement extraction heuristics
│   ├── embeddings.py       # TF-IDF & dense cosine similarity passage ranker
│   ├── nli_verifier.py     # Pretrained Natural Language Inference & contradiction logic
│   └── numerical_check.py  # Numerical value and percentage consistency checks
│
├── research_services/      # Scholarly API Integrations (Agent 4: Research Integration)
│   ├── crossref_client.py  # Crossref REST API client (Polite pool)
│   ├── openalex_client.py  # OpenAlex REST API client with abstract inverted-index decoder
│   ├── europe_pmc.py       # Europe PMC REST API client (Biomedical OA literature)
│   └── retrieval_service.py# Unified multi-source scholarly literature aggregator
│
├── contracts/              # SHARED SINGLE SOURCE OF TRUTH (All Agents)
│   ├── openapi/            # Canonical OpenAPI 3.1.0 specification (openapi.yaml)
│   ├── schemas/            # Canonical enums.json and 9 JSON schemas
│   └── examples/           # Validated synthetic fixture payloads (_synthetic: true)
│
├── docs/                   # Architecture, database schema, agent guides, deployment specs
└── scripts/                # Repository validation, dev runners, API endpoint test suites
```

### Team Roles & Ownership Matrix
| Role | Directory Ownership | Scope of Responsibility |
|---|---|---|
| **Agent 1: Frontend Architect** | `frontend/**` | Next.js 14 App Router, UI/UX, Tailwind CSS, Supabase SSR Auth, Accessibility |
| **Agent 2: Backend Architect** | `backend/**`, `scripts/**` | FastAPI API, Vercel Serverless runtime, PyMuPDF, Supabase DB & Storage, PDF export |
| **Agent 3: AI/ML Engineer** | `ai_engine/**` | Claim extraction, semantic embeddings, NLI verification, numerical guardrails |
| **Agent 4: Research Integration** | `research_services/**`, `tests/` | Crossref, OpenAlex, Europe PMC integrations, scholarly literature discovery |
| **Shared Consensus** | `contracts/**`, `docs/**` | OpenAPI 3.1.0, JSON schemas, canonical enums (Strict zero-drift contract) |

---

## 7. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend Framework** | Next.js (App Router) | `14.2.15` | Server-rendered React client interface |
| **UI Library & Styling** | React 18, Tailwind CSS | `18.3.1` / `3.4.13` | Responsive academic UI with warm design system |
| **Client Data Fetching** | TanStack React Query | `5.59.16` | Asynchronous status polling and cache management |
| **Icons & Charts** | Lucide React, Recharts | `0.441.0` / `2.13.0` | Academic vector icons and reliability distribution charts |
| **Backend Framework** | FastAPI | `0.165.0` | High-performance asynchronous REST API |
| **ASGI Server** | Uvicorn | `0.54.0` | Local production ASGI server |
| **Contract Validation** | Pydantic v2 / Settings | `2.14.4` / `2.16.3` | Type-safe schema validation and settings parsing |
| **PDF Extraction** | PyMuPDF (`fitz`) | `2.1` | Native PDF stream extraction, page layout analysis |
| **PDF Generation** | ReportLab | `5.1.0` | Synthesis of downloadable publication-ready audit reports |
| **Database & Auth** | Supabase (PostgreSQL) | `2.34.1` | 13 relational tables, Row-Level Security, JWT auth |
| **File Storage** | Supabase Storage / `/tmp` | Bucket `sapthack-documents` | Private PDF staging with serverless fallback |
| **Scholarly Literature** | Crossref, OpenAlex, Europe PMC | REST APIs | Free polite pool scholarly literature retrieval (₹0 budget) |
| **Testing** | pytest, pytest-asyncio, Node test runner | `9.2.0` / `1.5.0` | Automated contract, unit, and API test suites |

---

## 8. Local Setup & Execution Guide

### Prerequisites
- **Python:** 3.11, 3.12, or 3.13
- **Node.js:** v18.x or v20.x or higher
- **npm:** v9.x or higher

### Option A: Local Development in Windows PowerShell

```powershell
# 1. Clone repository
git clone https://github.com/bharathshiv12/CiteVerify-AI.git
cd CiteVerify-AI

# 2. Set up Backend Python Virtual Environment
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install -r backend\requirements-dev.txt

# 3. Configure Backend Environment
Copy-Item backend\.env.example backend\.env
# (Optional: Add your SUPABASE_URL and SUPABASE_SECRET_KEY to backend\.env)

# 4. Set up Frontend Node Environment (in a separate terminal)
cd frontend
npm install
Copy-Item .env.example .env.local

# 5. Start Backend Server (Port 8000)
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload

# 6. Start Frontend Server (Port 3000)
npm run dev
```

### Option B: Local Development in Linux / macOS / Git Bash

```bash
# 1. Clone repository
git clone https://github.com/bharathshiv12/CiteVerify-AI.git
cd CiteVerify-AI

# 2. Set up Backend Virtual Environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# 3. Configure Environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 4. Set up Frontend
cd frontend
npm install
npm run dev &

# 5. Start Backend
cd ..
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Open [http://localhost:3000](http://localhost:3000) in your browser. The backend documentation is accessible at [http://localhost:8000/api/docs](http://localhost:8000/api/docs).

---

## 9. Comprehensive REST API Reference

All backend API routes are prefixed with `/api`. Error responses follow the canonical `ErrorEnvelope` specification:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Document not found.",
    "details": {},
    "request_id": "req_abc123"
  }
}
```

### Route Index
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health` | Liveness and service configuration check | No |
| `GET` | `/api/health/ready` | Readiness probe with database connectivity check | No |
| `GET` | `/api/health/live` | Process liveness check | No |
| `GET` | `/api/auth/me` | Fetch authenticated user profile | Yes (Bearer JWT) |
| `POST` | `/api/auth/logout` | Revoke session and log out | Yes (Bearer JWT) |
| `POST` | `/api/auth/forgot-password` | Request password reset token | No |
| `POST` | `/api/documents/upload` | Upload and validate academic PDF (`multipart/form-data`) | Optional (Anonymous staged) |
| `GET` | `/api/documents` | List user documents (paginated) | Optional |
| `GET` | `/api/documents/{id}` | Retrieve document details and processing status | Optional (Owner/Public) |
| `POST` | `/api/documents/{id}/analyze` | Trigger 11-stage background verification pipeline | Optional (Owner/Public) |
| `GET` | `/api/documents/{id}/status` | Poll document verification progress and stage | Optional (Owner/Public) |
| `GET` | `/api/documents/{id}/claims` | Retrieve extracted claims, citations, and verdicts | Optional (Owner/Public) |
| `GET` | `/api/documents/{id}/report` | Retrieve final synthesized verification report | Optional (Owner/Public) |
| `GET` | `/api/documents/{id}/report/pdf` | Download publication-ready PDF report stream | Optional (Owner/Public) |
| `DELETE` | `/api/documents/{id}` | Delete document and cascade delete claims/audit | Yes (Owner only) |
| `GET` | `/api/claims/{id}` | Get claim details and candidate evidence passages | Optional |
| `POST` | `/api/claims/{id}/review` | Submit expert human review and override verdict | Yes (Bearer JWT) |
| `PATCH` | `/api/claims/{id}` | Edit claim text, page span, or citation mapping | Yes (Owner only) |
| `GET` | `/api/research/search` | Query scholarly literature (Crossref, OpenAlex, EPMC) | No |
| `GET` | `/api/dashboard/stats` | Retrieve workspace analytics and reliability metrics | Yes (Bearer JWT) |
| `GET` | `/api/dashboard/activity` | Retrieve user audit activity and recent verification runs | Yes (Bearer JWT) |
| `GET` | `/api/settings` | Get user verification preferences and defaults | Yes (Bearer JWT) |
| `PUT` | `/api/settings` | Update user verification preferences and defaults | Yes (Bearer JWT) |

---

## 10. Security, Privacy & Compliance

- **PostgreSQL Row-Level Security (RLS):** All 13 database tables in Supabase enforce granular RLS policies. Users can only read and mutate documents, claims, evidence, and reports belonging to their authenticated `auth.uid()`.
- **Insecure Direct Object Reference (IDOR) Protection:** Backend routes verify that the requesting user's identity matches the document's `user_id`. Cross-user access attempts strictly return `404 Not Found` to prevent metadata leakage.
- **JWT Verification:** Asymmetric JWKS signature verification ensures authenticated endpoints reject forged or expired tokens.
- **MIME & Magic Bytes Sanitization:** File uploads are strictly validated by checking the initial `%PDF-` byte header and MIME type. Executable or corrupted files are immediately rejected with `400 Bad Request`.
- **Serverless Filesystem Safety:** Local file operations safely fallback to `/tmp/citeverify_storage` in read-only serverless execution environments (e.g., Vercel), preventing filesystem permission crashes.
- **Strict CORS Origin Isolation:** Allowed CORS origins include local development (`http://localhost:3000`) and validated production Vercel domains (`https://.*\.vercel\.app`). All error responses preserve CORS headers to prevent opaque browser errors.

---

## 11. Verified Quality Metrics & Test Results

All quality gates and test suites pass cleanly across both local and production environments:

| Test Suite / Quality Gate | Command | Result | Execution Time |
|---|---|---|---|
| **Repository Contract Gatekeeper** | `python scripts/validate_repo.py` | **5 / 5 Gates Passed** | 0.8s |
| **Backend Unit & Contract Tests** | `pytest backend/tests` | **82 / 82 Passed** | 1.49s |
| **Comprehensive API Test Console** | `python scripts/test_all_endpoints.py` | **41 / 41 Endpoints Passed** | 4.2s |
| **Frontend Unit Tests** | `npm --prefix frontend run test` | **25 / 25 Passed** | 87ms |
| **Frontend TypeScript Typecheck** | `npm --prefix frontend run typecheck` | **0 Errors** | 3.5s |
| **Frontend ESLint Validation** | `npm --prefix frontend run lint` | **0 Warnings, 0 Errors** | 5.2s |
| **Next.js Production Build** | `npm --prefix frontend run build` | **17 / 17 Pages Compiled** | 8.6s |
| **Live Vercel Production Pipeline** | `urllib.request` HTTPS E2E | **100% Verified** | ~8s |

---

## 12. Git Collaboration & Branch Audit

The repository has completed full integration into `main`. All functional branches, feature branches, and integration releases have been incorporated:

| Branch Name | Type | Original Role | Status | Audit Recommendation |
|---|---|---|---|---|
| `main` | Production | Primary release branch for Vercel deployments | **Active / Canonical Head** | **Keep as default deployment branch** |
| `release/hackathon-final` | Release | Monorepo integration branch (Frontend + Backend) | Merged into `main` via PR #2 | Retained as milestone branch |
| `feature/vercel-deployment` | DevOps | Vercel serverless runtime and CORS fixes | Fully synchronized with `main` (`e51b5e0`) | Safe to retire or retain |
| `feature/backend-hackathon` | Feature | Complete Phase 1–11 backend application | Merged into `main` | Safe to retire or retain |
| `feature/frontend` | Feature | Frontend UI, Tailwind palette, and test suite | Merged into `main` | Safe to retire or retain |
| `feature/backend` | Feature | Initial backend milestone | Merged into `main` | Safe to retire or retain |
| `feature/research-api` | Feature | Research services milestone | Merged into `main` | Safe to retire or retain |
| `feature/ai-engine` | Feature | AI engine verification milestone | Merged into `main` | Safe to retire or retain |

---

## 13. Honest Limitations & Roadmap

In adherence to our hard honesty principles, we note current system boundaries:
1. **Scanned PDF Optical Character Recognition (OCR):** The current pipeline detects scanned or image-only PDFs and flags them transparently. It does not attempt lossy heuristic OCR on unsearchable bitmaps.
2. **Complex Multi-Column / Tabular Data Extraction:** Figures, diagrams, and heavily nested statistical tables are identified as non-text blocks; tabular claim extraction is slated for future specialized table parsing.
3. **Scholarly API Rate Limits:** Public polite pools (Crossref, OpenAlex) may occasionally throttle rapid consecutive requests. The system gracefully falls back and labels unverified claims as `UNABLE_TO_VERIFY` rather than guessing.
4. **Offline Local Embeddings:** When cloud LLM keys (`AI_PROVIDER=none`) are not provisioned, the verification engine relies on local pretrained NLI models and numerical consistency verification, achieving ₹0 operating cost without sacrificing evidence grounding.

---

## 14. License & Team Acknowledgements

CiteVerify AI is open-source software licensed under the [MIT License](LICENSE).

Developed for **INNOVEDGE 2026 Hackathon** (Problem Statement 03):
- **Agent 1 (Frontend Architect):** Next.js 14 App Router, UI/UX Design System, Supabase Client Auth.
- **Agent 2 (Backend Architect):** FastAPI Backend, Serverless Runtime, Supabase Database & Storage, ReportLab PDF Engine.
- **Agent 3 (AI/ML Engineer):** Claim Extraction, Semantic Embedding Ranker, Pretrained NLI Verifier.
- **Agent 4 (Research Integration):** Crossref, OpenAlex, Europe PMC Scholarly Literature Integrations.
