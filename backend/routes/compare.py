"""
FastAPI Route for /api/compare.
"""

from fastapi import APIRouter, HTTPException
from data.schemas import ComparisonRequest
from backend.services.product_service import ProductService
from backend.services.comparison_service import ComparisonService

router = APIRouter(prefix="/api", tags=["Compare"])
product_service = ProductService()
comparison_service = ComparisonService()

@router.post("/compare")
def compare_products(payload: ComparisonRequest):
    """
    POST /api/compare
    Returns normalized products and marketplace comparison matrix.
    """
    try:
        all_grouped, _ = product_service.search_and_group(query="")
        selected = [p for p in all_grouped if p.product_id in payload.product_ids]
        
        matrix = comparison_service.build_comparison_matrix(selected)
        return {
            "success": True,
            "comparison": matrix.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
