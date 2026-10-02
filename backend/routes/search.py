"""
FastAPI Route for /api/search.
"""

from fastapi import APIRouter, HTTPException
from data.schemas import SearchQuery
from backend.services.query_service import QueryService
from backend.services.product_service import ProductService

router = APIRouter(prefix="/api", tags=["Search"])
query_service = QueryService()
product_service = ProductService()

@router.post("/search")
def search_products(payload: SearchQuery, simulate_gemini_failure: bool = False):
    """
    POST /api/search
    1. Parses NL query into structured intent via ProviderManager (Gemini -> Groq -> Rule Fallback).
    2. Fetches offers, normalizes, performs 5-step matching, and filters budget in Python.
    3. Provides verified live data if configured or legitimate marketplace search links.
    """
    try:
        # Extract structured parameters
        extracted = query_service.parse_query(
            payload.query, simulate_gemini_failure=simulate_gemini_failure
        )
        
        # Override budget if payload provides explicit max_budget
        budget_to_use = payload.max_budget if payload.max_budget is not None else extracted.budget

        # Fetch and group products
        grouped_products, warnings = product_service.search_and_group(
            query=payload.query,
            category=extracted.category,
            max_budget=budget_to_use,
            marketplace_filter=payload.marketplace_filter,
            sort_by=payload.sort_by
        )

        # Generate real marketplace search links and retrieve source statuses
        search_links = product_service.get_marketplace_search_links(
            query=payload.query,
            category=extracted.category
        )
        source_statuses = product_service.get_source_statuses()

        return {
            "success": True,
            "query": payload.query,
            "extracted_intent": extracted.dict(),
            "provider_used": extracted.provider_used,
            "total_products": len(grouped_products),
            "products": [p.dict() for p in grouped_products],
            "marketplace_search_links": search_links,
            "source_status": source_statuses,
            "warnings": warnings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
