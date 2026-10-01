"""
Comparison Service for CartIQ.
Performs deterministic Python mathematical price calculations and comparative analysis.
"""

from typing import List
from data.schemas import GroupedProduct, ComparisonResult

class ComparisonService:

    @staticmethod
    def calculate_price_metrics(offers: list) -> dict:
        """
        Pure Python deterministic numerical comparison rules.
        """
        if not offers:
            return {"lowest": 0.0, "highest": 0.0, "difference": 0.0, "lowest_marketplace": ""}

        lowest_offer = min(offers, key=lambda o: o.price)
        highest_offer = max(offers, key=lambda o: o.price)
        diff = round(highest_offer.price - lowest_offer.price, 2)

        return {
            "lowest": lowest_offer.price,
            "highest": highest_offer.price,
            "difference": diff,
            "lowest_marketplace": lowest_offer.marketplace
        }

    def build_comparison_matrix(self, products: List[GroupedProduct]) -> ComparisonResult:
        """
        Builds factual comparison breakdown matrix across selected product groups.
        """
        if not products:
            return ComparisonResult(products=[], summary="No products selected for comparison.")

        cheapest_prod = min(products, key=lambda p: p.lowest_price) if products else None
        
        # Calculate highest rated product
        highest_rated = max(
            products,
            key=lambda p: max([o.rating for o in p.offers], default=0)
        ) if products else None

        # Build factual summary
        summary_lines = []
        for p in products:
            metrics = self.calculate_price_metrics(p.offers)
            summary_lines.append(
                f"- **{p.canonical_name}**: Lowest price ₹{metrics['lowest']} on {metrics['lowest_marketplace']} "
                f"(Saved ₹{metrics['difference']} vs highest offer)."
            )

        summary_text = "\n".join(summary_lines)

        return ComparisonResult(
            products=products,
            cheapest_product_id=cheapest_prod.product_id if cheapest_prod else None,
            highest_rated_product_id=highest_rated.product_id if highest_rated else None,
            summary=summary_text
        )
