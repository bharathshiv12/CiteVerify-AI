"""
Pytest configuration for CiteVerify backend tests.
Ensures unit tests run hermetically with isolated test environment.
"""
import pytest
from app.core.config import settings


@pytest.fixture(autouse=True)
def configure_test_environment(monkeypatch):
    """
    Sets ENVIRONMENT to testing for all pytest runs.
    """
    monkeypatch.setattr(settings, "ENVIRONMENT", "testing")
