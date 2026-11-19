# CiteVerify AI — API Test Report

**Date:** 2026-11-20  
**Test Suite:** `scripts/test_all_endpoints.py` (FastAPI TestClient + Starlette HTTP)  
**Total Endpoints Tested:** 41 Test Scenarios Across 22 Distinct Routes  
**Result:** 41 Passed / 0 Failed (100% Pass Rate)  
**Base Contract Reference:** `contracts/openapi/openapi.yaml`  

---

## 1. Test Execution Matrix

| # | Endpoint & Method | Test Scenario Description | Expected Status | Actual Status | Auth Level | Multi-Tenant IDOR Guard | Result |
|---|-------------------|---------------------------|-----------------|---------------|------------|-------------------------|--------|
| 1 | `GET /api/health` | Basic system health check | 200 | 200 | Anonymous | N/A | **PASS** |
| 2 | `GET /api/health/ready` | K8s/Docker readiness probe | 200 | 200 | Anonymous | N/A | **PASS** |
| 3 | `GET /api/health/live` | K8s/Docker liveness probe | 200 | 200 | Anonymous | N/A | **PASS** |
| 4 | `GET /api/auth/me` | Unauthenticated token check | 401 | 401 | None | Enforced | **PASS** |
| 5 | `GET /api/auth/me` | Authenticated profile retrieval | 200 | 200 | User Token | Scoped to caller | **PASS** |
| 6 | `POST /api/auth/logout` | Session invalidation | 200 | 200 | User Token | Scoped to caller | **PASS** |
| 7 | `POST /api/auth/forgot-password` | Malformed email string ("invalid") | 400 | 400 | Anonymous | Email format validator | **PASS** |
| 8 | `POST /api/auth/forgot-password` | Valid academic email | 200 | 200 | Anonymous | Non-disclosing user existence | **PASS** |
| 9 | `POST /api/documents/upload` | Upload `text/plain` file | 400 | 400 | User Token | Extension & MIME check | **PASS** |
| 10 | `POST /api/documents/upload` | Upload 0-byte empty file | 400 | 400 | User Token | Minimum payload size check | **PASS** |
| 11 | `POST /api/documents/upload` | Fake `%PDF-` header (corrupted) | 400 | 400 | User Token | Deep parser structure check | **PASS** |
| 12 | `POST /api/documents/upload` | Valid PDF A upload | 201 | 201 | User Token | Multi-tenant user assignment | **PASS** |
| 13 | `GET /api/documents` | User A lists uploaded documents | 200 | 200 | User Token A | Returns User A documents | **PASS** |
| 14 | `GET /api/documents` | User B lists uploaded documents | 200 | 200 | User Token B | Returns [] (Zero data leakage) | **PASS** |
| 15 | `GET /api/documents/{id}` | User A reads own document | 200 | 200 | User Token A | Allowed | **PASS** |
| 16 | `GET /api/documents/{id}` | User B accesses User A document | 404 | 404 | User Token B | Non-disclosing 404 Not Found | **PASS** |
| 17 | `GET /api/documents/{id}` | Anonymous access attempt | 401 | 401 | None | Bearer token required | **PASS** |
| 18 | `POST /api/documents/{id}/analyze`| User A triggers analysis pipeline | 202 | 202 | User Token A | Background worker queue | **PASS** |
| 19 | `POST /api/documents/{id}/analyze`| User B attempts analyze on User A doc | 404 | 404 | User Token B | Non-disclosing 404 | **PASS** |
| 20 | `GET /api/documents/{id}/status` | User A polls processing progress | 200 | 200 | User Token A | Stage progress envelope | **PASS** |
| 21 | `GET /api/documents/{id}/status` | User B cross-user status poll | 404 | 404 | User Token B | Non-disclosing 404 | **PASS** |
| 22 | `GET /api/documents/{id}/claims` | User A fetches extracted claims | 200 | 200 | User Token A | Array of canonical claims | **PASS** |
| 23 | `GET /api/documents/{id}/claims` | User B cross-user claims fetch | 404 | 404 | User Token B | Non-disclosing 404 | **PASS** |
| 24 | `GET /api/documents/{id}/report` | User A fetches verification report | 200 | 200 | User Token A | Report summary & verdicts | **PASS** |
| 25 | `GET /api/documents/{id}/report` | User B cross-user report fetch | 404 | 404 | User Token B | Non-disclosing 404 | **PASS** |
| 26 | `GET /api/documents/{id}/report/pdf`| User A downloads PDF export | 200 | 200 | User Token A | Content-Type: application/pdf | **PASS** |
| 27 | `GET /api/documents/{id}/report/pdf`| User B cross-user PDF download | 404 | 404 | User Token B | Non-disclosing 404 | **PASS** |
| 28 | `GET /api/claims/{id}` | User A fetches specific claim detail | 200 | 200 | User Token A | Claim & evidence passages | **PASS** |
| 29 | `GET /api/claims/{id}` | User B cross-user claim detail fetch | 404 | 404 | User Token B | Non-disclosing 404 | **PASS** |
| 30 | `POST /api/claims/{id}/review` | User A submits reviewer override | 200 | 200 | User Token A | Audit trail preserved | **PASS** |
| 31 | `POST /api/claims/{id}/review` | User B cross-user review attempt | 404 | 404 | User Token B | Non-disclosing 404 | **PASS** |
| 32 | `PATCH /api/claims/{id}` | User A edits claim text & boundaries | 200 | 200 | User Token A | Boundary re-indexed | **PASS** |
| 33 | `PATCH /api/claims/{id}` | User B cross-user patch attempt | 404 | 404 | User Token B | Non-disclosing 404 | **PASS** |
| 34 | `GET /api/research/search` | Search literature via query term | 200 | 200 | User Token | Multi-engine aggregator | **PASS** |
| 35 | `GET /api/dashboard/stats` | User A fetches dashboard summary | 200 | 200 | User Token A | Multi-tenant scoped counts | **PASS** |
| 36 | `GET /api/dashboard/activity` | User A fetches recent events | 200 | 200 | User Token A | Multi-tenant scoped feed | **PASS** |
| 37 | `GET /api/settings` | Fetch user settings & preferences | 200 | 200 | User Token A | User scoped settings | **PASS** |
| 38 | `PUT /api/settings` | Update user settings & preferences | 200 | 200 | User Token A | Validated schema update | **PASS** |
| 39 | `DELETE /api/documents/{id}` | User B attempts delete on User A doc | 404 | 404 | User Token B | Forbidden/Non-disclosing 404 | **PASS** |
| 40 | `DELETE /api/documents/{id}` | User A deletes own document | 204 | 204 | User Token A | Cascading delete on claims | **PASS** |
| 41 | `GET /api/documents/{id}` | User A fetches deleted document | 404 | 404 | User Token A | Verified tombstone/removal | **PASS** |

---

## 2. API Contract & Schema Compliance

### 2.1 Standard Error Envelope
All error responses consistently adhere to the canonical schema:
```json
{
  "error": {
    "code": "INVALID_FILE",
    "message": "File does not contain valid PDF content",
    "details": {},
    "request_id": "req-9471f496"
  }
}
```

### 2.2 Security & Multi-Tenancy Architecture
- **Bearer Token Authentication:** Endpoints require `Authorization: Bearer <jwt>`. Unauthenticated requests immediately receive `401 Unauthorized`.
- **In-Depth IDOR Mitigation:** If User B attempts to access User A's document or claim, the API returns `404 Not Found` rather than `403 Forbidden`. This design choice prevents resource enumeration and attacker probing of document existence.
- **Cascading Deletion:** Deleting a document securely purges all attached claims, references, and generated reports.
