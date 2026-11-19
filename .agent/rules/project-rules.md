# Rule: Project Ground Rules & Honesty Protocols

Every agent working on CiteVerify AI must adhere strictly to these principles:

---

## 1. Zero Tolerance for Fabrication
- Never invent academic papers, author names, DOIs, or URLs.
- Never forge citation evidence or quote passages that do not exist in the source literature.
- Never fabricate test results, benchmarks, or accuracy metrics.
- If a source paper is paywalled or cannot be reached via open-access APIs, record its retrieval status as `PAYWALLED` or `NOT_FOUND` and mark the claim as `UNABLE_TO_VERIFY` with `needs_human_review = true`.

---

## 2. Evidence Level Integrity
- Every evidence passage extracted must be tagged with its authentic `evidence_level`:
  - `FULL_TEXT`: Legitimate open-access full-text passage.
  - `ABSTRACT_ONLY`: Abstract retrieved from OpenAlex, Crossref, or Europe PMC.
  - `METADATA_ONLY`: Title, venue, year, or authors only (no text available).
  - `NONE`: No evidence found.
- **Never present an abstract snippet as full-text evidence.**

---

## 3. Verdict Rigor
- Do not force a claim into a verdict if evidence is inconclusive.
- When evidence is insufficient, `verdict` MUST be `null`, and `verification_state` set to `UNABLE_TO_VERIFY` or `REQUIRES_HUMAN_REVIEW`.
- Verification verdicts are strictly:
  - `SUPPORTED`: Empirical data explicitly validates the claim.
  - `PARTLY_SUPPORTED`: Data partially aligns, has unaddressed caveats, or limited scope.
  - `UNSUPPORTED`: Source discusses topic but offers no validating data.
  - `CONTRADICTORY`: Source evidence directly refutes the claim.
  - `POTENTIALLY_OUTDATED`: Source supported it originally, but newer literature supersedes it.

---

## 4. Zero Cost Budget (₹0)
- Use only free public APIs (OpenAlex polite pool, Crossref polite pool, Europe PMC).
- Use free-tier models (Gemini API free tier) or local models (HuggingFace sentence-transformers).
- Do not introduce paid dependencies, subscriptions, or credit card requirements.

