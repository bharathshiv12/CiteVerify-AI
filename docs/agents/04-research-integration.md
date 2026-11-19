# 04. Research Integration Role Specification (Agent 4)

## 1. Responsibility
The Research Integration Engineer owns API communication with Crossref, OpenAlex, and Europe PMC, publication matching against parsed reference strings, legitimate open-access retrieval, and provenance tracking.

## 2. Directory & Branch Ownership
- **Write Access:** `research_services/**`, `tests/integration/**`
- **Primary Branch:** `feature/research-api`
- **Forbidden from Editing:** `frontend/**`, `backend/**`, `contracts/**`.

## 3. Interfaces & Contracts Consumed and Provided
- Exposes callable Python functions:
  ```python
  async def retrieve_publication(raw_reference_text: str) -> ResearchPaper: ...
  async def extract_candidate_evidence(paper: ResearchPaper) -> List[Evidence]: ...
  ```
- Consumes canonical schemas: `ResearchPaper`, `Evidence`, `RetrievalStatus`, `EvidenceLevel`.

## 4. Key Deliverables by Roadmap Window
- **Hours 0-6:** Shared HTTP client with polite pool headers, timeouts, and on-disk caching.
- **Hours 6-12:** OpenAlex and Crossref API client integrations with offline recorded fixtures.
- **Hours 12-18:** Publication fuzzy matcher with match confidence calculation and explanation.
- **Hours 18-24:** Open-access full text & abstract chunker tagging authentic `evidence_level`.

## 5. Definition of Done
- [ ] Uses polite pool headers (`OPENALEX_EMAIL`, `CROSSREF_EMAIL`).
- [ ] Offline unit tests pass using recorded fixtures in `tests/fixtures/`.
- [ ] Returns `ResearchPaper` model with valid `match_confidence` and `match_reason`.
- [ ] Tags evidence with exact `evidence_level` (`FULL_TEXT`, `ABSTRACT_ONLY`, `METADATA_ONLY`, `NONE`).

