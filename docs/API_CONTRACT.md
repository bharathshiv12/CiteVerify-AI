# CiteVerify AI - Complete API Contract Specification

This document details the HTTP REST API contract implemented by CiteVerify AI. All endpoints are rooted under `/api`.

---

## 1. Global Conventions

1. **Identifiers**: All resource identifiers (`id`, `document_id`, `claim_id`, `paper_id`, `citation_id`, `evidence_id`) are standard UUID v4 strings (e.g. `550e8400-e29b-41d4-a716-446655440000`).
2. **Timestamps**: All dates and timestamps are formatted as ISO 8601 UTC strings (`YYYY-MM-DDTHH:MM:SSZ`).
3. **Casing**: All JSON keys are strictly in `snake_case`. Frontend TypeScript interfaces mirror `snake_case` directly to eliminate serialization conversion layers.
4. **Standard Error Envelope**:
   ```json
   {
     "error": {
       "code": "ERROR_CODE_STRING",
       "message": "Human-readable explanation of error.",
       "details": {},
       "request_id": "uuid-v4-string"
     }
   }
   ```
5. **Standard List Envelope**:
   ```json
   {
     "items": [],
     "page": 1,
     "page_size": 20,
     "total": 0
   }
   ```
6. **Honesty Principle in Models**:
   - `verdict` is nullable: when evidence is insufficient or unavailable, `verdict = null` and `verification_state = UNABLE_TO_VERIFY` or `REQUIRES_HUMAN_REVIEW`.
   - Every piece of evidence carries an explicit `evidence_level` (`FULL_TEXT`, `ABSTRACT_ONLY`, `METADATA_ONLY`, `NONE`).

---

## 2. Enumerations Reference

See canonical `contracts/schemas/enums.json`:
- **`VerificationVerdict`**: `SUPPORTED`, `PARTLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTORY`, `POTENTIALLY_OUTDATED`
- **`ProcessingStatus`**: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`
- **`VerificationState`**: `VERIFIED`, `REQUIRES_HUMAN_REVIEW`, `UNABLE_TO_VERIFY`, `PENDING`
- **`EvidenceLevel`**: `FULL_TEXT`, `ABSTRACT_ONLY`, `METADATA_ONLY`, `NONE`
- **`RetrievalStatus`**: `RETRIEVED`, `NOT_FOUND`, `PAYWALLED`, `API_ERROR`
- **`PipelineStage`**: `UPLOADED`, `TEXT_EXTRACTION`, `CLAIM_EXTRACTION`, `CITATION_PARSING`, `REFERENCE_PARSING`, `CITATION_MATCHING`, `PAPER_RETRIEVAL`, `EVIDENCE_EXTRACTION`, `VERIFICATION`, `REPORT_GENERATION`, `DONE`

---

## 3. Endpoints

### 3.1. GET /api/health
- **Purpose**: Liveness and diagnostic probe.
- **Request Format**: None.
- **Response Format**: `application/json`
- **Status Codes**: `200 OK`
- **Expected Behavior**: Responds immediately with status, service identifier, version, and server UTC timestamp.
- **Example Response**:
  ```json
  {
    "status": "ok",
    "service": "citeverify-backend",
    "version": "1.0.0",
    "timestamp": "2026-11-19T10:00:00Z"
  }
  ```

---

### 3.2. POST /api/documents/upload
- **Purpose**: Accepts and validates an academic PDF upload.
- **Request Format**: `multipart/form-data` with field `file` (binary PDF, max 25MB).
- **Validation Checks**:
  1. Filename must end with `.pdf` (case-insensitive).
  2. MIME type must be `application/pdf`.
  3. Magic bytes must begin with `%PDF-` (`0x25 0x50 0x44 0x46 0x2D`).
  4. Payload size must be greater than 0 bytes and not exceed `MAX_UPLOAD_SIZE_MB` (default 25MB).
- **Status Codes**:
  - `201 Created`: File accepted and saved to staging.
  - `400 Bad Request`: Missing file, invalid extension, or corrupted magic bytes.
  - `413 Payload Too Large`: Upload exceeds maximum allowed file size.
- **Example Response (`201 Created`)**:
  ```json
  {
    "id": "e4f8d9b2-3c1a-4d5e-9f8a-1b2c3d4e5f6a",
    "filename": "quantum_transformers_2026.pdf",
    "file_size_bytes": 2458900,
    "mime_type": "application/pdf",
    "status": "PENDING",
    "pipeline_stage": "UPLOADED",
    "page_count": null,
    "is_scanned": false,
    "error_message": null,
    "created_at": "2026-11-19T10:05:00Z",
    "updated_at": "2026-11-19T10:05:00Z"
  }
  ```
- **Example Error Response (`400 Bad Request`)**:
  ```json
  {
    "error": {
      "code": "INVALID_PDF_MAGIC_BYTES",
      "message": "The uploaded file does not contain valid PDF magic bytes (%PDF-).",
      "details": { "detected_header": "47494638" },
      "request_id": "8f2a1c90-9941-4c5b-9988-123456789abc"
    }
  }
  ```

---

### 3.3. POST /api/documents/{document_id}/analyze
- **Purpose**: Enqueues background verification pipeline for an uploaded document.
- **Parameters**: `document_id` (UUID in path).
- **Request Format**: Empty body or optional config parameters.
- **Expected Behavior**: Spawns an asynchronous background task orchestrating the 16 pipeline stages without blocking the HTTP worker. Immediately updates status to `PROCESSING`.
- **Status Codes**:
  - `202 Accepted`: Job queued.
  - `404 Not Found`: Document ID does not exist.
  - `409 Conflict`: Analysis is already running or already completed.
- **Example Response (`202 Accepted`)**:
  ```json
  {
    "document_id": "e4f8d9b2-3c1a-4d5e-9f8a-1b2c3d4e5f6a",
    "status": "PROCESSING",
    "pipeline_stage": "TEXT_EXTRACTION",
    "message": "Document analysis pipeline started in background."
  }
  ```

---

### 3.4. GET /api/documents/{document_id}/status
- **Purpose**: Polling endpoint for frontend processing screens.
- **Parameters**: `document_id` (UUID in path).
- **Status Codes**:
  - `200 OK`
  - `404 Not Found`
- **Example Response (`200 OK`)**:
  ```json
  {
    "document_id": "e4f8d9b2-3c1a-4d5e-9f8a-1b2c3d4e5f6a",
    "status": "PROCESSING",
    "pipeline_stage": "EVIDENCE_EXTRACTION",
    "progress_percent": 65,
    "total_claims_found": 14,
    "verified_claims_count": 9,
    "error_message": null
  }
  ```

---

### 3.5. GET /api/documents/{document_id}/claims
- **Purpose**: Retrieves paginated claims with filtering options.
- **Parameters**:
  - `document_id` (path, required)
  - `verdict` (query, optional: `VerificationVerdict`)
  - `needs_review` (query, optional: `boolean`)
  - `page` (query, optional integer, default 1)
  - `page_size` (query, optional integer, default 20)
- **Status Codes**:
  - `200 OK`
  - `404 Not Found`
- **Example Response (`200 OK`)**:
  ```json
  {
    "items": [
      {
        "id": "7b1c4e2a-0a9f-4d32-8b3e-7a91283c4d5e",
        "document_id": "e4f8d9b2-3c1a-4d5e-9f8a-1b2c3d4e5f6a",
        "claim_text": "Transformer architectures reduce training time across machine translation tasks by over 30%.",
        "page_number": 3,
        "char_span": [412, 508],
        "citations": [
          {
            "id": "9a8b7c6d-5e4f-3a2b-1c0d-e1f2a3b4c5d6",
            "document_id": "e4f8d9b2-3c1a-4d5e-9f8a-1b2c3d4e5f6a",
            "raw_marker": "[14]",
            "marker_type": "NUMERIC",
            "page_number": 3,
            "char_span": [504, 508],
            "reference_text": "14. Vaswani et al. Attention Is All You Need. NeurIPS 2017.",
            "reference_index": 14,
            "matched_paper_id": "fa1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d"
          }
        ],
        "verdict": "SUPPORTED",
        "verification_state": "VERIFIED",
        "confidence": 0.94,
        "rationale": "Vaswani et al. Section 5 demonstrates substantial training speedups compared to recurrent and convolutional baselines.",
        "evidence": [
          {
            "id": "bb112233-4455-6677-8899-aabbccddeeff",
            "paper_id": "fa1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
            "source_provider": "crossref",
            "doi": "10.48550/arXiv.1706.03762",
            "url": "https://arxiv.org/abs/1706.03762",
            "passage": "The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality after being trained for as little as twelve hours.",
            "evidence_level": "ABSTRACT_ONLY",
            "retrieval_status": "RETRIEVED",
            "similarity_score": 0.91,
            "section_name": "Abstract"
          }
        ],
        "needs_human_review": false,
        "review_reasons": [],
        "created_at": "2026-11-19T10:10:00Z",
        "updated_at": "2026-11-19T10:12:00Z"
      }
    ],
    "page": 1,
    "page_size": 20,
    "total": 1
  }
  ```

---

### 3.6. GET /api/documents/{document_id}/report
- **Purpose**: Retrieves the final synthesized verification report with aggregate statistics.
- **Parameters**: `document_id` (path, required).
- **Status Codes**:
  - `200 OK`: Report generated.
  - `404 Not Found`: Document not found.
  - `409 Conflict`: Analysis pipeline is not yet completed.
- **Example Response (`200 OK`)**:
  ```json
  {
    "document_id": "e4f8d9b2-3c1a-4d5e-9f8a-1b2c3d4e5f6a",
    "filename": "quantum_transformers_2026.pdf",
    "generated_at": "2026-11-19T10:15:30Z",
    "total_claims": 14,
    "reliability_score": 85.7,
    "verdict_counts": {
      "SUPPORTED": 10,
      "PARTLY_SUPPORTED": 2,
      "UNSUPPORTED": 1,
      "CONTRADICTORY": 0,
      "POTENTIALLY_OUTDATED": 0,
      "UNVERIFIED": 1
    },
    "evidence_level_counts": {
      "FULL_TEXT": 3,
      "ABSTRACT_ONLY": 9,
      "METADATA_ONLY": 1,
      "NONE": 1
    },
    "human_review_required_count": 2,
    "claims": []
  }
  ```

---

### 3.7. GET /api/claims/{claim_id}
- **Purpose**: Retrieves a single claim with full citations, matched publication metadata, evidence passages, and verification reasoning.
- **Parameters**: `claim_id` (path, required).
- **Status Codes**:
  - `200 OK`
  - `404 Not Found`
- **Example Response**: Returns single `Claim` object as described in 3.5.

---

### 3.8. POST /api/claims/{claim_id}/review
- **Purpose**: Records human expert feedback, updates the verdict/state, and logs an entry to verification audit history.
- **Parameters**: `claim_id` (path, required).
- **Request Body**:
  ```json
  {
    "reviewer_name": "Prof. Alan Grant",
    "updated_verdict": "PARTLY_SUPPORTED",
    "notes": "Verified against paper table 4; effect size is statistically significant but limited to English-German benchmark."
  }
  ```
- **Status Codes**:
  - `200 OK`: Claim updated.
  - `400 Bad Request`: Missing reviewer name or invalid verdict.
  - `404 Not Found`: Claim ID does not exist.

