"""
Unit tests for Search Query Parsing and Budget Filtering in CartIQ.
"""

from backend.services.query_service import QueryService
from backend.services.product_service import ProductService

def test_query_parsing():
    query_service = QueryService()
    res = query_service.parse_query("laptop under ₹50000")
    
    assert res.budget == 50000.0 or res.budget == 50000
    assert "laptop" in res.category.lower()

def test_price_filtering():
    product_service = ProductService()
    
    # Search with strict budget of ₹1000
    grouped, _ = product_service.search_and_group("earbuds", max_budget=1000.0)
    
    # All returned products and offers must be <= 1000
    for g in grouped:
        assert g.lowest_price <= 1000.0
        for offer in g.offers:
            assert offer.price <= 1000.0
