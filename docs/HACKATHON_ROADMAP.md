# 24-Hour Hackathon Execution Roadmap (INNOVEDGE 2026)

This roadmap coordinates the 4 parallel developers and AI coding agents across the 24-hour hackathon timeframe.

---

## 1. Execution Timeline & Milestones

| Window | Milestone Focus | Deliverables & Responsibilities | Owner(s) |
|---|---|---|---|
| **Hours 0–2** | **Foundation & Contracts** (CURRENT) | - Environment audit, repo skeleton, config files<br>- Canonical contracts (`enums.json`, OpenAPI, JSON schemas)<br>- Pydantic models & TypeScript interfaces<br>- Stubs with docstrings, `GET /api/health` 100% verified | All Roles / Lead |
| **Hours 2–6** | **Ingestion & Extraction** | - Backend: Multi-page PDF text extraction (`document_processor.py`)<br>- Backend: Citation & bibliography parsing (`citation_parser.py`)<br>- AI: Few-shot claim extraction prompt (`ai_engine/claim_extractor/`)<br>- Frontend: Landing page, dropzone, and mock dashboard | Agent 1 (UI)<br>Agent 2 (Parser)<br>Agent 3 (Claims) |
| **Hours 6–10** | **Scholarly API Integrations** | - Research: Crossref & OpenAlex client with polite pool and disk cache<br>- Research: Publication matcher with confidence scoring<br>- Research: Candidate evidence extraction from abstracts/OA text<br>- Backend: Wire research retrieval into background worker | Agent 4 (Research)<br>Agent 2 (Backend) |
| **Hours 10–15** | **AI Verification Engine** | - AI: Passage ranking using semantic similarity embeddings<br>- AI: LLM structured inference prompt comparing claim vs evidence<br>- AI: Rationale generation, confidence score, and review flags<br>- Backend: Connect AI verification to claims database | Agent 3 (AI/ML)<br>Agent 2 (Backend) |
| **Hours 15–18** | **Full-Stack Integration (Thin Slice)** | - Connect frontend to live backend (`NEXT_PUBLIC_USE_MOCKS=false`)<br>- End-to-end verification of first real academic PDF<br>- Claim drawer showing real evidence passages and provenance<br>- Human review submission endpoint wired to UI | All 4 Agents |
| **Hours 18–21** | **Report Synthesis & Hardening** | - Backend: Final report compilation and reliability scoring (0–100)<br>- Frontend: Summary statistics cards, download report summary<br>- End-to-end testing with 2–3 open-access benchmark papers<br>- Error handling for paywalled or missing DOIs | All 4 Agents |
| **Hours 21–24** | **Deployment & Demo Prep** | - Deploy frontend to Vercel and backend to Render/Railway<br>- Rehearse 3-minute judging script and slide deck<br>- Record fallback demo video in case of venue network latency | All 4 Agents / Lead |

---

## 2. Scope Boundaries

### MVP Must-Haves (Do not deviate):
1. Clean PDF upload with magic byte rejection.
2. Accurate extraction of factual, citation-worthy claims.
3. Retrieval of cited papers from OpenAlex / Crossref without paid keys.
4. Passage comparison outputting canonical verdicts (`SUPPORTED`, `CONTRADICTORY`, etc.).
5. Evidence level badge (`FULL_TEXT` vs `ABSTRACT_ONLY`) on every claim.
6. Traceable citation report with human review flags.

### Prohibited Scope Traps ("DO NOT START UNTIL MVP WORKS"):
- ❌ User authentication, sign-up, JWTs, or passwords.
- ❌ OCR for scanned/handwritten documents (flag and reject gracefully).
- ❌ Multi-file batch processing.
- ❌ PDF highlight rendering or in-browser PDF viewers.
- ❌ Complex export formats (LaTeX, Word docx export).
- ❌ Self-hosted vector databases (Qdrant, Pinecone); in-memory cosine ranking is sufficient.

