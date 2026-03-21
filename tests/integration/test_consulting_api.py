"""Integration tests for consulting API endpoints."""

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_list_services():
    response = client.get("/api/v1/consulting/services")
    payload = response.json()

    assert response.status_code == 200
    assert "services" in payload
    assert len(payload["services"]) == 4
    assert payload["services"][0]["id"] == "ai-readiness"


def test_request_consultation():
    response = client.post(
        "/api/v1/consulting/consultation",
        json={
            "name": "Alex Smith",
            "email": "alex@example.com",
            "company": "Example Inc",
            "service_type": "strategy",
            "message": "Need a quick AI roadmap",
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["request_id"] == "consult-new-id"
    assert payload["status"] == "submitted"


def test_request_consultation_validation_error():
    response = client.post(
        "/api/v1/consulting/consultation",
        json={"name": "Only Name"},
    )

    assert response.status_code == 422


def test_create_strategy():
    response = client.post(
        "/api/v1/consulting/strategy",
        json={
            "company_name": "Example Inc",
            "industry": "Retail",
            "current_tools": ["CRM"],
            "goals": ["Automate support"],
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["strategy_id"] == "strategy-new-id"
    assert payload["company"] == "Example Inc"
    assert isinstance(payload["recommendations"], list)
    assert payload["status"] == "generated"
