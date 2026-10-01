"""
FastAPI Route for /api/ask.
"""

from fastapi import APIRouter, HTTPException
from data.schemas import AskRequest, GroupedProduct
from ai.rag import CartIQRAGEngine
from backend.services.product_service import ProductService

router = APIRouter(prefix="/api", tags=["RAG Q&A"])
rag_engine = CartIQRAGEngine()
product_service = ProductService()

@router.post("/ask")
def ask_rag_question(payload: AskRequest, simulate_gemini_failure: bool = False):
    """
    POST /api/ask
    Runs RAG-based product Q&A through ProviderManager (Gemini -> Groq -> Rule Fallback).
    """
    try:
        if payload.product_context:
            products = [GroupedProduct(**p) for p in payload.product_context]
        else:
            products, _ = product_service.search_and_group(query=payload.query)

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
