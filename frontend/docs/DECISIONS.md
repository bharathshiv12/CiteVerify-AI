# Architecture and Implementation Decisions — CiteVerify Frontend

**Agent:** Agent 1 — Frontend Developer  
**Project:** CiteVerify AI (INNOVEDGE 2026 Hackathon)  
**Date:** 2026-11-19  

---

## 1. Framework and Runtime
- **Framework:** Next.js 14.2.15 (App Router with Server/Client Components).
- **React Version:** React 18.3.1.
- **Node.js & npm:** Node.js v20.18.1 LTS, npm 10.8.2.
- **Language:** TypeScript 5.6.3 with strict type checking.
- **Styling:** Tailwind CSS 3.4.13 with CSS custom properties (`var(--...)`) mapped to theme tokens.

---

## 2. Brand and Design System Decisions
- **Immutable Brand Color Tokens:**
  - Background (`--bg`): `#FFF8E8`
  - Cards (`--card`): `#FFFFFF`
  - Primary (`--primary`): `#F4B860`
  - Secondary (`--secondary`): `#FFDCA8`
  - Highlight (`--highlight`): `#FFF0D6`
  - Heading (`--heading`): `#8D6E63`
  - Border (`--border`): `#F0E4D2`
- **Derived Supporting Tokens:**
  - Ink (`--ink`): `#3E2F27`
  - Muted Ink (`--ink-muted`): `#7A685D`
  - Input Border (`--border-input`): `#A08B78`
  - Focus Ring (`--focus`): `#8D6E63`
- **Semantic Verification Palette (Verdict / Icon / Pale BG / Badge Text):**
  - Supported: `#39765B` / `#E4F1EA` / `#1F5A42`
  - Partially Supported: `#B68A42` / `#F7EBCF` / `#7A5A14`
  - Unsupported: `#B94D4D` / `#F6E1E1` / `#8F2E2E`
  - Contradictory: `#74518C` / `#EDE3F3` / `#54346B`
  - Potentially Outdated: `#B77B35` / `#F8E7D2` / `#8A5214`
  - Needs Human Review: `#766F68` / `#ECE8E4` / `#4F4943`
- **Button Standards:**
  - Primary: `#F4B860` background, `#3E2F27` text, 10px radius, no gradient, no white text.
  - Secondary: `#FFDCA8` background, `#3E2F27` text, 10px radius, no gradient.
  - Ghost / Outline: `#A08B78` border, `#3E2F27` text, 10px radius.
- **Typography:**
  - Headings: Manrope
  - Body & UI: Inter
  - Technical metadata: IBM Plex Mono

---

## 3. Confidence Thresholds
Centralized in `frontend/lib/constants/verdicts.ts`:
- **High Confidence:** `confidence >= 0.75`
- **Medium Confidence:** `confidence >= 0.50 && confidence < 0.75`
- **Low Confidence:** `confidence < 0.50`
- Explanatory tooltip: *"Confidence reflects how strong the retrieved evidence is. It does not guarantee the claim is true or false."*

---

## 4. Pipeline and Verification State Mapping
- UI 6-Stage Workflow mapped to canonical `PipelineStage` enums:
  1. `01 Upload`: `UPLOADED`
  2. `02 Extract`: `TEXT_EXTRACTION`, `CLAIM_EXTRACTION`, `CITATION_PARSING`, `REFERENCE_PARSING`
  3. `03 Map Citations`: `CITATION_MATCHING`
  4. `04 Retrieve Research`: `PAPER_RETRIEVAL`
  5. `05 Compare Evidence`: `EVIDENCE_EXTRACTION`
  6. `06 Verify`: `VERIFICATION`, `REPORT_GENERATION`, `DONE`
- **Honesty Rule for Null Verdict:** If `claim.verdict === null`, it is rendered as **"Needs Human Review / Unable to Verify"** with an amber/slate badge. It is **never** coerced to `UNSUPPORTED`.

---

## 5. Authentication & Storage
- Supabase Auth using client anon key only (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`).
- When credentials are absent, an honest banner and empty state are displayed (*"Authentication is not configured"*).
- Password validation requirements:
  - Minimum 8 characters.
  - At least one uppercase letter.
  - At least one lowercase letter.
  - At least one number.
- Document history is stored in a local device registry (`frontend/lib/document-registry.ts`) keyed by user or anonymous session, deduplicated by `document_id`.

---

## 6. Mock Mode Architecture
- Activated only when `NEXT_PUBLIC_USE_MOCKS=true`.
- Sourced strictly from canonical `contracts/examples/`:
  - `contracts/examples/synthetic_document.json`
  - `contracts/examples/synthetic_claims.json`
  - `contracts/examples/synthetic_report.json`
- Renders a persistent `SAMPLE DATA` banner across all screens when active.
