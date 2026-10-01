"""
Unit tests for Explainable 5-step Product Matcher in CartIQ.
"""

from data.schemas import ProductOffer
from data.product_matcher import ProductMatcher

def test_identical_model_grouping():
    matcher = ProductMatcher()

    offer_amz = ProductOffer(
        product_id="p1",
        name="boAt Airdopes 141 Bluetooth TWS Earbuds",
        brand="boAt",
        model="141",
        category="wireless earbuds",
        price=999.0,
        marketplace="Amazon",
        product_url="https://www.amazon.in/dp/B097VD4LYG",
        source_product_id="amz_141"
    )

    offer_fk = ProductOffer(
        product_id="p2",
        name="boAt Airdopes 141 True Wireless Earbuds",
        brand="boAt",
        model="141",
        category="wireless earbuds",
        price=899.0,
        marketplace="Flipkart",
        product_url="https://www.flipkart.com/p/itm141",
        source_product_id="fk_141"
    )

    is_match, score, reason = matcher.are_same_product(offer_amz, offer_fk)
    assert is_match is True
    assert score >= 0.8

    # Test grouping into single GroupedProduct
    grouped = matcher.group_offers([offer_amz, offer_fk])
    assert len(grouped) == 1
    assert grouped[0].available_offers_count == 2
    assert grouped[0].lowest_price == 899.0
    assert grouped[0].lowest_marketplace == "Flipkart"
