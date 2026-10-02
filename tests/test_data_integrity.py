"""
Unit tests for Data Integrity, URL Validation, and Source Status Distinction in CartIQ.
"""

from data.normalizer import normalize_offer
from utils.validators import validate_product_url, is_valid_url
from backend.services.product_service import ProductService
from sources.demo_source import DemoSourceAdapter
from sources.source_a import AmazonSourceAdapter


def test_invalid_product_url_becomes_unavailable():
    """
    Test 4: A malformed/invalid or placeholder source URL must become 'Product link unavailable'
    and never a guessed or fabricated product URL.
    """
    # 1. Obvious placeholder
    raw_invalid1 = {
        "title": "Roadster Casual Shirt",
        "price": 799,
        "url": "unavailable"
    }
    offer1 = normalize_offer(raw_invalid1, "Amazon")
    assert offer1.product_url == "Product link unavailable"

    # 2. Localhost or dummy domain
    raw_invalid2 = {
        "title": "Puma Running Shoes",
        "price": 1499,
        "url": "http://localhost:8000/product/123"
    }
    offer2 = normalize_offer(raw_invalid2, "Flipkart")
    assert offer2.product_url == "Product link unavailable"

    # 3. Malformed string
    assert validate_product_url("not_a_url") == "Product link unavailable"
    assert validate_product_url("") == "Product link unavailable"
    assert validate_product_url(None) == "Product link unavailable"
    assert validate_product_url("http://amz") == "Product link unavailable"

    # 4. Valid marketplace URL is preserved
    valid_amz = "https://www.amazon.in/dp/B097VD4LYG"
    assert validate_product_url(valid_amz, expected_marketplace="Amazon") == valid_amz


def test_demo_and_live_distinction():
    """
    Test 5: Demo offers must have a source state indicating demo data,
    while live adapters report NOT_CONFIGURED when no live credentials exist.
    """
    demo_adapter = DemoSourceAdapter()
    assert demo_adapter.get_status() == "DEMO"
    
    offers = demo_adapter.fetch_offers("earbuds")
    assert len(offers) > 0
    for offer in offers:
        assert offer.source_type == "DEMO"

    amz_adapter = AmazonSourceAdapter()
    assert amz_adapter.get_status() in ["NOT_CONFIGURED", "VERIFIED_LIVE"]


def test_budget_filtering_on_grouped_products():
    """
    Test 6: Budget filtering continues working strictly in Python for retrieved offers.
    """
    service = ProductService()
    grouped, _ = service.search_and_group("shoes", max_budget=1500.0)

    for gp in grouped:
        assert gp.lowest_price <= 1500.0
        for offer in gp.offers:
            assert offer.price <= 1500.0


def test_source_statuses_and_search_links_in_service():
    """
    Test 7: ProductService exposes source statuses and marketplace search destinations.
    """
    service = ProductService()
    statuses = service.get_source_statuses()
    
    assert "amazon" in statuses
    assert "flipkart" in statuses
    assert "meesho" in statuses
    
    links = service.get_marketplace_search_links("kitchen items")
    assert "kitchen" in links["amazon"]["url"]
    assert "kitchen" in links["flipkart"]["url"]
    assert "kitchen" in links["meesho"]["url"]
