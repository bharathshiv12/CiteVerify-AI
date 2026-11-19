# 03. AI / ML Role Specification (Agent 3)

## 1. Responsibility
The AI/ML Engineer owns natural language extraction of factual claims, vector embeddings for passage semantic similarity ranking, prompt engineering for structured natural language inference (NLI), confidence scoring, and rationale generation.

## 2. Directory & Branch Ownership
- **Write Access:** `ai_engine/**`
- **Primary Branch:** `feature/ai-engine`
- **Forbidden from Editing:** `frontend/**`, `backend/**`, `contracts/**`.

## 3. Interfaces & Contracts Consumed and Provided
- Exposes callable Python functions:
  ```python
  def extract_claims(pages: List[dict], document_id: UUID) -> List[Claim]: ...
  def compute_similarities(query_text: str, passages: List[str]) -> List[float]: ...
  async def verify_claim_against_evidence(claim_text: str, evidence_items: List[Evidence]) -> Verification: ...
  ```
- Consumes canonical Pydantic schemas: `Claim`, `Evidence`, `Verification`, `VerificationVerdict`.

## 4. Key Deliverables by Roadmap Window
- **Hours 0-6:** Claim extraction prompt template with few-shot academic examples.
- **Hours 6-12:** Embedding service integration (local sentence-transformers or cloud embedding API).
- **Hours 12-18:** LLM verification prompt returning strict JSON conforming to `Verification` schema.
- **Hours 18-24:** Evaluation benchmark on small hand-labeled sample in `evaluation/`.

## 5. Definition of Done
- [ ] LLM provider client handles timeouts, retries, and schema validation errors.
- [ ] Returns valid canonical `VerificationVerdict` values (`SUPPORTED`, `PARTLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTORY`, `POTENTIALLY_OUTDATED`) or `null` on insufficient evidence.
- [ ] No model weight files committed to Git.
- [ ] Prompt templates versioned in `ai_engine/prompts/`.

