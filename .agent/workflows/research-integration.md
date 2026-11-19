# Workflow: Research Integration (Agent 4)

This workflow outlines the procedures for the Research Integration Engineer and Agent 4.

---

## 1. Scope & Ownership
- **Directory:** `research_services/**`, `tests/integration/**`
- **Branch:** `feature/research-api`
- **Responsibilities:**
  - Common HTTP Client (`common/`): Connection pooling, polite pool headers (`User-Agent: CiteVerify/1.0 (mailto:email)`), exponential backoff, rate limiting, and local cache.
  - Crossref Client (`crossref/`): Free metadata and DOI querying via Crossref REST API.
  - OpenAlex Client (`openalex/`): Fast, rich publication matching, OA status, and abstract inverted index reconstruction.
  - Europe PMC Client (`europe_pmc/`): Biomedical paper lookup and open-access full-text retrieval.
  - Publication Matcher (`publication_matcher/`): Fuzzy & exact matching between parsed reference strings and API results, computing match confidence scores.
  - Evidence Extractor (`evidence_extractor/`): Abstract or full-text chunking with explicit `evidence_level` tagging.

---

## 2. Hard Constraints
- **Model Re-use:** Return canonical `ResearchPaper` and `Evidence` models from `app.schemas`. Do not create duplicate domain models.
- **Polite Pool Compliance:** Always send `OPENALEX_EMAIL` and `CROSSREF_EMAIL` in headers.
- **Fixture Tests:** Never commit live API calls to unit tests. Use recorded JSON response fixtures in `research_services/tests/fixtures/`.
- **Licensing:** Only download and parse full text where open access licenses (`cc-by`, public domain) are legitimately established.

