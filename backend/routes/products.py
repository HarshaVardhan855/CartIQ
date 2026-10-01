"""
FastAPI Route for /api/products/{product_id}.
"""

from fastapi import APIRouter, HTTPException
from backend.services.product_service import ProductService

router = APIRouter(prefix="/api", tags=["Products"])
product_service = ProductService()

@router.get("/products/{product_id}")
def get_product_details(product_id: str):
    """
    GET /api/products/{product_id}
    Returns one product group and all available marketplace offers.
    """
    grouped_products, _ = product_service.search_and_group(query="")
    for p in grouped_products:
        if p.product_id == product_id:
            return {"success": True, "product": p.dict()}
    
    raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found.")
