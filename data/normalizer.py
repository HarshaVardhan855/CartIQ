"""
Data Normalization module for CartIQ.
Converts heterogeneous marketplace raw dictionaries into validated ProductOffer schema.
Ensures deterministic URL validation and clear distinction between verified and demo data.
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime
from data.schemas import ProductOffer
from utils.validators import validate_product_url

def clean_price(val: Any) -> float:
    """
    Parses and cleans price inputs into float values.
    Handles inputs like '₹999', 'Rs. 1,200', 999.0, etc.
    """
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return max(0.0, float(val))
    
    # Strip currency symbols and commas
    cleaned_str = re.sub(r'[^\d.]', '', str(val))
    try:
        return float(cleaned_str) if cleaned_str else 0.0
    except ValueError:
        return 0.0

def normalize_offer(raw_data: Dict[str, Any], marketplace: str, source_type: Optional[str] = None) -> ProductOffer:
    """
    Normalizes a raw dictionary from any marketplace source into a standardized ProductOffer.
    """
    # 1. Title/Name mapping
    name = (
        raw_data.get("name") or
        raw_data.get("title") or
        raw_data.get("product_name") or
        raw_data.get("item_title") or
        "Unknown Product"
    ).strip()

    # 2. Price mapping (selling_price, current_price, offer_price -> price)
    price_val = (
        raw_data.get("price") if raw_data.get("price") is not None else
        raw_data.get("selling_price") if raw_data.get("selling_price") is not None else
        raw_data.get("current_price") if raw_data.get("current_price") is not None else
        raw_data.get("offer_price") if raw_data.get("offer_price") is not None else
        0.0
    )
    price = clean_price(price_val)

    # 3. Original price & discount calculation
    orig_price_val = raw_data.get("original_price") or raw_data.get("mrp") or raw_data.get("list_price")
    original_price = clean_price(orig_price_val) if orig_price_val else None

    discount = raw_data.get("discount", 0.0)
    if original_price and original_price > price:
        calculated_discount = round(((original_price - price) / original_price) * 100, 1)
        discount = calculated_discount

    # 4. Brand & Model extraction / fallback
    brand = (raw_data.get("brand") or "Generic").strip()
    model = (raw_data.get("model") or "").strip()

    # 5. Category
    category = (raw_data.get("category") or "General").strip()

    # 6. Ratings & Reviews
    rating = float(raw_data.get("rating", 0.0))
    review_count = int(raw_data.get("review_count", 0))

    # 7. Features list normalization
    features = raw_data.get("features", [])
    if isinstance(features, str):
        features = [f.strip() for f in features.split(",") if f.strip()]
    elif not isinstance(features, list):
        features = []

    # 8. Strict Product URL validation (No guessing, no fake URLs)
    raw_url = raw_data.get("product_url") or raw_data.get("url") or ""
    product_url = validate_product_url(str(raw_url), expected_marketplace=marketplace)

    # 9. Product ID & Source ID
    source_pid = str(raw_data.get("source_product_id") or raw_data.get("id") or name[:10])
    product_id = raw_data.get("product_id") or f"prod_{marketplace.lower()}_{source_pid}"

    image_url = raw_data.get("image_url")
    availability = bool(raw_data.get("availability", True))
    last_updated = raw_data.get("last_updated") or datetime.now().strftime("%d %b %Y, %I:%M %p")
    
    # 10. Source Type (VERIFIED_LIVE vs DEMO)
    resolved_source_type = source_type or raw_data.get("source_type", "DEMO")

    return ProductOffer(
        product_id=product_id,
        name=name,
        brand=brand,
        model=model,
        category=category,
        price=price,
        original_price=original_price,
        currency=raw_data.get("currency", "INR"),
        discount=discount,
        rating=rating,
        review_count=review_count,
        features=features,
        availability=availability,
        marketplace=marketplace,
        product_url=product_url,
        image_url=image_url,
        source_product_id=source_pid,
        source_type=resolved_source_type,
        last_updated=last_updated
    )
