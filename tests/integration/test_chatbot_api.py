"""Integration tests for chatbot API endpoints."""

from fastapi.testclient import TestClient

from src.main import app
from src.api import chatbot


client = TestClient(app)


def test_chat_endpoint_uses_model_response(monkeypatch):
    async def fake_call_gemini(prompt: str) -> str:
        assert "sales" in prompt
        assert "Hello" in prompt
        return "Mocked response"

    monkeypatch.setattr(chatbot, "call_gemini", fake_call_gemini)

    response = client.post(
        "/api/v1/chatbot/chat",
        json={"message": "Hello", "context": "sales"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "response": "Mocked response",
        "context": "sales",
        "status": "success",
    }


def test_chat_endpoint_validation_error():
    response = client.post("/api/v1/chatbot/chat", json={"context": "general"})

    assert response.status_code == 422


def test_list_sessions():
    response = client.get("/api/v1/chatbot/sessions")

    assert response.status_code == 200
    assert response.json() == {"sessions": [], "count": 0}


def test_create_session():
    response = client.post("/api/v1/chatbot/sessions", params={"user_id": "user-1"})

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "new-session-id",
        "user_id": "user-1",
        "status": "active",
    }
