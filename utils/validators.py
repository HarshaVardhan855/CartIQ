"""
Validation utilities for URLs, budget values, and queries in CartIQ.
"""

import re
from typing import Optional

def is_valid_url(url: Optional[str]) -> bool:
    """
    Validates if a URL is valid and non-empty.
    """
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(re.match(regex, url))

def sanitize_query(query: str) -> str:
    """
    Sanitizes raw search query strings.
    """
    if not query:
        return ""
    # Strip dangerous characters or excessive whitespace
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
