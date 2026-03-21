"""Unit tests for Gemini call wrapper in chatbot module."""

import pytest

from src.api import chatbot


@pytest.mark.asyncio
async def test_call_gemini_without_api_key(monkeypatch):
    monkeypatch.setattr(chatbot, "GEMINI_API_KEY", "")

    result = await chatbot.call_gemini("hello")

    assert "not configured" in result


@pytest.mark.asyncio
async def test_call_gemini_success(monkeypatch):
    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {
                "candidates": [
                    {"content": {"parts": [{"text": "AI response"}]}}
                ]
            }

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

        async def post(self, url, headers, json, timeout):
            return FakeResponse()

    monkeypatch.setattr(chatbot, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(chatbot.httpx, "AsyncClient", lambda: FakeClient())

    result = await chatbot.call_gemini("hello")

    assert result == "AI response"


@pytest.mark.asyncio
async def test_call_gemini_no_candidates(monkeypatch):
    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

        async def post(self, url, headers, json, timeout):
            return FakeResponse()

    monkeypatch.setattr(chatbot, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(chatbot.httpx, "AsyncClient", lambda: FakeClient())

    result = await chatbot.call_gemini("hello")

    assert result == "No response generated"


@pytest.mark.asyncio
async def test_call_gemini_non_200_status(monkeypatch):
    class FakeResponse:
        status_code = 500

        @staticmethod
        def json():
            return {"error": "server"}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

        async def post(self, url, headers, json, timeout):
            return FakeResponse()

    monkeypatch.setattr(chatbot, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(chatbot.httpx, "AsyncClient", lambda: FakeClient())

    result = await chatbot.call_gemini("hello")

    assert result == "Error: API returned status 500"


@pytest.mark.asyncio
async def test_call_gemini_exception(monkeypatch):
    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

        async def post(self, url, headers, json, timeout):
            raise RuntimeError("network down")

    monkeypatch.setattr(chatbot, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(chatbot.httpx, "AsyncClient", lambda: FakeClient())

    result = await chatbot.call_gemini("hello")

    assert "Error calling Gemini API" in result
    assert "network down" in result
