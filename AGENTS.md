# AGENTS.md — Global Multi-Agent Instructions: CiteVerify AI

Welcome to **CiteVerify AI**, built for INNOVEDGE 2026 Hackathon (Problem Statement 03).
This document provides autonomous AI coding agents and human teammates with the architectural boundaries, ownership rules, and operational protocols of this monorepo.

---

## 1. Condensed Project Identity & Core Principle

**What we build:** A web application where an academic user uploads a research paper PDF. The system extracts factual claims, links attached citations, retrieves cited publications from free scholarly APIs (Crossref, OpenAlex, Europe PMC), extracts evidence passages, and evaluates whether the cited publication genuinely supports the factual assertion.

> [!IMPORTANT]
> **Core Principle:** A real citation does not automatically support its claim. We verify the claim against the evidence.

### Hard Honesty Rules
1. **Never fabricate:** Never invent publications, DOIs, evidence passages, citations, benchmark results, or test passes.
2. **Abstracts vs. Full Text:** An abstract is never presented as full text. Every evidence item carries an explicit `evidence_level` (`FULL_TEXT`, `ABSTRACT_ONLY`, `METADATA_ONLY`, `NONE`).
3. **Retrieval failure is not refutation:** A paper that cannot be retrieved is not an invalid reference. It is marked `UNABLE_TO_VERIFY` or flagged for human review.
4. **Insufficient evidence is never forced into a binary verdict:** A claim with insufficient evidence has `verdict = null` and `verification_state = UNABLE_TO_VERIFY` or `REQUIRES_HUMAN_REVIEW`.
5. **Traceability:** Every verdict must be traceable to a source (DOI/URL, provider, passage, evidence level).

---

## 2. 16-Step Pipeline Overview

1. User uploads academic PDF.
2. Backend validates magic bytes (`%PDF-`), MIME, extension, size limit.
3. PDF processor extracts text and detects scanned/image PDFs.
4. Claim extractor isolates factual, empirical statements.
5. Citation parser detects numeric (`[1]`, `[1-3]`) and author-year (`Smith et al., 2020`) markers.
6. Reference parser parses the bibliography section.
7. Citation matcher links each claim to its bibliography references.
8. Research services query Crossref and OpenAlex (Europe PMC for biomedical).
9. Publication metadata is matched with match confidence and explanation.
10. Legitimate open-access abstracts/full-text are fetched.
11. Evidence extractor chunks candidate passages.
12. Embedding service ranks passages semantically against the claim.
13. Verification engine compares the exact claim with evidence.
14. Structured JSON results are produced and validated against the schema.
15. Human-review flags are assigned.
16. Dashboard and final report display results with audit history.

---

## 3. Four Agent Team Ownership & Boundaries

| Agent | Role | Owned Directory (Write Access) | Working Branch |
|---|---|---|---|
| **Agent 1** | Frontend Architect | `frontend/**` | `feature/frontend` |
| **Agent 2** | Backend Architect | `backend/**`, `scripts/**` | `feature/backend` |
| **Agent 3** | AI/ML Engineer | `ai_engine/**` | `feature/ai-engine` |
| **Agent 4** | Research Integration | `research_services/**`, `tests/integration/**` | `feature/research-api` |

### Strict Boundaries:
- **Agent 2 (Backend)** must never overwrite or modify frontend UI files.
- **Agent 1 (Frontend)** must never modify backend business logic or database layers.
- **Agent 3 (AI/ML)** must not redefine API response schemas in `ai_engine/`.
- **Agent 4 (Research)** must reuse canonical `ResearchPaper` and `Evidence` models, never create duplicates.

---

## 4. Contracts Are the Source of Truth

The canonical contract resides in:
- `contracts/openapi/openapi.yaml`
- `contracts/schemas/enums.json`
- `contracts/schemas/*.schema.json`

**Rules:**
- `backend/app/schemas/` and `frontend/types/` are direct downstream projections of `contracts/`.
- **Nobody invents, renames, or drops fields independently.**
- If you need a schema change, stop and raise a `contract-change` PR requiring approval from all 4 roles before code is merged.
- Run `python scripts/validate_repo.py` before committing.

---

## 5. Pointer to Detailed Guides

- Rules: `.agent/rules/` (`project-rules.md`, `coding-standards.md`, `api-contract-rules.md`, `git-collaboration.md`)
- Workflows: `.agent/workflows/`
- Agent Specific Roles: `docs/agents/` (`00-overview.md`, `01-frontend.md`, `02-backend.md`, `03-ai-ml.md`, `04-research-integration.md`, `OWNERSHIP.md`)
- Architecture: `docs/ARCHITECTURE.md`
- Integration: `docs/INTEGRATION_GUIDE.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`

