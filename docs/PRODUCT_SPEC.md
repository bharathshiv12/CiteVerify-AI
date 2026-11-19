# PRODUCT SPECIFICATION: CITEVERIFY AI
## INNOVEDGE 2026 Hackathon | Problem Statement 03

---

## 1. Executive Summary & Problem Statement

Academic research is experiencing a replication and citation fidelity crisis. Studies show that over **15–20% of academic citations do not actually support the factual statements they accompany**, resulting from citation copying, superficial reading of abstracts, misinterpreting statistical claims, or subtle citation gaming.

**CiteVerify AI** is an automated, evidence-grounded claim and citation verification platform. A user uploads an academic PDF; CiteVerify extracts factual claims, links attached citations, retrieves cited publications from free scholarly APIs (Crossref, OpenAlex, Europe PMC), extracts evidence passages, and evaluates whether the cited source actually substantiates the claim.

> [!IMPORTANT]
> **Core Principle:** A real citation does not automatically support its claim. We verify the claim against the evidence.

---

## 2. Target Users & Personas

1. **Peer Reviewers & Journal Editors:** Rapidly audit submitted manuscripts to verify whether critical claims in the introduction and discussion sections match their citations.
2. **Researchers & Postgraduates:** Audit their own bibliographies and literature reviews before journal submission to eliminate inadvertent citation distortion.
3. **Science Journalists & Fact-Checkers:** Check whether popular science reporting accurately reflects primary research papers cited in press releases.

---

## 3. 24-Hour MVP Scope

### Must-Have Features:
- [x] Multi-page academic PDF upload with format/magic byte validation.
- [ ] Text and section parsing with page number preservation.
- [ ] Claim extraction isolating empirical and quantitative assertions.
- [ ] In-text citation parsing (numeric `[1]` and author-year `Smith et al., 2020`).
- [ ] Bibliography reference extraction.
- [ ] Free scholarly API lookup via Crossref and OpenAlex polite pools.
- [ ] Publication matching with match confidence score and rationale.
- [ ] Passage retrieval with strict `evidence_level` categorization (`FULL_TEXT`, `ABSTRACT_ONLY`, `METADATA_ONLY`, `NONE`).
- [ ] Semantic passage ranking against claims.
- [ ] Verification engine outputting 5 canonical verdicts (`SUPPORTED`, `PARTLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTORY`, `POTENTIALLY_OUTDATED`) or `null` for insufficient evidence.
- [ ] Human review flagging and review feedback submission.
- [ ] Interactive web dashboard showing overall reliability score and traceable evidence cards.

---

## 4. Explicit Non-Goals (Out of Scope for 24h Hackathon)

- **Optical Character Recognition (OCR):** Scanned image PDFs are flagged as `is_scanned=True` with a notice that OCR is out of scope.
- **User Authentication / Paywalls:** No login, user accounts, or billing gateways.
- **Paid APIs:** ₹0 budget. Zero dependence on paid APIs (e.g. Scopus, Web of Science, IEEE Xplore paid tiers).
- **Batch Processing:** Single document upload per verification session.
- **Automatic PDF re-writing:** The system flags and audits; it does not rewrite text for authors.

---

## 5. Live Demo Script (3-Minute Presentation)

1. **0:00 - 0:30 (The Hook):** State the problem: "How many citations in this paper actually say what the authors claim they say?" Show an example paper where an author cites a paper claiming 95% accuracy when the source reported 72%.
2. **0:30 - 1:00 (Upload & Pipeline):** Upload a sample open-access paper. Show the live status progression (`TEXT_EXTRACTION` -> `CLAIM_EXTRACTION` -> `PAPER_RETRIEVAL` -> `VERIFICATION`).
3. **1:00 - 2:00 (Dashboard & Traceability):**
   - Highlight the **Reliability Score** (e.g. 82%).
   - Show a **SUPPORTED** claim side-by-side with the highlighted abstract excerpt.
   - Show a **CONTRADICTORY** claim where CiteVerify caught a misquotation.
   - Show an **UNABLE_TO_VERIFY** claim with an `ABSTRACT_ONLY` badge demonstrating honesty.
4. **2:00 - 2:30 (Human-in-the-loop):** Demonstrate an expert reviewer reviewing a flagged claim, updating the verdict, and saving the note to audit history.
5. **2:30 - 3:00 (Architecture & Zero-Cost):** Highlight the monorepo architecture, ₹0 budget using OpenAlex/Crossref polite pools, and contract-driven parallel development.

---

## 6. Judging Angles & Evaluation Criteria

- **Technical Execution & Reliability:** Contract-first monorepo, 100% test pass rate, typed interfaces.
- **Intellectual Honesty:** Never fabricating evidence; clear distinction between full-text and abstract; no hallucinated certainty.
- **User Experience:** Clean Next.js dashboard, intuitive color-coded verdicts, traceable evidence cards.
- **Feasibility & Scalability:** Operates within ₹0 cost using open scholarly infrastructure.

