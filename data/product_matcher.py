"""
Explainable 5-step Staged Product Matching and Offer Grouping Engine for CartIQ.

Same Product -> Multiple Marketplace Offers.
"""

import re
from typing import List, Tuple
from difflib import SequenceMatcher
from data.schemas import ProductOffer, GroupedProduct

def normalize_text(text: str) -> str:
    """Helper to convert string to lower case alphanumeric tokens."""
    if not text:
        return ""
    return re.sub(r'[^a-z0-9\s]', '', text.lower()).strip()

def extract_model_sku(name: str, model_hint: str = "") -> str:
    """
    Extracts model/SKU alphanumeric patterns e.g. '141', 'VS102', 'Nord Buds 2', 'M10'.
    """
    if model_hint and len(model_hint) > 1:
        return normalize_text(model_hint)
    
    # Common model code patterns in electronics/products (e.g., numbers, numbers+letters)
    tokens = re.findall(r'\b[A-Za-z]*\d+[A-Za-z0-9]*\b|\b[A-Z]{2,}\d+\b', name)
    if tokens:
        return normalize_text(" ".join(tokens))
    return ""

class ProductMatcher:
    """
    Explainable 5-step Staged Product Matching Engine.
    """

    @staticmethod
    def step1_brand_match(brand1: str, brand2: str, name1: str, name2: str) -> bool:
        """Step 1 — Brand matching."""
        b1 = normalize_text(brand1)
        b2 = normalize_text(brand2)
        if b1 and b2 and (b1 == b2 or b1 in b2 or b2 in b1):
            return True
        
        # Fallback: check if brand is present in full product name
        n1 = normalize_text(name1)
        n2 = normalize_text(name2)
        if b1 and b1 in n2:
            return True
        if b2 and b2 in n1:
            return True
        return False

    @staticmethod
    def step2_model_sku_match(model1: str, model2: str, name1: str, name2: str) -> float:
        """Step 2 — Model/SKU matching."""
        m1 = extract_model_sku(name1, model1)
        m2 = extract_model_sku(name2, model2)
        
        if m1 and m2 and m1 == m2:
            return 1.0
        if m1 and m2 and (m1 in m2 or m2 in m1):
            return 0.8
        return 0.0

    @staticmethod
    def step3_name_similarity(name1: str, name2: str) -> float:
        """Step 3 — Normalized product-name similarity."""
        n1 = normalize_text(name1)
        n2 = normalize_text(name2)
        if not n1 or not n2:
            return 0.0
        
        # Jaccard Token Similarity
        tokens1 = set(n1.split())
        tokens2 = set(n2.split())
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # SequenceMatcher similarity
        seq_ratio = SequenceMatcher(None, n1, n2).ratio()
        
        return max(jaccard, seq_ratio)

    @staticmethod
    def step4_specification_match(features1: List[str], features2: List[str]) -> float:
        """Step 4 — Important specification matching."""
        if not features1 or not features2:
            return 0.5  # Neutral score if specs missing
        
        set1 = {normalize_text(f) for f in features1 if f}
        set2 = {normalize_text(f) for f in features2 if f}
        
        common = set1.intersection(set2)
        return len(common) / max(len(set1), len(set2)) if set1 and set2 else 0.5

    @staticmethod
    def step5_embedding_similarity(offer1: ProductOffer, offer2: ProductOffer) -> float:
        """Step 5 — Optional embedding/semantic similarity score."""
        # Lightweight token overlap score as fast embedding proxy
        n1 = normalize_text(f"{offer1.name} {offer1.category}")
        n2 = normalize_text(f"{offer2.name} {offer2.category}")
        tokens1 = set(n1.split())
        tokens2 = set(n2.split())
        return len(tokens1.intersection(tokens2)) / len(tokens1.union(tokens2)) if tokens1 and tokens2 else 0.0

    def are_same_product(self, offer1: ProductOffer, offer2: ProductOffer) -> Tuple[bool, float, str]:
        """
        Runs the 5-step matching process.
        Returns (is_match, confidence_score, matching_reason).
        """
        # Step 1: Brand check
        brand_match = self.step1_brand_match(offer1.brand, offer2.brand, offer1.name, offer2.name)
        if not brand_match:
            return False, 0.0, "Brand mismatch"

        # Step 2: Model/SKU check
        model_score = self.step2_model_sku_match(offer1.model, offer2.model, offer1.name, offer2.name)
        if model_score >= 0.8:
            return True, 0.95, f"Step 2: Model SKU matched ({offer1.model or offer2.model})"

        # Step 3: Name similarity
        name_sim = self.step3_name_similarity(offer1.name, offer2.name)
        
        # Step 4: Spec match
        spec_sim = self.step4_specification_match(offer1.features, offer2.features)
        
        # Step 5: Semantic embedding similarity
        embed_sim = self.step5_embedding_similarity(offer1, offer2)

        composite_score = (name_sim * 0.5) + (spec_sim * 0.3) + (embed_sim * 0.2)

        if name_sim >= 0.65 or composite_score >= 0.60:
            return True, round(composite_score, 2), f"Step 3/4/5: Similarity score {round(composite_score, 2)}"

        return False, round(composite_score, 2), "Below match threshold"

    def group_offers(self, offers: List[ProductOffer]) -> List[GroupedProduct]:
        """
        Groups a list of marketplace offers into canonical GroupedProduct instances.
        Determines lowest price, highest price, price difference, best offer marketplace in Python.
        """
        if not offers:
            return []

        clusters: List[List[ProductOffer]] = []

        for offer in offers:
            placed = False
            for cluster in clusters:
                # Compare offer with first item in cluster (representative)
                is_match, score, reason = self.are_same_product(offer, cluster[0])
                if is_match:
                    cluster.append(offer)
                    placed = True
                    break
            if not placed:
                clusters.append([offer])

        grouped_products: List[GroupedProduct] = []

        for idx, cluster in enumerate(clusters):
            # Sort offers by price ascending (deterministic comparison engine rule)
            sorted_offers = sorted(cluster, key=lambda o: o.price)
            lowest_offer = sorted_offers[0]

            prices = [o.price for o in cluster]
            lowest_price = min(prices)
            highest_price = max(prices)
            price_diff = round(highest_price - lowest_price, 2)

            # Representative canonical info
            rep = lowest_offer
            canonical_name = rep.name
            
            # Canonical product ID
            group_id = f"grp_{idx+1}_{re.sub(r'[^a-zA-Z0-9]', '', rep.brand.lower())}"

            # Merge unique features across offers
            merged_features: List[str] = []
            for o in cluster:
                for f in o.features:
                    if f and f not in merged_features:
                        merged_features.append(f)

            grouped = GroupedProduct(
                product_id=group_id,
                canonical_name=canonical_name,
                brand=rep.brand,
                model=rep.model,
                category=rep.category,
                features=merged_features,
                image_url=rep.image_url,
                offers=sorted_offers,
                lowest_price=lowest_price,
                highest_price=highest_price,
                price_difference=price_diff,
                lowest_marketplace=lowest_offer.marketplace,
                available_offers_count=len(sorted_offers)
            )
            grouped_products.append(grouped)

        # Sort grouped products by lowest price ascending
        return sorted(grouped_products, key=lambda g: g.lowest_price)
