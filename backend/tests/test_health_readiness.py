"""
Tests for health endpoints and database readiness probes.
"""
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.database.repository import get_repository


@pytest.fixture
def client():
    return TestClient(app)


def test_health_basic(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "repository_backend" in data


def test_health_live(client):
    r = client.get("/api/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "live"


def test_health_ready_memory(client, monkeypatch):
    monkeypatch.setattr(settings, "REPOSITORY_BACKEND", "memory")
    r = client.get("/api/health/ready")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ready"
    assert data["database"] == "ready"


def test_health_ready_supabase_connected(client, monkeypatch):
    monkeypatch.setattr(settings, "REPOSITORY_BACKEND", "supabase")
    mock_repo = AsyncMock()
    mock_repo.check_connection.return_value = (True, "Connected and schema verified")
    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        r = client.get("/api/health/ready")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ready"
        assert data["database"] == "ready"
        assert data["backend"] == "supabase"
    finally:
        app.dependency_overrides.pop(get_repository, None)


def test_health_ready_supabase_disconnected(client, monkeypatch):
    monkeypatch.setattr(settings, "REPOSITORY_BACKEND", "supabase")
    mock_repo = AsyncMock()
    mock_repo.check_connection.return_value = (False, "Table public.documents not found in schema cache")
    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        r = client.get("/api/health/ready")
        assert r.status_code == 503
        data = r.json()
        assert data["status"] == "not_ready"
        assert data["database"] == "disconnected"
        assert "Table public.documents not found" in data["error"]
    finally:
        app.dependency_overrides.pop(get_repository, None)
