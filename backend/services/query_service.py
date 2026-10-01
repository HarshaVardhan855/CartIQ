"""
Query Understanding Service for CartIQ.
Uses ProviderManager (Gemini -> Groq -> Rule Fallback) to convert NL queries into structured requirements.
"""

from typing import Optional
from data.schemas import StructuredQueryExtraction
from ai.provider_manager import ProviderManager
from ai.prompts import QUERY_EXTRACTION_SYSTEM_PROMPT
from utils.logger import logger

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
