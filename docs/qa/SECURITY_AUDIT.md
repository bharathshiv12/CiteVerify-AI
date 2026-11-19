# CiteVerify AI — Application Security Audit

**Date:** 2026-11-20  
**Auditor:** Senior Application Security Engineer  
**Standard:** OWASP Top 10 (2021), ASVS Level 2, CWE Guidelines  
**Scope:** Frontend (Next.js 14), Backend (FastAPI), Database/Auth (Supabase), External Scholarly APIs  

---

## 1. Executive Security Summary

CiteVerify AI exhibits a robust security architecture. Authentication leverages cryptographic JWT verification through Supabase GoTrue. Multi-tenant data isolation is protected by strict ownership checks returning non-disclosing 404 responses to eliminate IDOR enumeration. PDF uploads are guarded by a defense-in-depth pipeline (extension checking, magic-byte inspection, size capping, and structural parsing). Zero secrets are exposed in client-side bundles.

---

## 2. Threat Vector Evaluation

### 2.1 Broken Object Level Authorization (BOLA / IDOR) — PASS
* **Risk:** User B requests `/api/documents/{user_a_doc_id}` to view or alter another user's research paper.
* **Audit Finding:**
  - Tested across all resource routes: `GET`, `PATCH`, `DELETE` on `/api/documents/{id}`, `/api/documents/{id}/claims`, `/api/documents/{id}/report`, `/api/claims/{id}`, and `/api/claims/{id}/review`.
  - When User B presents a valid JWT for their own identity and requests User A's document, the backend verifies ownership against the document's `user_id`.
  - **Non-Disclosing Status Code:** The server returns `404 Not Found` rather than `403 Forbidden`. This completely prevents attackers from discovering valid document IDs or confirming whether a paper has been uploaded.

### 2.2 Broken Authentication & Token Handling — PASS
* **Risk:** Weak password policies, token tampering, token replay, credential leakage.
* **Audit Finding:**
  - Passwords require minimum 8 characters, uppercase, lowercase, numbers, and symbols.
  - Supabase Auth handles password hashing using industry-standard bcrypt/Argon2.
  - JWTs are validated cryptographically against both the configured HMAC secret and the remote JWKS public key endpoint.
  - Expired tokens and tampered signatures are rejected immediately with 401 Unauthorized.
  - No guest mode or authentication bypasses exist; all unauthenticated API requests are blocked.

### 2.3 Malicious PDF & File Upload Attacks — PASS
* **Risk:** Uploading executables masquerading as PDFs, corrupted files triggering buffer overflows in PyMuPDF, or decompression bombs.
* **Audit Finding:**
  - **Level 1 (Extension):** Rejects any file without a `.pdf` extension.
  - **Level 2 (MIME Type):** Enforces `application/pdf` Content-Type header.
  - **Level 3 (Magic Bytes):** Checks the first 1024 bytes of the binary stream for the `%PDF-` signature.
  - **Level 4 (Size Cap):** Rejects payloads exceeding 30MB with HTTP 413 Payload Too Large.
  - **Level 5 (Structural Parsing):** Files containing fake `%PDF-` headers without valid PDF xref/trailer objects are caught by PyMuPDF exception handlers and cleanly rejected with HTTP 400 (`File does not contain valid PDF content`).

### 2.4 Injection Vulnerabilities (SQL / NoSQL / Command) — PASS
* **Risk:** Malicious claim text, metadata, or search parameters executing arbitrary commands or SQL.
* **Audit Finding:**
  - Backend uses parameterized queries in Supabase client and typed Pydantic models.
  - External search queries to Crossref, OpenAlex, and Europe PMC are URL-encoded (`urllib.parse.quote_plus`).
  - Python `subprocess` is never invoked with user-supplied arguments; PDF extraction is performed via memory buffers using C-bindings in PyMuPDF.

### 2.5 Cross-Site Scripting (XSS) & Content Injection — PASS
* **Risk:** Malicious JavaScript injected via research paper title, abstract, or extracted claim rendered into the DOM.
* **Audit Finding:**
  - Next.js / React automatically escapes interpolated JSX values (`{claim.claim_text}`).
  - No `dangerouslySetInnerHTML` is used in user-facing components.
  - PDF generation uses a sandboxed canvas renderer and sanitizes text strings before drawing.

### 2.6 Cross-Origin Resource Sharing (CORS) — PASS
* **Risk:** Permissive wildcard CORS (`*`) allowing malicious third-party origins to read academic reports.
* **Audit Finding:**
  - `backend/app/core/config.py` defines `BACKEND_CORS_ORIGINS`.
  - Default configuration restricts origins to `http://localhost:3000` and configured production frontend domains.
  - Credentials (`allow_credentials=True`) are enabled only for whitelisted origins.

### 2.7 Secrets & Configuration Management — PASS
* **Risk:** Leaking API keys, service role keys, or database credentials.
* **Audit Finding:**
  - Automated scanner in `scripts/validate_repo.py` verified that no `.env` or `.env.local` files are tracked in git.
  - Frontend client bundle only imports `NEXT_PUBLIC_` prefixed variables (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`).
  - Secret keys (`SUPABASE_SECRET_KEY`, `SUPABASE_JWT_SECRET`) are never loaded or referenced in frontend code.

---

## 3. Security Recommendations for Production Hardening

1. **Rate Limiting Middleware:** Implement token-bucket rate limiting (e.g., `slowapi` or Redis) on `/api/documents/upload` (e.g., 5 uploads/min per user) to mitigate denial-of-wallet and compute exhaustion.
2. **Virus / Malware Scanning:** For high-volume multi-institutional deployments, integrate ClamAV scanning on uploaded byte streams prior to PyMuPDF parsing.
3. **Content Security Policy (CSP):** Add explicit CSP headers in `next.config.mjs` restricting script sources to `'self'`.
