"""
Abstract Base Source Adapter for CartIQ.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from data.schemas import ProductOffer

class BaseSourceAdapter(ABC):
    """
    Modular source-adapter interface.
    Each supported data source (API, feed, mock, adapter) must implement fetch_offers.
    """

    def __init__(self, marketplace_name: str):
        self.marketplace_name = marketplace_name

    @abstractmethod
    def fetch_offers(self, query: str, category: Optional[str] = None, max_budget: Optional[float] = None) -> List[ProductOffer]:
        """
        Retrieves product offers for a given search query.
        Must return normalized ProductOffer instances.
        Raises exception if source network/API fails.
        """
        pass
