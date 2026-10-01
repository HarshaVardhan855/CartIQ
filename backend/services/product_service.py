"""
Product Data Service for CartIQ.
Orchestrates multi-source data collection, normalization, 5-step product matching, and budget filtering.
Handles single-source failures gracefully.
"""

from typing import List, Tuple, Optional
from sources.source_a import AmazonSourceAdapter
from sources.source_b import FlipkartSourceAdapter
from sources.source_c import MeeshoSourceAdapter
from sources.demo_source import DemoSourceAdapter
from data.schemas import ProductOffer, GroupedProduct
from data.product_matcher import ProductMatcher
from utils.logger import logger

class ProductService:
    def __init__(self):
        self.adapters = [
            AmazonSourceAdapter(),
            FlipkartSourceAdapter(),
            MeeshoSourceAdapter(),
            DemoSourceAdapter()
        ]
        self.matcher = ProductMatcher()

    def search_and_group(
        self,
        query: str,
        category: Optional[str] = None,
        max_budget: Optional[float] = None,
        marketplace_filter: Optional[str] = "All",
        sort_by: Optional[str] = "Lowest Price"
    ) -> Tuple[List[GroupedProduct], List[str]]:
        """
        Gathers offers from supported adapters, normalizes, groups offers into canonical products,
        and enforces budget filtering in Python.
        """
        all_raw_offers: List[ProductOffer] = []
        source_warnings: List[str] = []

        # 1. Fetch from source adapters with resilience
        for adapter in self.adapters:
            # Skip if specific marketplace filter requested
            if marketplace_filter and marketplace_filter != "All" and adapter.marketplace_name not in ["DemoAll", marketplace_filter]:
                continue

            try:
                offers = adapter.fetch_offers(query=query, category=category, max_budget=max_budget)
                all_raw_offers.extend(offers)
            except Exception as e:
                msg = f"{adapter.marketplace_name} data is temporarily unavailable."
                logger.error(f"[ProductService] {adapter.marketplace_name} source failure: {e}")
                source_warnings.append(msg)

        if not all_raw_offers:
            # Fallback to demo source if empty
            try:
                demo_adapter = DemoSourceAdapter()
                all_raw_offers = demo_adapter.fetch_offers(query=query, category=category, max_budget=max_budget)
            except Exception as e:
                logger.error(f"Fallback demo adapter error: {e}")

        # 2. Group offers into same product clusters (Explainable 5-step matching)
        grouped_products = self.matcher.group_offers(all_raw_offers)

        # 3. Enforce deterministic Budget Filtering in Python (Section 11, 38)
        if max_budget is not None and max_budget > 0:
            filtered_groups = []
            for gp in grouped_products:
                # Keep offers within budget
                valid_offers = [o for o in gp.offers if o.price <= max_budget]
                if valid_offers:
                    gp.offers = sorted(valid_offers, key=lambda o: o.price)
                    gp.lowest_price = gp.offers[0].price
                    gp.highest_price = gp.offers[-1].price
                    gp.price_difference = round(gp.highest_price - gp.lowest_price, 2)
                    gp.lowest_marketplace = gp.offers[0].marketplace
                    gp.available_offers_count = len(gp.offers)
                    filtered_groups.append(gp)
            grouped_products = filtered_groups

        # 4. Filter by specific marketplace if requested
        if marketplace_filter and marketplace_filter != "All":
            mf_groups = []
            for gp in grouped_products:
                mf_offers = [o for o in gp.offers if o.marketplace.lower() == marketplace_filter.lower()]
                if mf_offers:
                    gp.offers = mf_offers
                    gp.available_offers_count = len(mf_offers)
                    mf_groups.append(gp)
            grouped_products = mf_groups

        # 5. Deterministic Python Sorting
        if sort_by == "Lowest Price":
            grouped_products.sort(key=lambda g: g.lowest_price)
        elif sort_by == "Highest Rating":
            grouped_products.sort(key=lambda g: max([o.rating for o in g.offers], default=0), reverse=True)
        elif sort_by == "Highest Discount":
            grouped_products.sort(key=lambda g: max([o.discount for o in g.offers], default=0), reverse=True)

        return grouped_products, source_warnings
