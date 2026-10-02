"""
FastAPI Routes for CartIQ AI Shopping Assistant.
Provides:
- POST /api/ask  — RAG-grounded Q&A with product context
- POST /ask_ai   — General shopping advisor (no product context required),
                   used by the floating chat widget.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from data.schemas import AskRequest, GroupedProduct
from ai.rag import CartIQRAGEngine
from backend.services.product_service import ProductService

router = APIRouter(tags=["RAG Q&A"])
rag_engine = CartIQRAGEngine()
product_service = ProductService()


@router.post("/api/ask")
def ask_rag_question(payload: AskRequest, simulate_gemini_failure: bool = False):
    """
    POST /api/ask
    Runs RAG-based product Q&A through ProviderManager (Gemini -> Groq -> Rule Fallback).
    Uses product context if provided; otherwise uses general shopping advisor mode.
    """
    try:
        if payload.product_context:
            products = [GroupedProduct(**p) for p in payload.product_context]
        else:
            # General advisor mode — no live product fetch to avoid fabrication
            products = []

        res = rag_engine.ask_question(
            question=payload.query,
            products=products,
            simulate_gemini_failure=simulate_gemini_failure
        )
        return {
            "success": True,
            "answer": res.answer,
            "context_used_count": res.context_used_count,
            "provider_used": res.provider_used
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FloatingAskRequest(BaseModel):
    """Request schema for the floating chat widget endpoint."""
    question: str


@router.post("/ask_ai")
def ask_ai_floating(payload: FloatingAskRequest, simulate_gemini_failure: bool = False):
    """
    POST /ask_ai
    General shopping advisory endpoint for the floating CartIQ chat widget.
    Works without live product data. Never fabricates live marketplace prices,
    ratings, stock, or availability.
    """
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # General advisor mode: empty products list triggers GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT
        res = rag_engine.ask_question(
            question=payload.question.strip(),
            products=[],
            simulate_gemini_failure=simulate_gemini_failure
        )
        return {
            "success": True,
            "answer": res.answer,
            "provider_used": res.provider_used,
            "mode": "general_advisor"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
