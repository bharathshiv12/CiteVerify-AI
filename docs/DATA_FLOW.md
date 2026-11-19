# End-to-End Pipeline Data Flow

This document details the lifecycle of data as it passes through each stage of the CiteVerify AI verification pipeline.

---

## 1. Pipeline Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as Frontend (Next.js)
    participant Backend as Backend (FastAPI)
    participant Extractor as Text & Citation Processor
    participant Research as Research Services (APIs)
    participant AI as AI Engine (LLM & Embeddings)
    participant DB as Repository (Persistence)

    User->>Frontend: Select & upload academic PDF
    Frontend->>Backend: POST /api/documents/upload (multipart)
    Backend->>Backend: Validate extension, MIME, magic bytes (%PDF-)
    Backend->>DB: Store Document (status: PENDING)
    Backend-->>Frontend: 201 Created (Document JSON)

    Frontend->>Backend: POST /api/documents/{id}/analyze
    Backend->>DB: Update Document (status: PROCESSING)
    Backend-->>Frontend: 202 Accepted (Background task enqueued)

    loop Polling Status
        Frontend->>Backend: GET /api/documents/{id}/status
        Backend-->>Frontend: 200 OK (current stage & progress %)
    end

    Note over Backend,Extractor: Stage 1-3: Text Extraction
    Backend->>Extractor: Extract text per page & check text layer
    Extractor-->>Backend: pages[] & is_scanned flag

    Note over Backend,AI: Stage 4: Claim Extraction
    Backend->>AI: Extract factual empirical statements from text
    AI-->>Backend: claims[] (claim_text, page, char_span)

    Note over Backend,Extractor: Stage 5-7: Citation Parsing & Matching
    Backend->>Extractor: Parse markers [1], (Smith, 2020) & References
    Extractor-->>Backend: citations[] & references map
    Backend->>Backend: Match in-text citations to claim sentences

    Note over Backend,Research: Stage 8-10: Publication Retrieval
    Backend->>Research: Query Crossref / OpenAlex for parsed references
    Research-->>Backend: ResearchPaper (DOI, abstract, OA URL, match_confidence)

    Note over Backend,Research: Stage 11: Candidate Evidence Extraction
    Backend->>Research: Chunk abstract / open-access text into passages
    Research-->>Backend: Candidate evidence[] (tagged with EvidenceLevel)

    Note over Backend,AI: Stage 12-14: Ranking & Verification
    Backend->>AI: Compute semantic similarity between claim & passages
    AI-->>Backend: Ranked passages
    Backend->>AI: LLM Verification Prompt (claim vs top evidence)
    AI-->>Backend: Verification (verdict, confidence, rationale, review flags)

    Note over Backend,DB: Stage 15-16: Final Report Assembly
    Backend->>Backend: Compile summary metrics & reliability score
    Backend->>DB: Persist claims, evidence, verifications
    Backend->>DB: Update Document (status: COMPLETED, stage: DONE)

    Frontend->>Backend: GET /api/documents/{id}/report
    Backend-->>Frontend: 200 OK (VerificationReport JSON)
    Frontend->>User: Render Dashboard, Evidence Cards & Reliability Score
```

---

## 2. Pipeline Stage Details & Artifacts

| Stage | Name | Input | Output | Primary Component |
|---|---|---|---|---|
| **1** | Upload | Binary PDF bytes from user | Staged file in `uploads/` | `app/api/routes/documents.py` |
| **2** | Validation | Binary file header & metadata | Validated file or error envelope | `app/processors/upload_validator.py` |
| **3** | Text Extraction | Staged PDF | Page-by-page text, page count | `app/services/document_processor.py` |
| **4** | Claim Extraction | Page text | List of candidate factual claims | `ai_engine/claim_extractor/` |
| **5** | Citation Parsing | Body text | In-text markers (`[1]`, `Smith et al.`) | `app/services/citation_parser.py` |
| **6** | Reference Parsing | End-of-document text | Parsed bibliography dictionary | `app/services/citation_parser.py` |
| **7** | Citation Matching | Claims & citations | Claims linked to reference text | `app/services/citation_matcher.py` |
| **8** | API Lookup | Reference strings | Scholarly records (Crossref/OpenAlex) | `research_services/` |
| **9** | Match Resolution | Query vs API metadata | `ResearchPaper` with match confidence | `research_services/publication_matcher/` |
| **10**| Text Retrieval | DOI / OpenAlex ID | Abstract or legitimate open-access text | `research_services/` |
| **11**| Evidence Chunking | Paper text/abstract | Atomic passages with `EvidenceLevel` | `research_services/evidence_extractor/` |
| **12**| Semantic Ranking | Claim text & passages | Cosine similarity scores | `ai_engine/embedding_service/` |
| **13**| Verification | Claim + Top evidence passages | NLI inference outcome | `ai_engine/verification_engine/` |
| **14**| Schema Validation | Raw LLM output | Validated `Verification` object | `ai_engine/llm/` |
| **15**| Review Flagging | Confidence, contradictions | `needs_human_review` & trigger reasons | `ai_engine/verification_engine/` |
| **16**| Report Synthesis | All claims & verifications | `VerificationReport` with score (0-100) | `app/services/report_generator.py` |

