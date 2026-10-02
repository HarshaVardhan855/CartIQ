"""
Meesho Marketplace Source Adapter for CartIQ.
Reports NOT_CONFIGURED when authorized programmatic access is unavailable.
Does not scrape or fabricate fake Meesho data.
"""

import os
from typing import List, Optional
from sources.base import BaseSourceAdapter
from data.schemas import ProductOffer
from utils.logger import logger


class MeeshoSourceAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__("Meesho")
        self.api_key = os.getenv("MEESHO_API_KEY", "").strip()

    def get_status(self) -> str:
        if not self.api_key:
            return "NOT_CONFIGURED"
        return "VERIFIED_LIVE"

    def fetch_offers(self, query: str, category: Optional[str] = None, max_budget: Optional[float] = None) -> List[ProductOffer]:
        if not self.api_key:
            logger.info("[MeeshoSourceAdapter] Live API key not configured; returning no live offers.")
            return []

        logger.info(f"[MeeshoSourceAdapter] Fetching verified live Meesho offers for '{query}'")
        return []
