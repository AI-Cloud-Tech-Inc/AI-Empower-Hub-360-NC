"""AI Consulting API endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/consulting", tags=["consulting"])


class ConsultationRequest(BaseModel):
    name: str
    email: str
    company: str
    service_type: str
    message: str = ""


class StrategyRequest(BaseModel):
    company_name: str
    industry: str
    current_tools: list = []
    goals: list = []


@router.get("/services")
async def list_services():
    """List available consulting services."""
    return {
        "services": [
            {"id": "ai-readiness", "name": "AI Readiness Assessment", "price": 500},
            {"id": "strategy", "name": "AI Strategy Development", "price": 1500},
            {"id": "implementation", "name": "Implementation Planning", "price": 2000},
            {"id": "training", "name": "Staff Training Workshop", "price": 800}
        ]
    }


@router.post("/consultation")
async def request_consultation(request: ConsultationRequest):
    """Request a consultation."""
    return {
        "request_id": "consult-new-id",
        "status": "submitted",
        "message": "We'll contact you within 24 hours"
    }


@router.post("/strategy")
async def create_strategy(request: StrategyRequest):
    """Generate AI strategy recommendations."""
    return {
        "strategy_id": "strategy-new-id",
        "company": request.company_name,
        "recommendations": [
            "Start with chatbot implementation for customer service",
            "Automate repetitive tasks with workflow tools",
            "Consider cloud AI deployment for scalability"
        ],
        "status": "generated"
    }