# Workflow: AI / ML Development (Agent 3)

This workflow outlines the procedures for the AI/ML Engineer and Agent 3.

---

## 1. Scope & Ownership
- **Directory:** `ai_engine/**`
- **Branch:** `feature/ai-engine`
- **Responsibilities:**
  - Claim extraction (`claim_extractor/`): Identifying empirical, citation-worthy factual assertions.
  - Embedding service (`embedding_service/`): Local or API embeddings for cosine ranking of passages.
  - Evidence ranking & filtering (`evidence_retriever/`): Reranking candidate passages against claim text.
  - Verification engine (`verification_engine/`): LLM prompt engineering, structured JSON extraction, verdict classification, confidence scoring, and rationale generation.
  - LLM Provider Abstraction (`llm/`): Generic interface (`generate_json(prompt, schema)`) supporting Gemini, OpenAI, or local models.
  - Optional ML / Training (`training/`): Classifier fine-tuning or zero-shot evaluation (`evaluation/`).

---

## 2. Hard Constraints
1. **Source of Truth:** Never define custom claim or verification response schemas. Import schemas directly from `backend/app/schemas/` or `contracts/schemas/`.
2. **Model Weights:** NEVER commit `.pt`, `.bin`, `.safetensors`, `.onnx` files to Git. Store weights remotely if fine-tuning.
3. **Structured Validation:** Always parse and validate LLM outputs against Pydantic schemas before returning to the backend. Never trust raw unstructured text strings.

---

## 3. Development Steps
1. Configure `ai_engine/.env` with `LLM_PROVIDER=gemini` and `LLM_API_KEY`.
2. Implement `ai_engine/llm/client.py` using official SDKs or HTTP requests with exponential backoff and schema validation.
3. Version all prompt templates in `ai_engine/prompts/*.txt` or `*.j2`.
4. Run `ai_engine/tests/` to verify deterministic JSON formatting.

