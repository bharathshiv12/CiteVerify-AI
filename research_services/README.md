# CiteVerify AI - Research Services Package

This package manages all interactions with free scholarly publication APIs (Crossref, OpenAlex, Europe PMC) for CiteVerify AI.

---

## 1. Owner & Scope
- **Owner:** Agent 4 (Research Integration Engineer)
- **Primary Branch:** `feature/research-api`
- **Budget:** ₹0. Uses polite pool free tiers only.

---

## 2. Directory Structure
```
research_services/
├── common/              # Shared HTTP client: polite pool headers, retries, cache
├── crossref/            # Crossref REST API client
├── openalex/            # OpenAlex REST API client
├── europe_pmc/          # Europe PMC client
├── publication_matcher/ # Fuzzy matching and confidence scoring
├── evidence_extractor/  # Abstract and OA passage chunker
└── tests/               # Offline tests using recorded JSON fixtures
```

---

## 3. Polite Pool Configuration
To receive higher rate limits and avoid throttling on OpenAlex and Crossref without paying, configure your email address in `.env`:
```
OPENALEX_EMAIL=your-email@institution.edu
CROSSREF_EMAIL=your-email@institution.edu
```
Requests include a descriptive header:
`User-Agent: CiteVerify/1.0 (mailto:your-email@institution.edu)`

