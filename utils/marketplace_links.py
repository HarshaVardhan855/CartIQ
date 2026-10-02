"""
Marketplace Search Link Generator for CartIQ.

Generates safe, legitimate search destinations for Amazon, Flipkart, and Meesho
based on user's cleaned search query.
CartIQ NEVER fabricates product IDs, ASINs, or individual product URLs.
"""

import os
import re
import urllib.parse
from typing import Dict, Any, Optional
from utils.logger import logger


def clean_marketplace_query(query: str, category: Optional[str] = None) -> str:
    """
    Deterministic query-cleaning function.
    Strips budget phrases, intent prefixes, and noise so marketplace search engines
    receive a clean, relevant product search term.

    Example:
        'I need running shoes under ₹2000 for men' -> 'running shoes for men'
        'wireless earbuds under 1000' -> 'wireless earbuds'
    """
    if not query:
        return category.strip() if category else ""

    text = query.strip()

    # 1. Remove common conversational search prefixes
    text = re.sub(
        r'(?i)\b(i\s+need|i\s+want|looking\s+for|search\s+for|find\s+me|show\s+me|get\s+me|suggest|recommend)\b',
        '',
        text
    )

    # 2. Remove price / budget expressions (e.g. 'under ₹2000', 'under 1000', 'below Rs. 500', 'budget 1500')
    text = re.sub(
        r'(?i)\b(under|below|less\s+than|upto|up\s+to|within|max|budget|around|approx)\s*(?:₹|rs\.?|inr)?\s*[\d,]+(?:\s*(?:rs|rupees|inr))?',
        '',
        text
    )
    # Remove standalone currency values (e.g. '₹1000', 'Rs 500', '1000 inr')
    text = re.sub(r'(?i)(?:₹|rs\.?|inr)\s*[\d,]+', '', text)
    text = re.sub(r'(?i)\b[\d,]+\s*(?:rs|rupees|inr)\b', '', text)

    # 3. Clean up multiple spaces and special punctuation
    text = re.sub(r'[^\w\s\-\+\&]', ' ', text)
    cleaned = " ".join(text.split()).strip()

    # Fallback if cleaning stripped everything
    if not cleaned:
        if category and category.strip():
            return category.strip()
        # Fallback to alphanumeric tokens of original query
        fallback = re.sub(r'[^\w\s]', ' ', query)
        return " ".join(fallback.split()).strip()

    return cleaned


def build_marketplace_search_links(query: str, category: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Constructs real, structured marketplace search destinations for Amazon, Flipkart, and Meesho.

    Returns:
    {
        "amazon": {
            "marketplace": "Amazon",
            "url": "https://www.amazon.in/s?k=...",
            "type": "search"
        },
        "flipkart": {
            "marketplace": "Flipkart",
            "url": "https://www.flipkart.com/search?q=...",
            "type": "search"
        },
        "meesho": {
            "marketplace": "Meesho",
            "url": "https://www.meesho.com/search?q=...",
            "type": "search"
        }
    }
    """
    cleaned_query = clean_marketplace_query(query, category)
    encoded_query = urllib.parse.quote_plus(cleaned_query)

    logger.info(f"[MarketplaceLinks] Cleaned query '{query}' -> '{cleaned_query}' (encoded: '{encoded_query}')")

    if not encoded_query:
        return {
            "amazon": {
                "marketplace": "Amazon",
                "url": "https://www.amazon.in",
                "type": "search",
                "query": ""
            },
            "flipkart": {
                "marketplace": "Flipkart",
                "url": "https://www.flipkart.com",
                "type": "search",
                "query": ""
            },
            "meesho": {
                "marketplace": "Meesho",
                "url": "https://www.meesho.com",
                "type": "search",
                "query": ""
            }
        }

    # 1. Amazon Search URL
    amazon_base = f"https://www.amazon.in/s?k={encoded_query}"
    amazon_tag = os.getenv("AMAZON_ASSOCIATE_TAG", "").strip()
    if amazon_tag:
        amazon_url = f"{amazon_base}&tag={urllib.parse.quote_plus(amazon_tag)}"
    else:
        amazon_url = amazon_base

    # 2. Flipkart Search URL
    flipkart_base = f"https://www.flipkart.com/search?q={encoded_query}"
    flipkart_affid = os.getenv("FLIPKART_AFFILIATE_ID", "").strip()
    if flipkart_affid:
        flipkart_url = f"{flipkart_base}&affid={urllib.parse.quote_plus(flipkart_affid)}"
    else:
        flipkart_url = flipkart_base

    # 3. Meesho Search URL
    meesho_url = f"https://www.meesho.com/search?q={encoded_query}"

    return {
        "amazon": {
            "marketplace": "Amazon",
            "url": amazon_url,
            "type": "search",
            "query": cleaned_query
        },
        "flipkart": {
            "marketplace": "Flipkart",
            "url": flipkart_url,
            "type": "search",
            "query": cleaned_query
        },
        "meesho": {
            "marketplace": "Meesho",
            "url": meesho_url,
            "type": "search",
            "query": cleaned_query
        }
    }
