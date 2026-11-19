"""
Integration tests for document routes: upload, list, get, extract, delete.
"""
import io
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.main import app
from app.core.security import create_test_jwt


def create_dynamic_pdf(pages_text: list) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    for text in pages_text:
        c.drawString(100, 700, text)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


@pytest.fixture
def client():
    return TestClient(app)


def test_document_lifecycle(client):
    user_id = uuid4()
    token = create_test_jwt(user_id=user_id, email="author@research.org")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Upload valid PDF
    pdf_bytes = create_dynamic_pdf(["Page 1: Deep learning models achieve state of the art results [1]."])
    files = {"file": ("paper.pdf", pdf_bytes, "application/pdf")}
    resp = client.post("/api/documents/upload", files=files, headers=headers)
    assert resp.status_code == 201
    doc_data = resp.json()
    doc_id = doc_data["id"]
    assert doc_data["filename"] == "paper.pdf"
    assert doc_data["status"] == "PENDING"
    assert doc_data["pipeline_stage"] == "UPLOADED"

    # 2. List documents (user-scoped)
    list_resp = client.get("/api/documents", headers=headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    assert any(d["id"] == doc_id for d in list_data["items"])

    # 3. Get document details
    get_resp = client.get(f"/api/documents/{doc_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == doc_id

    # 4. Extract document text
    extract_resp = client.post(f"/api/documents/{doc_id}/extract", headers=headers)
    assert extract_resp.status_code == 200
    ext_data = extract_resp.json()
    assert ext_data["page_count"] == 1
    assert ext_data["is_scanned"] is False
    assert len(ext_data["pages"]) == 1
    assert "state of the art" in ext_data["pages"][0]["text"]

    # 5. Delete document
    del_resp = client.delete(f"/api/documents/{doc_id}", headers=headers)
    assert del_resp.status_code == 204

    # Verify document is gone
    get_after_del = client.get(f"/api/documents/{doc_id}", headers=headers)
    assert get_after_del.status_code == 404
