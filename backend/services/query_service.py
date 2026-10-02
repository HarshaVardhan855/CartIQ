"""
Query Understanding Service for CartIQ.
Uses ProviderManager (Gemini -> Groq -> Rule Fallback) to convert NL queries into structured requirements.
"""

import re
from typing import Optional
from data.schemas import StructuredQueryExtraction
from ai.provider_manager import ProviderManager
from ai.prompts import QUERY_EXTRACTION_SYSTEM_PROMPT
from utils.logger import logger


def extract_budget_from_query(query: str) -> Optional[float]:
    """
    Extracts numerical budget from natural language query string.
    Handles phrasing like: 'under ₹500', 'below 1000', 'less than 2000', 'within ₹5000'.
    Returns None if no explicit budget is specified.
    """
    if not query:
        return None

    q = query.lower()
    pattern = r'(?:under|below|less than|within|budget|rs\.?|₹)\s*([\d,]+)'
    match = re.search(pattern, q)
    if match:
        try:
            return float(match.group(1).replace(",", ""))
        except (ValueError, TypeError):
            pass

    return None


def map_budget_to_preset(budget: Optional[float]) -> str:
    """
    Maps detected numerical budget to Streamlit UI radio preset options:
    - None -> 'Any'
    - <= 500 -> 'Under ₹500'
    - 1000 -> 'Under ₹1,000'
    - 2000 -> 'Under ₹2,000'
    - 5000 -> 'Under ₹5,000'
    - Other non-matching numbers -> 'Custom'
    """
    if budget is None:
        return "Any"
    b = float(budget)
    if b <= 500.0:
        return "Under ₹500"
    elif b == 1000.0:
        return "Under ₹1,000"
    elif b == 2000.0:
        return "Under ₹2,000"
    elif b == 5000.0:
        return "Under ₹5,000"
    else:
        return "Custom"

class QueryService:
    def __init__(self, provider_manager: Optional[ProviderManager] = None):
        self.provider_manager = provider_manager or ProviderManager()

    def parse_query(self, user_query: str, simulate_gemini_failure: bool = False) -> StructuredQueryExtraction:
        """
        Extracts category, budget, currency, and requirements from natural language prompt.
        """
        logger.info(f"[QueryService] Parsing NL query: '{user_query}'")
        prompt = f"Extract structured search parameters for user prompt: '{user_query}'"

        parsed_json, provider_used = self.provider_manager.generate_json(
            prompt=prompt,
            system_prompt=QUERY_EXTRACTION_SYSTEM_PROMPT,
            simulate_gemini_failure=simulate_gemini_failure
        )

        category = str(parsed_json.get("category", "")).lower()
        budget = parsed_json.get("budget")
        if budget is not None:
            try:
                budget = float(budget)
            except (ValueError, TypeError):
                budget = None

        currency = str(parsed_json.get("currency", "INR"))
        reqs = parsed_json.get("requirements", [])
        if not isinstance(reqs, list):
            reqs = []

        return StructuredQueryExtraction(
            category=category,
            budget=budget,
            currency=currency,
            requirements=reqs,
            provider_used=provider_used
        )
