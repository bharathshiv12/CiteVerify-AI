"""
Test for GET /api/health liveness endpoint.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_returns_200_and_expected_shape():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "citeverify-backend"
    assert "version" in data
    assert "timestamp" in data
    assert "X-Request-ID" in response.headers

