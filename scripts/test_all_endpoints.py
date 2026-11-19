import sys
import os
import io
import time
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("backend"))

from app.core.config import settings
settings.ENVIRONMENT = "testing"

from app.main import app
from app.core.security import create_test_jwt
from app.database.repository import get_repository
from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.enums import ProcessingStatus, PipelineStage, VerificationVerdict

client = TestClient(app)

results = []

def record(endpoint, scenario, expected_status, actual_status, passed, notes=""):
    results.append({
        "endpoint": endpoint,
        "scenario": scenario,
        "expected": expected_status,
        "actual": actual_status,
        "passed": passed,
        "notes": notes
    })
    status_str = "PASS" if passed else "FAIL"
    print(f"[{status_str}] {endpoint} - {scenario} -> Exp: {expected_status}, Got: {actual_status} {notes}")

def test_endpoints():
    user_a = uuid4()
    user_b = uuid4()
    token_a = create_test_jwt(user_id=user_a, email="user_a@academic.edu")
    token_b = create_test_jwt(user_id=user_b, email="user_b@academic.edu")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Health Endpoints
    r = client.get("/api/health")
    record("/api/health", "GET basic health", 200, r.status_code, r.status_code == 200)

    r = client.get("/api/health/ready")
    record("/api/health/ready", "GET readiness", 200, r.status_code, r.status_code == 200)

    r = client.get("/api/health/live")
    record("/api/health/live", "GET liveness", 200, r.status_code, r.status_code == 200)

    # 2. Auth Endpoints
    r = client.get("/api/auth/me")
    record("/api/auth/me", "Unauthenticated request", 401, r.status_code, r.status_code == 401)

    r = client.get("/api/auth/me", headers=headers_a)
    record("/api/auth/me", "Authenticated request", 200, r.status_code, r.status_code == 200)

    r = client.post("/api/auth/logout", headers=headers_a)
    record("/api/auth/logout", "Authenticated logout", 200, r.status_code, r.status_code == 200)

    r = client.post("/api/auth/forgot-password", json={"email": "invalid"})
    record("/api/auth/forgot-password", "Invalid email format", 422, r.status_code, r.status_code in [400, 422])

    r = client.post("/api/auth/forgot-password", json={"email": "valid@university.edu"})
    record("/api/auth/forgot-password", "Valid email submission", 200, r.status_code, r.status_code == 200)

    # 3. Document Endpoints
    # Upload invalid file (not PDF)
    txt_file = io.BytesIO(b"Hello plain text")
    r = client.post("/api/documents/upload", files={"file": ("test.txt", txt_file, "text/plain")}, headers=headers_a)
    record("/api/documents/upload", "Upload non-PDF text/plain", 400, r.status_code, r.status_code == 400, r.text[:60])

    # Upload empty PDF
    empty_pdf = io.BytesIO(b"")
    r = client.post("/api/documents/upload", files={"file": ("empty.pdf", empty_pdf, "application/pdf")}, headers=headers_a)
    record("/api/documents/upload", "Upload 0-byte file", 400, r.status_code, r.status_code == 400, r.text[:60])

    # Upload fake PDF (wrong magic bytes)
    fake_pdf = io.BytesIO(b"GIF89aNotARealPDFHeader")
    r = client.post("/api/documents/upload", files={"file": ("fake.pdf", fake_pdf, "application/pdf")}, headers=headers_a)
    record("/api/documents/upload", "Upload fake PDF header", 400, r.status_code, r.status_code == 400, r.text[:60])

    # Upload valid PDF
    pdf_bytes = Path("tests/fixtures/pdf_a_simple.pdf").read_bytes()
    r = client.post("/api/documents/upload", files={"file": ("pdf_a.pdf", io.BytesIO(pdf_bytes), "application/pdf")}, headers=headers_a)
    record("/api/documents/upload", "Upload valid PDF A", 201, r.status_code, r.status_code == 201)
    doc_a = r.json()
    doc_a_id = doc_a["id"]

    # List documents
    r = client.get("/api/documents", headers=headers_a)
    record("/api/documents", "List User A documents", 200, r.status_code, r.status_code == 200 and r.json()["total"] >= 1)

    r = client.get("/api/documents", headers=headers_b)
    record("/api/documents", "List User B documents (isolation)", 200, r.status_code, r.status_code == 200 and r.json()["total"] == 0)

    # Get document by ID
    r = client.get(f"/api/documents/{doc_a_id}", headers=headers_a)
    record(f"/api/documents/{{id}}", "Get own document", 200, r.status_code, r.status_code == 200)

    # Cross-user IDOR access attempt
    r = client.get(f"/api/documents/{doc_a_id}", headers=headers_b)
    record(f"/api/documents/{{id}}", "Cross-user IDOR attempt User B on User A doc", 404, r.status_code, r.status_code == 404)

    # Unauthenticated access attempt
    r = client.get(f"/api/documents/{doc_a_id}")
    record(f"/api/documents/{{id}}", "Unauthenticated document access", 401, r.status_code, r.status_code == 401)

    # Analyze document
    r = client.post(f"/api/documents/{doc_a_id}/analyze", headers=headers_a)
    record(f"/api/documents/{{id}}/analyze", "Analyze document User A", 202, r.status_code, r.status_code == 202)

    # Cross-user analyze attempt
    r = client.post(f"/api/documents/{doc_a_id}/analyze", headers=headers_b)
    record(f"/api/documents/{{id}}/analyze", "Cross-user analyze attempt User B on User A doc", 404, r.status_code, r.status_code == 404)

    # Get document status
    r = client.get(f"/api/documents/{doc_a_id}/status", headers=headers_a)
    record(f"/api/documents/{{id}}/status", "Get document status", 200, r.status_code, r.status_code == 200)

    # Cross-user status attempt
    r = client.get(f"/api/documents/{doc_a_id}/status", headers=headers_b)
    record(f"/api/documents/{{id}}/status", "Cross-user status attempt", 404, r.status_code, r.status_code == 404)

    # Wait for background pipeline to complete
    for _ in range(20):
        st = client.get(f"/api/documents/{doc_a_id}/status", headers=headers_a).json()
        if st.get("status") in ["COMPLETED", "FAILED"]:
            break
        time.sleep(0.2)

    # Get document claims
    r = client.get(f"/api/documents/{doc_a_id}/claims", headers=headers_a)
    record(f"/api/documents/{{id}}/claims", "Get document claims", 200, r.status_code, r.status_code == 200)
    claims_data = r.json()
    claims = claims_data.get("items", [])

    # Cross-user claims attempt
    r = client.get(f"/api/documents/{doc_a_id}/claims", headers=headers_b)
    record(f"/api/documents/{{id}}/claims", "Cross-user claims attempt", 404, r.status_code, r.status_code == 404)

    # Get report
    r = client.get(f"/api/documents/{doc_a_id}/report", headers=headers_a)
    record(f"/api/documents/{{id}}/report", "Get verification report", 200, r.status_code, r.status_code == 200)

    # Cross-user report attempt
    r = client.get(f"/api/documents/{doc_a_id}/report", headers=headers_b)
    record(f"/api/documents/{{id}}/report", "Cross-user report attempt", 404, r.status_code, r.status_code == 404)

    # Export report PDF
    r = client.get(f"/api/documents/{doc_a_id}/report/pdf", headers=headers_a)
    record(f"/api/documents/{{id}}/report/pdf", "Export report PDF stream", 200, r.status_code, r.status_code == 200 and r.headers.get("content-type") == "application/pdf")

    # Cross-user export PDF attempt
    r = client.get(f"/api/documents/{doc_a_id}/report/pdf", headers=headers_b)
    record(f"/api/documents/{{id}}/report/pdf", "Cross-user export PDF attempt", 404, r.status_code, r.status_code == 404)

    # Claims individual endpoints
    if claims:
        claim_id = claims[0]["id"]
        r = client.get(f"/api/claims/{claim_id}", headers=headers_a)
        record("/api/claims/{id}", "Get claim details", 200, r.status_code, r.status_code == 200)

        # Cross-user get claim attempt
        r = client.get(f"/api/claims/{claim_id}", headers=headers_b)
        record("/api/claims/{id}", "Cross-user claim attempt", 404, r.status_code, r.status_code == 404)

        # Review claim
        review_payload = {
            "reviewer_name": "Dr. Reviewer",
            "updated_verdict": "SUPPORTED",
            "notes": "Expert confirmation of BLEU score against WMT 2014 benchmark."
        }
        r = client.post(f"/api/claims/{claim_id}/review", json=review_payload, headers=headers_a)
        record("/api/claims/{id}/review", "Submit human review", 200, r.status_code, r.status_code == 200, r.text[:60] if r.status_code != 200 else "")

        # Cross-user review claim attempt
        r = client.post(f"/api/claims/{claim_id}/review", json=review_payload, headers=headers_b)
        record("/api/claims/{id}/review", "Cross-user review claim attempt", 404, r.status_code, r.status_code == 404)

        # Patch claim
        patch_payload = {
            "claim_text": "Refined claim text asserting empirical transformer translation results.",
            "char_span": [10, 85]
        }
        r = client.patch(f"/api/claims/{claim_id}", json=patch_payload, headers=headers_a)
        record("/api/claims/{id}", "Patch claim text & span", 200, r.status_code, r.status_code == 200, r.text[:60] if r.status_code != 200 else "")

        # Cross-user patch claim attempt
        r = client.patch(f"/api/claims/{claim_id}", json=patch_payload, headers=headers_b)
        record("/api/claims/{id}", "Cross-user patch claim attempt", 404, r.status_code, r.status_code == 404)

    # Research search & paper lookup
    r = client.get("/api/research/search?query=transformer+attention")
    record("/api/research/search", "Search literature query", 200, r.status_code, r.status_code == 200)

    # Dashboard endpoints
    r = client.get("/api/dashboard/stats", headers=headers_a)
    record("/api/dashboard/stats", "Get User A dashboard stats", 200, r.status_code, r.status_code == 200)

    r = client.get("/api/dashboard/activity", headers=headers_a)
    record("/api/dashboard/activity", "Get User A dashboard activity", 200, r.status_code, r.status_code == 200)

    # Settings endpoints
    r = client.get("/api/settings", headers=headers_a)
    record("/api/settings", "GET user settings", 200, r.status_code, r.status_code == 200)

    put_settings = {
        "email_notifications": True,
        "default_confidence_threshold": 0.85,
        "theme": "dark",
        "institution": "MIT CSAIL"
    }
    r = client.put("/api/settings", json=put_settings, headers=headers_a)
    record("/api/settings", "PUT user settings", 200, r.status_code, r.status_code == 200)

    # Delete document
    r = client.delete(f"/api/documents/{doc_a_id}", headers=headers_b)
    record(f"/api/documents/{{id}}", "Cross-user delete attempt (must fail)", 404, r.status_code, r.status_code == 404)

    r = client.delete(f"/api/documents/{doc_a_id}", headers=headers_a)
    record(f"/api/documents/{{id}}", "Delete own document", 204, r.status_code, r.status_code == 204)

    # Confirm deleted
    r = client.get(f"/api/documents/{doc_a_id}", headers=headers_a)
    record(f"/api/documents/{{id}}", "Get deleted document (must 404)", 404, r.status_code, r.status_code == 404)

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"\n=======================================================")
    print(f"API Endpoints Test Completed: {passed}/{total} Passed")
    print(f"=======================================================")

if __name__ == "__main__":
    test_endpoints()
