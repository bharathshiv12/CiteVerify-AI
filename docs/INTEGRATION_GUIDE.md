# Integration Guide: Backend, AI Engine & Research Services

This guide defines the explicit Python library interfaces used by the backend orchestrator to call `ai_engine` and `research_services`.

---

## 1. Architectural Model

`ai_engine` and `research_services` are importable Python packages located in the repository root.
The backend imports them as standard Python modules:

```python
from ai_engine.claim_extractor import extract_claims
from ai_engine.embedding_service import compute_similarities
from ai_engine.verification_engine import verify_claim_against_evidence
from research_services.publication_matcher import match_and_retrieve_paper
from research_services.evidence_extractor import extract_candidate_evidence
```

All data exchanged between these packages uses canonical Pydantic v2 schemas defined in `backend/app/schemas/` (`Claim`, `Citation`, `ResearchPaper`, `Evidence`, `Verification`).

---

## 2. Interface Signatures

### 2.1. Claim Extraction (`ai_engine`)
```python
def extract_claims(
    pages: List[Dict[str, Any]],
    document_id: UUID,
) -> List[Claim]:
    """
    Parses document pages and returns structured Claim objects.
    Each claim contains: claim_text, page_number, char_span.
    """
```

### 2.2. Research Retrieval & Matching (`research_services`)
```python
async def match_and_retrieve_paper(
    raw_reference_text: str,
) -> ResearchPaper:
    """
    Queries Crossref and OpenAlex polite pools, establishment match confidence,
    and returns a canonical ResearchPaper object.
    """
```

### 2.3. Evidence Passage Extraction (`research_services`)
```python
async def extract_candidate_evidence(
    paper: ResearchPaper,
) -> List[Evidence]:
    """
    Extracts atomic passages from abstract or open-access full text,
    assigning each passage its genuine evidence_level (FULL_TEXT, ABSTRACT_ONLY).
    """
```

### 2.4. Semantic Passage Ranking (`ai_engine`)
```python
def compute_similarities(
    query_text: str,
    passages: List[str],
) -> List[float]:
    """
    Computes cosine similarity between the claim text and candidate passages.
    Returns list of similarity scores in [0.0, 1.0].
    """
```

### 2.5. Claim Verification (`ai_engine`)
```python
async def verify_claim_against_evidence(
    claim_text: str,
    evidence_items: List[Evidence],
) -> Verification:
    """
    Executes structured inference comparing claim statement with evidence.
    Returns Verification object with canonical verdict, confidence, rationale,
    and human review trigger flags.
    """
```

---

## 3. Error Handling Across Boundaries

1. **Transient Network Errors in Research APIs:** `research_services` catches HTTP errors, retries with exponential backoff up to 3 times, and falls back to `retrieval_status = API_ERROR`. It must never raise unhandled network exceptions up to the backend.
2. **LLM Output Parsing Errors:** `ai_engine` attempts structured JSON parsing and Pydantic validation. If the LLM generates invalid JSON after retries, it sets `verification_state = REQUIRES_HUMAN_REVIEW`, `verdict = null`, and `review_reasons = ["LLM_PARSING_FAILURE"]`.

