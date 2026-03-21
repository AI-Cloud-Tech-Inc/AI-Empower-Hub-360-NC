"""Integration tests for application-level routes."""

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_root_serves_html():
    """Root path should serve the website index file."""
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_api_root_returns_metadata():
    """API root should return app metadata and status."""
    response = client.get("/api")
    payload = response.json()

    assert response.status_code == 200
    assert payload["name"] == "AI Empower Hub 360"
    assert payload["api_version"] == "v1"
    assert payload["status"] == "running"


def test_health_returns_healthy():
    """Health check endpoint should always return healthy status."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_unknown_path_falls_back_to_index():
    """Unknown non-file paths should resolve to the SPA index fallback."""
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
