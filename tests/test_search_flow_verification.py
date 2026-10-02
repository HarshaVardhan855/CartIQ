"""
End-to-end verification tests for Section 21 specified search queries in CartIQ:
- clothes under ₹1000
- running shoes under ₹2000
- kitchen items
- books
- laptop
- earbuds
- water bottle
- face wash
"""

import urllib.parse
from backend.services.query_service import QueryService
from backend.services.product_service import ProductService
from utils.marketplace_links import build_marketplace_search_links


TEST_QUERIES = [
    ("clothes under ₹1000", 1000.0, "clothes"),
    ("running shoes under ₹2000", 2000.0, "running shoes"),
    ("kitchen items", None, "kitchen"),
    ("books", None, "books"),
    ("laptop", None, "laptop"),
    ("earbuds", None, "earbuds"),
    ("water bottle", None, "water bottle"),
    ("face wash", None, "face wash"),
]


def test_section_21_search_suite():
    query_service = QueryService()
    product_service = ProductService()

    for query, expected_budget, expected_term in TEST_QUERIES:
        # 1. CartIQ parses query intent
        extracted = query_service.parse_query(query, simulate_gemini_failure=True)
        budget = extracted.budget if extracted.budget is not None else expected_budget

        # 2. Product service search and grouping
        grouped, warnings = product_service.search_and_group(
            query=query,
            category=extracted.category,
            max_budget=budget
        )

        # 3. Real marketplace search links
        links = product_service.get_marketplace_search_links(query, extracted.category)
        
        # Verify Amazon, Flipkart, Meesho search destinations
        assert "amazon" in links
        assert "flipkart" in links
        assert "meesho" in links

        # Verify links use legitimate marketplace search destinations with the actual query
        assert "https://www.amazon.in/s?k=" in links["amazon"]["url"]
        assert "https://www.flipkart.com/search?q=" in links["flipkart"]["url"]
        assert "https://www.meesho.com/search?q=" in links["meesho"]["url"]

        # Verify no fake product IDs or ASINs in search URLs
        for m_key in ["amazon", "flipkart", "meesho"]:
            assert "/dp/" not in links[m_key]["url"]
            assert "/itm" not in links[m_key]["url"]

        # 4. If demo products returned, verify they are marked DEMO and within budget
        if grouped:
            for gp in grouped:
                assert gp.source_type in ["DEMO", "VERIFIED_LIVE"]
                if budget is not None and budget > 0:
                    assert gp.lowest_price <= budget
                for offer in gp.offers:
                    assert offer.source_type in ["DEMO", "VERIFIED_LIVE"]
                    if budget is not None and budget > 0:
                        assert offer.price <= budget
