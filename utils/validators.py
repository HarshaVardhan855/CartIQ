"""
Validation utilities for URLs, budget values, and queries in CartIQ.
Ensures CartIQ never propagates malformed, placeholder, or guessed product links.
"""

import re
import urllib.parse
from typing import Optional

# Known legitimate domains for primary marketplaces
MARKETPLACE_DOMAINS = {
    "amazon": ["amazon.in", "amazon.com", "amzn.to", "www.amazon.in", "www.amazon.com"],
    "flipkart": ["flipkart.com", "dl.flipkart.com", "www.flipkart.com", "fkrt.it"],
    "meesho": ["meesho.com", "www.meesho.com"]
}

REJECTED_HOSTS = {
    "localhost", "127.0.0.1", "0.0.0.0", "example.com", "www.example.com",
    "test.com", "dummy.com", "fake.com", "amz", "fk", "msh"
}

REJECTED_VALUES = {
    "unavailable", "product link unavailable", "none", "null", "n/a", "#",
    "http://amz", "http://fk", "http://msh", "https://amz", "https://fk", "https://msh"
}


def is_valid_url(url: Optional[str]) -> bool:
    """
    Validates if a URL is valid, uses http/https, has a valid domain, and is not a rejected placeholder.
    """
    if not url or not isinstance(url, str):
        return False

    url_str = url.strip()
    if not url_str or url_str.lower() in REJECTED_VALUES:
        return False

    try:
        parsed = urllib.parse.urlparse(url_str)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = (parsed.hostname or "").lower()
        if not hostname or hostname in REJECTED_HOSTS:
            return False

        # Hostname must have at least one dot (domain.tld)
        if "." not in hostname:
            return False

        return True
    except Exception:
        return False


def validate_product_url(url: Optional[str], expected_marketplace: Optional[str] = None) -> str:
    """
    Validates product URL strictly.
    If valid, returns the cleaned URL.
    If invalid, placeholder, or domain mismatch, returns 'Product link unavailable'.
    CartIQ NEVER fabricates or guesses a replacement product URL.
    """
    if not is_valid_url(url):
        return "Product link unavailable"

    url_str = url.strip()

    if expected_marketplace:
        m_key = expected_marketplace.lower()
        if m_key in MARKETPLACE_DOMAINS:
            try:
                parsed = urllib.parse.urlparse(url_str)
                hostname = (parsed.hostname or "").lower()
                valid_domains = MARKETPLACE_DOMAINS[m_key]
                # Check if hostname matches or ends with any valid domain
                matches = any(
                    hostname == dom or hostname.endswith("." + dom)
                    for dom in valid_domains
                )
                if not matches:
                    return "Product link unavailable"
            except Exception:
                return "Product link unavailable"

    return url_str


def sanitize_query(query: str) -> str:
    """
    Sanitizes raw search query strings.
    """
    if not query:
        return ""
    # Strip dangerous control characters or excessive whitespace
    query = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', query)
    return query.strip()


def validate_budget(budget: Optional[float]) -> Optional[float]:
    """
    Validates budget values to ensure non-negative numeric floats.
    """
    if budget is None:
        return None
    try:
        val = float(budget)
        return val if val >= 0 else None
    except (ValueError, TypeError):
        return None
