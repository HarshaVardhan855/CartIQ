"""
Unit tests for Python Deterministic Price Comparison Engine in CartIQ.
"""

from data.schemas import ProductOffer
from backend.services.comparison_service import ComparisonService

def test_lowest_price_calculation():
    offers = [
        ProductOffer(product_id="1", name="boAt 141", price=999.0, marketplace="Amazon", product_url="http://amz", source_product_id="1"),
        ProductOffer(product_id="2", name="boAt 141", price=899.0, marketplace="Flipkart", product_url="http://fk", source_product_id="2"),
        ProductOffer(product_id="3", name="boAt 141", price=920.0, marketplace="Meesho", product_url="http://msh", source_product_id="3")
    ]

    metrics = ComparisonService.calculate_price_metrics(offers)

    assert metrics["lowest"] == 899.0
    assert metrics["highest"] == 999.0
    assert metrics["difference"] == 100.0
    assert metrics["lowest_marketplace"] == "Flipkart"
