"""
Unit tests for Data Normalizer in CartIQ.
"""

from data.normalizer import normalize_offer

def test_raw_field_normalization():
    # Source A style payload
    raw_a = {
        "title": "boAt Airdopes 141 TWS",
        "selling_price": "₹999",
        "mrp": "₹4,490",
        "brand": "boAt",
        "model": "141",
        "category": "wireless earbuds",
        "rating": 4.3,
        "review_count": 142000,
        "url": "https://www.amazon.in/dp/B097VD4LYG",
        "id": "amz_123"
    }
    
    offer_a = normalize_offer(raw_a, "Amazon")
    
    assert offer_a.name == "boAt Airdopes 141 TWS"
    assert offer_a.price == 999.0
    assert offer_a.original_price == 4490.0
    assert offer_a.marketplace == "Amazon"
    assert offer_a.product_url == "https://www.amazon.in/dp/B097VD4LYG"

    # Source B style payload with different keys
    raw_b = {
        "item_title": "boAt Airdopes 141 TWS",
        "offer_price": 899,
        "list_price": 4490,
        "brand": "boAt",
        "model": "141",
        "category": "wireless earbuds",
        "rating": 4.3,
        "product_url": "https://www.flipkart.com/p/itm123",
        "source_product_id": "fk_123"
    }

    offer_b = normalize_offer(raw_b, "Flipkart")

    assert offer_b.name == "boAt Airdopes 141 TWS"
    assert offer_b.price == 899.0
    assert offer_b.marketplace == "Flipkart"
    assert offer_b.product_url == "https://www.flipkart.com/p/itm123"
