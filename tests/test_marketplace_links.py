"""
Unit tests for Real Marketplace Search Link Generation and Query Cleaning in CartIQ.
"""

from utils.marketplace_links import build_marketplace_search_links, clean_marketplace_query

def test_search_links_exist_for_query():
    """
    Test 1: Search links exist for a query and cover Amazon, Flipkart, and Meesho.
    """
    links = build_marketplace_search_links("wireless earbuds")
    
    assert "amazon" in links
    assert "flipkart" in links
    assert "meesho" in links
    
    assert "amazon.in" in links["amazon"]["url"]
    assert "flipkart.com" in links["flipkart"]["url"]
    assert "meesho.com" in links["meesho"]["url"]
    
    assert links["amazon"]["type"] == "search"
    assert links["flipkart"]["type"] == "search"
    assert links["meesho"]["type"] == "search"


def test_user_query_is_represented_and_not_hardcoded():
    """
    Test 2: Ensure generated search destinations correspond to the actual query.
    """
    query1 = "running shoes"
    links1 = build_marketplace_search_links(query1)
    
    assert "running+shoes" in links1["amazon"]["url"] or "running%20shoes" in links1["amazon"]["url"]
    assert "running+shoes" in links1["flipkart"]["url"] or "running%20shoes" in links1["flipkart"]["url"]
    assert "running+shoes" in links1["meesho"]["url"] or "running%20shoes" in links1["meesho"]["url"]
    
    query2 = "python programming book"
    links2 = build_marketplace_search_links(query2)
    assert "python" in links2["amazon"]["url"]
    assert "programming" in links2["amazon"]["url"]
    assert "running" not in links2["amazon"]["url"]


def test_no_fake_product_urls_or_asins():
    """
    Test 3: Verify that the marketplace-link layer generates only search destinations
    and does NOT fabricate individual product URLs, fake ASINs, or fake product slugs.
    """
    links = build_marketplace_search_links("water bottle")
    
    for key, link_obj in links.items():
        url = link_obj["url"]
        # Must be a search URL or marketplace domain, not a specific product detail page (/dp/ or /p/)
        assert "/dp/" not in url
        assert "/itm" not in url
        assert "fake" not in url.lower()
        assert "dummy" not in url.lower()
        assert link_obj["type"] == "search"


def test_query_cleaning_removes_budget_and_intent_noise():
    """
    Test query cleaning removes conversational prefixes and budget constraints.
    """
    # 1. Budget stripping
    cleaned1 = clean_marketplace_query("I need running shoes under ₹2000 for men")
    assert "2000" not in cleaned1
    assert "under" not in cleaned1.lower()
    assert "running shoes" in cleaned1
    assert "men" in cleaned1

    # 2. Standalone budget stripping
    cleaned2 = clean_marketplace_query("laptop under 50000")
    assert cleaned2 == "laptop"

    # 3. Simple category
    cleaned3 = clean_marketplace_query("clothes under ₹1000")
    assert cleaned3 == "clothes"
