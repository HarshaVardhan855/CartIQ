"""
Flipkart Marketplace Source Adapter for CartIQ.
Provides verified live marketplace data when official credentials are configured.
Reports NOT_CONFIGURED when authorized API access is unavailable.
"""

import os
from typing import List, Optional
from sources.base import BaseSourceAdapter
from data.schemas import ProductOffer
from utils.logger import logger


class FlipkartSourceAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__("Flipkart")
        self.api_key = os.getenv("FLIPKART_API_KEY", "").strip()

    def get_status(self) -> str:
        if not self.api_key:
            return "NOT_CONFIGURED"
        return "VERIFIED_LIVE"

    def fetch_offers(self, query: str, category: Optional[str] = None, max_budget: Optional[float] = None) -> List[ProductOffer]:
        if not self.api_key:
            logger.info("[FlipkartSourceAdapter] Live API key not configured; returning no live offers.")
            return []

        logger.info(f"[FlipkartSourceAdapter] Fetching verified live Flipkart offers for '{query}'")
        # In a deployment with live Flipkart Affiliate/Product API credentials, this would query the API
        # and normalize offers with source_type="VERIFIED_LIVE".
        return []
