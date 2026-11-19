# CiteVerify AI — Frontend Architecture & Developer Guide

**Project:** CiteVerify AI (INNOVEDGE 2026 Hackathon, Problem Statement 03)  
**Agent:** Agent 1 — Frontend Developer  
**Status:** Production-Ready & Verified  
**Tagline:** *"Verify the Claim. Trace the Evidence. Trust the Research."*  

---

## 1. Project Purpose & Scientific Integrity

CiteVerify AI is an evidence-first academic claim and citation verification platform. It allows researchers, peer reviewers, students, and institutions to upload research paper PDFs and systematically evaluate whether factual assertions are genuinely supported by cited literature retrieved via Crossref, OpenAlex, and Europe PMC.

### Core Principle
> **A real citation does not automatically support its claim. We verify the claim against the evidence.**

### Scientific Honesty Rules
1. **Never fabricate:** Zero invented DOIs, publications, evidence passages, citations, or metrics.
2. **Abstracts vs. Full Text:** Abstracts are never labelled as full text (`evidence_level`: `FULL_TEXT`, `ABSTRACT_ONLY`, `METADATA_ONLY`, `NONE`).
3. **Retrieval failure is not refutation:** Unretrievable publications are categorized as `UNABLE_TO_VERIFY` or flagged for human review, never marked false.
4. **No coerced verdicts:** Claims with insufficient evidence carry `verdict: null` and prompt expert human review.
5. **Full traceability:** Every verdict traces to a source DOI/URL, provider, section, and evidence passage.

---

## 2. Technology Stack

- **Framework:** Next.js 14.2.15 (App Router, Server & Client Components)
- **Language:** TypeScript 5.6.3 (Strict mode, zero `any`)
- **Styling:** Tailwind CSS 3.4.13 with locked CSS custom properties
- **Data Fetching:** TanStack React Query v5 (2-second polling with automatic window focus pauses)
- **Authentication:** Supabase SSR Auth with anon public key (zero service-role keys in client)
- **Icons:** Lucide React
- **Test Runner:** Node.js native test runner (`node:test`, `node:assert`)

---

## 3. Route Map

### Public Routes
- `/`: Academic landing page with core principles, pipeline architecture, and live backend health probe.
- `/login`: Academic login with remember-me, password visibility toggle, and unconfigured-auth guest fallback.
- `/signup`: Registration with academic institution capture, password strength checklist, and draft policy acceptance.
- `/forgot-password`: Recovery request with neutral confirmation.
- `/reset-password`: Supabase password update workflow.
- `/auth/callback`: OAuth / magic-link token exchange.
- `/terms`: Honest prototype terms of service (Draft).
- `/privacy`: Honest prototype privacy policy (Draft).

### Authenticated & Workspace Routes
- `/dashboard`: Comprehensive workspace metrics, donut verdict breakdown, recent verifications, and quick actions.
- `/verify`: Stage 01 PDF file uploader with binary validation (`%PDF-`), size checks, and pipeline dispatcher.
- `/verify/[documentId]/[stage]`: 6-stage workflow runner (`upload`, `extract`, `map`, `retrieve`, `compare`, `verify`).
- `/reports`: Paginated list of verified manuscript reports with reliability scores and download links.
- `/reports/[documentId]`: Synthesized academic integrity report with print stylesheet (`window.print`), JSON export, and audit trails.
- `/history`: Local device document registry with status filters and device-purging confirmation dialog.
- `/settings`: Academic profile management, theme toggle (Light / Dark / System), notification preferences, and password change.
- `/design-system`: Non-production living styleguide and component showcase.

---

## 4. Design System & Locked Brand Palette

| Token | Hex Code | Usage |
|---|---|---|
| `--bg` | `#FFF8E8` | Canvas background |
| `--card` | `#FFFFFF` | Card & table surface |
| `--primary` | `#F4B860` | Primary buttons, active rings, progress |
| `--secondary` | `#FFDCA8` | Secondary buttons, active navigation background |
| `--highlight` | `#FFF0D6` | Sidebar surface, callouts |
| `--heading` | `#8D6E63` | Section headings, primary labels |
| `--border` | `#F0E4D2` | Dividers and card borders |
| `--ink` | `#3E2F27` | Primary text and button text |
| `--ink-muted` | `#7A685D` | Secondary metadata and captions |

### Button Specifications
- **Primary:** `#F4B860` background, `#3E2F27` text, 10px radius, no gradient, no white text.
- **Secondary:** `#FFDCA8` background, `#3E2F27` text, 10px radius, no gradient.
- **Ghost / Outline:** `#A08B78` border, `#3E2F27` text, 10px radius.

---

## 5. Development & Execution Commands

### Prerequisites
- Node.js v20+ LTS
- npm v10+

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```

### Type Checking
```bash
npm run typecheck
```

### Code Linting
```bash
npm run lint
```

### Unit Tests
```bash
npm test
```

### Production Build
```bash
npm run build
```

---

## 6. Environment Variables (`frontend/.env.example`)

```env
# Base URL of the CiteVerify FastAPI backend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Synthetic mock payload toggle (set to 'true' for offline UI demo with SAMPLE DATA banner)
NEXT_PUBLIC_USE_MOCKS=false

# Optional Supabase credentials for user authentication
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=

# Maximum upload file size in Megabytes (default 25)
NEXT_PUBLIC_MAX_UPLOAD_MB=25
```

---

## 7. Verified Completion Checklist

- [x] All 10 required unit test suites passing (10/10).
- [x] Zero TypeScript compilation errors (`tsc --noEmit`).
- [x] Zero ESLint errors or warnings (`next lint`).
- [x] Production build passes (`next build`).
- [x] Locked brand colors and button specifications strictly preserved.
- [x] Contract gaps documented in `CONTRACT_GAPS.md`.
- [x] Git branch `feature/frontend` cleanly isolated; no changes outside `frontend/`.
