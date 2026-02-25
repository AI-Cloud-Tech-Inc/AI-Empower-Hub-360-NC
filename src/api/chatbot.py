"""Chatbot API endpoints."""
import os
import httpx
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

# Get API key from environment
GEMINI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"


class ChatRequest(BaseModel):
    message: str
    context: str = "general"


async def call_gemini(prompt: str) -> str:
    """Call Gemini API to generate a response."""
    if not GEMINI_API_KEY:
        return "Error: Gemini API key not configured. Please set GOOGLE_GENAI_API_KEY in .env file."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, timeout=30.0)
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                return "No response generated"
            else:
                return f"Error: API returned status {response.status_code}"
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"


@router.post("/chat")
async def chat(request: ChatRequest):
    """AI chatbot endpoint for virtual assistants."""
    # Build prompt with context
    prompt = f"You are an AI assistant for Empower Hub 360 NC, a company that provides AI solutions for businesses. Context: {request.context}. User message: {request.message}"
    
    # Get response from Gemini
    response = await call_gemini(prompt)
    
    return {
        "response": response,
        "context": request.context,
        "status": "success"
    }


@router.get("/sessions")
async def list_sessions():
    """List active chatbot sessions."""
    return {"sessions": [], "count": 0}


@router.post("/sessions")
async def create_session(user_id: str):
    """Create a new chatbot session."""
    return {
        "session_id": "new-session-id",
        "user_id": user_id,
        "status": "active"
    }