"""
Flipkart Marketplace Source Adapter for CartIQ.
Uses category-agnostic token search via demo_source._find_matching_indices.
"""

from typing import List, Optional
from sources.base import BaseSourceAdapter
from sources.demo_source import RAW_DEMO_PRODUCTS, _find_matching_indices
from data.schemas import ProductOffer
from data.normalizer import normalize_offer
from utils.logger import logger


class FlipkartSourceAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__("Flipkart")

    def fetch_offers(self, query: str, category: Optional[str] = None, max_budget: Optional[float] = None) -> List[ProductOffer]:
        logger.info(f"Fetching Flipkart offers for '{query}'")
        matched_indices = _find_matching_indices(query or "", category or "")
        offers = []
        seen = set()
        for idx in matched_indices:
            item = RAW_DEMO_PRODUCTS[idx]
            if item.get("marketplace") == "Flipkart":
                sid = item.get("source_product_id", "")
                if sid not in seen:
                    seen.add(sid)
                    offers.append(normalize_offer(item, "Flipkart"))
        return offers
