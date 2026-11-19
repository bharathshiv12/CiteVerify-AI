# GEMINI.md — Instructions for Gemini & Antigravity Agents

This document guides Google Gemini / Antigravity agents operating within the **CiteVerify AI** repository (INNOVEDGE 2026 Hackathon, Problem Statement 03).

---

## 1. Project Summary & Core Principles

- **What CiteVerify AI is:** An automated academic claim and citation verification platform. It parses research paper PDFs, extracts factual claims, resolves cited literature from Crossref, OpenAlex, and Europe PMC, and runs verification against retrieved evidence passages.
- **Core Principle:** A real citation does not automatically support its claim. We verify the claim against the evidence.
- **Budget Constraint:** ₹0 budget. Free public scholarly APIs (polite pools), local open models, and free-tier cloud LLMs (Gemini API free tier) only.

### 5 Hard Honesty Rules
1. Never fabricate publications, DOIs, quotes, evidence passages, or test results.
2. Abstracts are never presented as full-text. Every evidence item explicitly sets `evidence_level` (`FULL_TEXT`, `ABSTRACT_ONLY`, `METADATA_ONLY`, `NONE`).
3. Failed retrieval is never marked as false or unsupported. It is categorized as `UNABLE_TO_VERIFY` or flagged for human review.
4. Insufficient evidence is never forced into a binary verdict; `verdict` remains `null`.
5. Every verification verdict must trace back to verifiable sources (DOI, provider, passage, level).

---

## 2. Monorepo Map & Responsibilities

```
CiteVerify-AI/
├── frontend/              # Agent 1 (Next.js 14 App Router, TypeScript, Tailwind)
├── backend/               # Agent 2 (FastAPI, PDF extraction, DB, pipeline orchestrator)
├── ai_engine/             # Agent 3 (Claim extraction, embeddings, LLM verification)
├── research_services/     # Agent 4 (Crossref, OpenAlex, Europe PMC integrations)
├── contracts/             # SHARED SSOT (OpenAPI, JSON schemas, canonical enums)
├── docs/                  # Architecture, specs, roadmap, agent assignments
└── scripts/               # Validation, environment audit, dev start scripts
```

---

## 3. Role Boundaries & Contract Enforcement

- **Contracts First:** `contracts/openapi/openapi.yaml` and `contracts/schemas/enums.json` are immutable without a team-approved `contract-change` PR.
- **No Cross-Folder Contamination:**
  - Agent 1 edits `frontend/**`.
  - Agent 2 edits `backend/**` and `scripts/**`.
  - Agent 3 edits `ai_engine/**`.
  - Agent 4 edits `research_services/**` and `tests/integration/**`.
- **Import convention:** `ai_engine` and `research_services` are Python library packages imported directly by `backend`. They are not separate microservices.

---

## 4. Key References for Gemini Agents

- Rules directory: `.agent/rules/`
- Workflows directory: `.agent/workflows/`
- Agent specification files: `docs/agents/`
- Integration guide: `docs/INTEGRATION_GUIDE.md`
- Verification script: `python scripts/validate_repo.py`

