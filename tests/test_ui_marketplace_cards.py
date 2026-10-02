"""
Unit tests for Reference Marketplace Search Cards UI and Dropdown Filtering.
"""

from utils.marketplace_links import build_marketplace_search_links
from ui.components import render_marketplace_search_cards
import unittest.mock as mock


def test_marketplace_cards_all_selected():
    """
    Test 1: When 'All' is selected, exactly 3 cards (Amazon, Flipkart, Meesho) are displayed.
    """
    query = "wireless earbuds under 1000"
    links = build_marketplace_search_links(query)

    with mock.patch("streamlit.markdown") as mock_st_md:
        render_marketplace_search_cards(links, query, marketplace_filter="All")
        assert mock_st_md.called
        rendered_html = mock_st_md.call_args[0][0]

        # Heading check matching reference design
        assert "Search Results for" in rendered_html
        assert "wireless earbuds under 1000" in rendered_html

        # All 3 cards present
        assert "ref-market-card amazon" in rendered_html
        assert "ref-market-card flipkart" in rendered_html
        assert "ref-market-card meesho" in rendered_html

        # Live Link badge present
        assert "Live Link" in rendered_html
        assert "live-link-badge-pill" in rendered_html

        # Official Website indicators
        assert "Official Website" in rendered_html
        assert "official-badge-pill" in rendered_html

        # Highlight feature chips present
        assert "Latest Prices" in rendered_html
        assert "Latest Deals" in rendered_html
        assert "Best Prices" in rendered_html

        # Prominent CTA buttons
        assert "Search Amazon &rarr;" in rendered_html or "Search Amazon →" in rendered_html
        assert "Search Flipkart &rarr;" in rendered_html or "Search Flipkart →" in rendered_html
        assert "Search Meesho &rarr;" in rendered_html or "Search Meesho →" in rendered_html

        # Real links with query
        assert "amazon.in/s?k=" in rendered_html
        assert "flipkart.com/search?q=" in rendered_html
        assert "meesho.com/search?q=" in rendered_html

        # Smart search info box present
        assert "Smart Search" in rendered_html
        assert "Click on any platform above to open their website" in rendered_html

        # Old label "Live Data: Not Configured" completely removed
        assert "Live Data: Not Configured" not in rendered_html
        assert "Not Configured" not in rendered_html

        # No demo labels in the rendered marketplace card section
        assert "Demo Data" not in rendered_html
        assert "Demo Price" not in rendered_html
        assert "Lowest Demo Price" not in rendered_html
        assert "Demo Catalog" not in rendered_html


def test_marketplace_cards_amazon_selected():
    """
    Test 2: When 'Amazon' is selected, ONLY the Amazon card is displayed (exactly 1 card).
    """
    query = "running shoes under 2000"
    links = build_marketplace_search_links(query)

    with mock.patch("streamlit.markdown") as mock_st_md:
        render_marketplace_search_cards(links, query, marketplace_filter="Amazon")
        assert mock_st_md.called
        rendered_html = mock_st_md.call_args[0][0]

        # Amazon is displayed
        assert "ref-market-card amazon" in rendered_html
        assert "Search Amazon" in rendered_html
        assert "amazon.in/s?k=" in rendered_html

        # Flipkart and Meesho are NOT displayed
        assert "ref-market-card flipkart" not in rendered_html
        assert "ref-market-card meesho" not in rendered_html
        assert "Search Flipkart" not in rendered_html
        assert "Search Meesho" not in rendered_html


def test_marketplace_cards_flipkart_selected():
    """
    Test 3: When 'Flipkart' is selected, ONLY the Flipkart card is displayed (exactly 1 card).
    """
    query = "laptop"
    links = build_marketplace_search_links(query)

    with mock.patch("streamlit.markdown") as mock_st_md:
        render_marketplace_search_cards(links, query, marketplace_filter="Flipkart")
        assert mock_st_md.called
        rendered_html = mock_st_md.call_args[0][0]

        # Flipkart is displayed
        assert "ref-market-card flipkart" in rendered_html
        assert "Search Flipkart" in rendered_html
        assert "flipkart.com/search?q=" in rendered_html

        # Amazon and Meesho are NOT displayed
        assert "ref-market-card amazon" not in rendered_html
        assert "ref-market-card meesho" not in rendered_html
        assert "Search Amazon" not in rendered_html
        assert "Search Meesho" not in rendered_html


def test_marketplace_cards_meesho_selected():
    """
    Test 4: When 'Meesho' is selected, ONLY the Meesho card is displayed (exactly 1 card).
    """
    query = "kitchen items"
    links = build_marketplace_search_links(query)

    with mock.patch("streamlit.markdown") as mock_st_md:
        render_marketplace_search_cards(links, query, marketplace_filter="Meesho")
        assert mock_st_md.called
        rendered_html = mock_st_md.call_args[0][0]

        # Meesho is displayed
        assert "ref-market-card meesho" in rendered_html
        assert "Search Meesho" in rendered_html
        assert "meesho.com/search?q=" in rendered_html

        # Amazon and Flipkart are NOT displayed
        assert "ref-market-card amazon" not in rendered_html
        assert "ref-market-card flipkart" not in rendered_html
        assert "Search Amazon" not in rendered_html
        assert "Search Flipkart" not in rendered_html
