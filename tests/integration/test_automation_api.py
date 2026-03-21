"""Integration tests for automation API endpoints."""

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_list_workflows():
    response = client.get("/api/v1/automation/workflows")

    assert response.status_code == 200
    assert response.json() == {"workflows": [], "count": 0}


def test_create_workflow():
    response = client.post(
        "/api/v1/automation/workflows",
        json={
            "name": "Daily Summary",
            "trigger": "cron",
            "actions": [{"type": "email", "target": "ops@example.com"}],
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["workflow_id"] == "wf-new-id"
    assert payload["name"] == "Daily Summary"
    assert payload["status"] == "active"


def test_create_workflow_validation_error():
    response = client.post("/api/v1/automation/workflows", json={"name": "Broken"})

    assert response.status_code == 422


def test_list_tasks():
    response = client.get("/api/v1/automation/tasks")

    assert response.status_code == 200
    assert response.json() == {"tasks": [], "count": 0}


def test_create_task():
    response = client.post(
        "/api/v1/automation/tasks",
        json={"title": "Follow-up leads", "description": "CRM sync", "priority": "high"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["task_id"] == "task-new-id"
    assert payload["title"] == "Follow-up leads"
    assert payload["status"] == "pending"


def test_execute_workflow():
    response = client.post("/api/v1/automation/execute/workflow-123")

    assert response.status_code == 200
    assert response.json() == {
        "workflow_id": "workflow-123",
        "status": "executed",
        "result": "success",
    }
