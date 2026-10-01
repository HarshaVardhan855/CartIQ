"""
Demo Data Source for CartIQ.
Category-agnostic controlled catalog for development, testing, and demonstration.
Covers Electronics, Fashion, Books, Home & Kitchen, Stationery, Beauty, Toys, Daily Needs.
"""

from typing import List, Dict, Any, Optional
from sources.base import BaseSourceAdapter
from data.schemas import ProductOffer
from data.normalizer import normalize_offer
from utils.logger import logger

# ---------------------------------------------------------------------------
# Category keyword synonyms for fuzzy matching
# Maps canonical category tags to search terms that should resolve to them.
# ---------------------------------------------------------------------------
CATEGORY_SYNONYMS: Dict[str, List[str]] = {
    "wireless earbuds": ["earbuds", "tws", "earbud", "earphone", "airpods", "wireless earphone"],
    "headphones": ["headphone", "over ear", "on ear", "headset", "wired headphone"],
    "laptop": ["laptop", "notebook", "computer"],
    "smartwatch": ["smartwatch", "smart watch", "fitness band", "wearable", "watch"],
    "smartphone": ["phone", "mobile", "smartphone", "android", "iphone"],
    "bluetooth speaker": ["speaker", "bluetooth speaker", "portable speaker", "wireless speaker"],
    "power bank": ["power bank", "powerbank", "charger bank"],
    "keyboard": ["keyboard", "mechanical keyboard"],
    "shirt": ["shirt", "shirts", "t-shirt", "tshirt", "tee", "top", "clothes", "clothing", "men shirt", "womens top"],
    "jeans": ["jeans", "denim", "pants", "trousers", "clothes", "clothing"],
    "dress": ["dress", "frock", "gown", "clothes", "clothing", "women dress"],
    "shoes": ["shoes", "sneakers", "footwear", "running shoes", "sports shoes", "casual shoes"],
    "sandals": ["sandals", "slippers", "flip flops", "footwear", "chappal"],
    "bag": ["bag", "backpack", "handbag", "tote", "sling bag", "office bag"],
    "watch": ["watch", "wristwatch", "fashion watch", "analog watch"],
    "fiction book": ["book", "books", "novel", "fiction", "story", "harry potter", "thriller"],
    "programming book": ["book", "books", "programming", "python", "coding", "tech book", "computer book"],
    "self help book": ["book", "books", "self help", "self-help", "motivation", "productivity"],
    "academic book": ["book", "books", "textbook", "academic", "competitive exam", "ncert", "school book"],
    "kitchen container": ["kitchen", "container", "storage box", "lunch box", "food storage", "kitchen items", "tiffin"],
    "cookware": ["cookware", "pan", "vessel", "kadai", "frying pan", "kitchen items", "utensils"],
    "pressure cooker": ["pressure cooker", "cooker", "kitchen items", "kitchen"],
    "water bottle": ["water bottle", "bottle", "sipper", "flask", "daily needs", "household"],
    "bedsheet": ["bedsheet", "bed sheet", "bed cover", "linen", "home", "home decor"],
    "notebook": ["notebook", "diary", "notepad", "stationery"],
    "pen": ["pen", "ball pen", "gel pen", "stationery", "writing"],
    "face wash": ["face wash", "facewash", "cleanser", "beauty", "skincare", "skin care"],
    "shampoo": ["shampoo", "hair wash", "hair care", "beauty", "personal care"],
    "moisturizer": ["moisturizer", "cream", "lotion", "beauty", "skincare"],
    "building blocks": ["toys", "toy", "blocks", "lego", "building blocks", "kids"],
    "board game": ["board game", "game", "toys", "puzzle", "chess", "kids"],
    "household cleaner": ["cleaner", "cleaning", "household", "daily needs", "cleaning products", "detergent"],
    "storage organizer": ["organizer", "storage", "household", "daily needs", "rack", "shelf"],
}

RAW_DEMO_PRODUCTS: List[Dict[str, Any]] = [
    # =========================================================================
    # ELECTRONICS — EARBUDS
    # =========================================================================
    {
        "name": "boAt Airdopes 141 Bluetooth TWS Earbuds",
        "brand": "boAt", "model": "141", "category": "wireless earbuds",
        "selling_price": 999, "mrp": 4490, "rating": 4.3, "review_count": 142000,
        "features": ["42H Playtime", "Low Latency Beast Mode", "ENx Tech", "IPX4 Water Resistance", "Fast Charge"],
        "marketplace": "Amazon",
        "product_url": "https://www.amazon.in/dp/B097VD4LYG",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_boat_141"
    },
    {
        "name": "boAt Airdopes 141 True Wireless Earbuds",
        "brand": "boAt", "model": "141", "category": "wireless earbuds",
        "offer_price": 899, "list_price": 4490, "rating": 4.3, "review_count": 198000,
        "features": ["42 Hours Battery", "IWP Tech", "8mm Drivers", "Type-C Charging"],
        "marketplace": "Flipkart",
        "product_url": "https://www.flipkart.com/boat-airdopes-141-bluetooth-headset/p/itm2984189f",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_boat_141"
    },
    {
        "name": "boAt Airdopes 141 Wireless Earphones",
        "brand": "boAt", "model": "141", "category": "wireless earbuds",
        "current_price": 920, "mrp": 4490, "rating": 4.2, "review_count": 45000,
        "features": ["42 Hours Playback", "Quick Charging", "Clear Voice Calls"],
        "marketplace": "Meesho",
        "product_url": "https://www.meesho.com/boat-airdopes-141-tws/p/3x9abc",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_boat_141"
    },
    {
        "name": "Noise VS102 Truly Wireless Earbuds",
        "brand": "Noise", "model": "VS102", "category": "wireless earbuds",
        "selling_price": 899, "mrp": 2999, "rating": 4.1, "review_count": 67000,
        "features": ["50H Playtime", "Instacharge", "11mm Driver", "IPX5"],
        "marketplace": "Amazon",
        "product_url": "https://www.amazon.in/dp/B09NVQ183Z",
        "image_url": "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_noise_vs102"
    },
    {
        "name": "Noise Buds VS102 TWS Headset",
        "brand": "Noise", "model": "VS102", "category": "wireless earbuds",
        "offer_price": 799, "list_price": 2999, "rating": 4.2, "review_count": 89000,
        "features": ["50 Hours Battery", "Flybird Design", "Type-C"],
        "marketplace": "Flipkart",
        "product_url": "https://www.flipkart.com/noise-buds-vs102-tws/p/itm8931234",
        "image_url": "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_noise_vs102"
    },
    {
        "name": "OnePlus Nord Buds 2 True Wireless Earbuds",
        "brand": "OnePlus", "model": "Nord Buds 2", "category": "wireless earbuds",
        "selling_price": 2499, "mrp": 3299, "rating": 4.4, "review_count": 53000,
        "features": ["25dB ANC", "12.4mm Driver", "36H Battery Life", "Fast Charging"],
        "marketplace": "Amazon",
        "product_url": "https://www.amazon.in/dp/B0BY8MCQGG",
        "image_url": "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_op_nordbuds2"
    },
    {
        "name": "OnePlus Nord Buds 2 TWS with ANC",
        "brand": "OnePlus", "model": "Nord Buds 2", "category": "wireless earbuds",
        "offer_price": 2399, "list_price": 3299, "rating": 4.5, "review_count": 62000,
        "features": ["Active Noise Cancellation", "12.4mm Drivers", "36 Hours Total Playback"],
        "marketplace": "Flipkart",
        "product_url": "https://www.flipkart.com/oneplus-nord-buds-2-tws/p/itme987654",
        "image_url": "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_op_nordbuds2"
    },
    {
        "name": "realme TechLife Buds T100",
        "brand": "realme", "model": "T100", "category": "wireless earbuds",
        "selling_price": 1399, "mrp": 2999, "rating": 4.2, "review_count": 91000,
        "features": ["28H Playtime", "10mm Bass Driver", "AI ENC for Calls", "88ms Low Latency"],
        "marketplace": "Amazon",
        "product_url": "https://www.amazon.in/dp/B0B8SFPBNH",
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_realme_t100"
    },
    {
        "name": "realme TechLife Buds T100 TWS",
        "brand": "realme", "model": "T100", "category": "wireless earbuds",
        "offer_price": 1299, "list_price": 2999, "rating": 4.3, "review_count": 112000,
        "features": ["28H Playtime", "AI Noise Cancellation", "Google Fast Pair"],
        "marketplace": "Flipkart",
        "product_url": "https://www.flipkart.com/realme-techlife-buds-t100/p/itm5432167",
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_realme_t100"
    },

    # =========================================================================
    # ELECTRONICS — LAPTOPS
    # =========================================================================
    {
        "name": "HP 15s Intel Core i3 12th Gen Laptop (8GB RAM / 512GB SSD)",
        "brand": "HP", "model": "15s", "category": "laptop",
        "selling_price": 37990, "mrp": 51000, "rating": 4.2, "review_count": 12400,
        "features": ["Intel Core i3-1215U", "8GB DDR4 RAM", "512GB NVMe SSD", "15.6 FHD", "Windows 11"],
        "marketplace": "Amazon",
        "product_url": "https://www.amazon.in/dp/B0B5RF3P7X",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_hp_15s"
    },
    {
        "name": "HP 15s Core i3 12th Gen 15.6 Inch Thin and Light Laptop",
        "brand": "HP", "model": "15s", "category": "laptop",
        "offer_price": 36490, "list_price": 51000, "rating": 4.3, "review_count": 18900,
        "features": ["Core i3 12th Gen", "8 GB RAM / 512 GB SSD", "Anti Glare Screen"],
        "marketplace": "Flipkart",
        "product_url": "https://www.flipkart.com/hp-15s-core-i3-12th-gen/p/itma1b2c3d",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_hp_15s"
    },

    # =========================================================================
    # ELECTRONICS — SMARTWATCHES
    # =========================================================================
    {
        "name": "boAt Wave Call Smart Watch with Bluetooth Calling",
        "brand": "boAt", "model": "Wave Call", "category": "smartwatch",
        "selling_price": 1299, "mrp": 7990, "rating": 4.1, "review_count": 48000,
        "features": ["1.69 HD Display", "Bluetooth Calling", "150+ Watch Faces", "HR & SpO2"],
        "marketplace": "Amazon",
        "product_url": "https://www.amazon.in/dp/B0B5L5L4P5",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_boat_wavecall"
    },
    {
        "name": "boAt Wave Call Smartwatch",
        "brand": "boAt", "model": "Wave Call", "category": "smartwatch",
        "offer_price": 1199, "list_price": 7990, "rating": 4.2, "review_count": 61000,
        "features": ["BT Calling", "1.69 inch Touch Display", "Multiple Sports Modes"],
        "marketplace": "Flipkart",
        "product_url": "https://www.flipkart.com/boat-wave-call-smartwatch/p/itmx9y8z",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_boat_wavecall"
    },
    {
        "name": "boAt Wave Call BT Calling Watch",
        "brand": "boAt", "model": "Wave Call", "category": "smartwatch",
        "current_price": 1249, "mrp": 7990, "rating": 4.0, "review_count": 12000,
        "features": ["Bluetooth Calling", "HD Screen", "Fitness Tracking"],
        "marketplace": "Meesho",
        "product_url": "https://www.meesho.com/boat-wave-call-watch/p/999msh",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_boat_wavecall"
    },

    # =========================================================================
    # FASHION — SHIRTS / CLOTHING
    # =========================================================================
    {
        "name": "Roadster Men's Regular Fit Cotton Casual Shirt",
        "brand": "Roadster", "model": "Regular Casual", "category": "shirt",
        "selling_price": 799, "mrp": 1799, "rating": 4.2, "review_count": 8900,
        "features": ["100% Cotton", "Regular Fit", "Full Sleeve", "Machine Washable"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_roadster_shirt"
    },
    {
        "name": "Roadster Men Casual Cotton Shirt",
        "brand": "Roadster", "model": "Regular Casual", "category": "shirt",
        "offer_price": 749, "list_price": 1799, "rating": 4.3, "review_count": 14200,
        "features": ["Pure Cotton", "Regular Fit", "Spread Collar", "Full Sleeves"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_roadster_shirt"
    },
    {
        "name": "Roadster Mens Cotton Casual Shirt",
        "brand": "Roadster", "model": "Regular Casual", "category": "shirt",
        "current_price": 699, "mrp": 1799, "rating": 4.1, "review_count": 3200,
        "features": ["Cotton Material", "Comfortable Fit", "Casual Wear"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_roadster_shirt"
    },
    {
        "name": "H&M Men's Regular Fit Oxford Shirt",
        "brand": "H&M", "model": "Oxford Regular", "category": "shirt",
        "selling_price": 999, "mrp": 1999, "rating": 4.4, "review_count": 5600,
        "features": ["Oxford Fabric", "Button Down Collar", "Regular Fit", "Business Casual"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_hm_oxford_shirt"
    },
    {
        "name": "H&M Regular Fit Oxford Shirt Men",
        "brand": "H&M", "model": "Oxford Regular", "category": "shirt",
        "offer_price": 949, "list_price": 1999, "rating": 4.3, "review_count": 7800,
        "features": ["Oxford Weave", "Formal & Casual", "Full Sleeve"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_hm_oxford_shirt"
    },

    # =========================================================================
    # FASHION — SHOES
    # =========================================================================
    {
        "name": "Puma Softride One4All Men's Running Shoes",
        "brand": "Puma", "model": "Softride One4All", "category": "shoes",
        "selling_price": 1599, "mrp": 3999, "rating": 4.3, "review_count": 6200,
        "features": ["Softride Foam", "Rubber Outsole", "Lightweight", "Breathable Upper"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_puma_softride"
    },
    {
        "name": "Puma Softride One4All Running Sports Shoes",
        "brand": "Puma", "model": "Softride One4All", "category": "shoes",
        "offer_price": 1499, "list_price": 3999, "rating": 4.4, "review_count": 9100,
        "features": ["Softride Cushioning", "Durable Sole", "Sports Running"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_puma_softride"
    },
    {
        "name": "Puma Softride Running Shoes Men",
        "brand": "Puma", "model": "Softride One4All", "category": "shoes",
        "current_price": 1399, "mrp": 3999, "rating": 4.1, "review_count": 2800,
        "features": ["Soft Foam Sole", "Sports Casual"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_puma_softride"
    },

    # =========================================================================
    # FASHION — BAGS
    # =========================================================================
    {
        "name": "Wildcraft Ace 30L Laptop Backpack",
        "brand": "Wildcraft", "model": "Ace 30L", "category": "bag",
        "selling_price": 1199, "mrp": 2499, "rating": 4.3, "review_count": 4100,
        "features": ["30 Litre", "Laptop Compartment", "Water Resistant", "Padded Straps"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_wildcraft_ace30"
    },
    {
        "name": "Wildcraft Ace 30 Litre Backpack",
        "brand": "Wildcraft", "model": "Ace 30L", "category": "bag",
        "offer_price": 1099, "list_price": 2499, "rating": 4.4, "review_count": 6800,
        "features": ["30L Capacity", "15.6 Laptop Sleeve", "Multiple Pockets"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_wildcraft_ace30"
    },
    {
        "name": "Wildcraft 30L Laptop Bag Backpack",
        "brand": "Wildcraft", "model": "Ace 30L", "category": "bag",
        "current_price": 999, "mrp": 2499, "rating": 4.1, "review_count": 1900,
        "features": ["30 Litre Capacity", "Laptop Pocket", "Durable"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_wildcraft_ace30"
    },

    # =========================================================================
    # BOOKS — FICTION
    # =========================================================================
    {
        "name": "Harry Potter and the Philosopher's Stone (Paperback)",
        "brand": "J.K. Rowling", "model": "HP Book 1", "category": "fiction book",
        "selling_price": 399, "mrp": 599, "rating": 4.8, "review_count": 45000,
        "features": ["Paperback", "352 Pages", "English", "Children's Fantasy"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_hp_book1"
    },
    {
        "name": "Harry Potter and the Philosopher's Stone",
        "brand": "J.K. Rowling", "model": "HP Book 1", "category": "fiction book",
        "offer_price": 349, "list_price": 599, "rating": 4.9, "review_count": 67000,
        "features": ["Paperback Edition", "352 Pages", "Fantasy Novel"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_hp_book1"
    },
    {
        "name": "Harry Potter Philosophers Stone English",
        "brand": "J.K. Rowling", "model": "HP Book 1", "category": "fiction book",
        "current_price": 329, "mrp": 599, "rating": 4.7, "review_count": 12000,
        "features": ["Children's Fantasy", "Paperback"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_hp_book1"
    },
    {
        "name": "Atomic Habits by James Clear (Paperback)",
        "brand": "James Clear", "model": "Atomic Habits", "category": "self help book",
        "selling_price": 449, "mrp": 699, "rating": 4.7, "review_count": 38000,
        "features": ["Paperback", "320 Pages", "Self-Help", "Productivity & Habits"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_atomic_habits"
    },
    {
        "name": "Atomic Habits Self Help Book",
        "brand": "James Clear", "model": "Atomic Habits", "category": "self help book",
        "offer_price": 399, "list_price": 699, "rating": 4.8, "review_count": 52000,
        "features": ["Self Help & Motivation", "320 Pages", "Bestseller"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_atomic_habits"
    },
    {
        "name": "Python Programming: Learn Python in One Day",
        "brand": "Jamie Chan", "model": "Python Book", "category": "programming book",
        "selling_price": 299, "mrp": 499, "rating": 4.4, "review_count": 8900,
        "features": ["Paperback", "Beginner Friendly", "Examples Included", "Python 3"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_python_book"
    },
    {
        "name": "Python Programming Learn in One Day Book",
        "brand": "Jamie Chan", "model": "Python Book", "category": "programming book",
        "offer_price": 279, "list_price": 499, "rating": 4.3, "review_count": 12000,
        "features": ["Tech Book", "Coding Examples", "Beginner to Intermediate"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_python_book"
    },

    # =========================================================================
    # HOME & KITCHEN
    # =========================================================================
    {
        "name": "Cello Homeware Plastic Modular Basket Storage Container",
        "brand": "Cello", "model": "Modular Basket", "category": "kitchen container",
        "selling_price": 499, "mrp": 999, "rating": 4.2, "review_count": 7800,
        "features": ["BPA Free", "Stackable", "Air-Tight Lid", "Microwave Safe"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_cello_basket"
    },
    {
        "name": "Cello Modular Storage Container Kitchen",
        "brand": "Cello", "model": "Modular Basket", "category": "kitchen container",
        "offer_price": 449, "list_price": 999, "rating": 4.3, "review_count": 10200,
        "features": ["Airtight", "Stackable Design", "Food Grade Plastic"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_cello_basket"
    },
    {
        "name": "Cello Plastic Kitchen Container Set",
        "brand": "Cello", "model": "Modular Basket", "category": "kitchen container",
        "current_price": 399, "mrp": 999, "rating": 4.1, "review_count": 3100,
        "features": ["Food Safe Plastic", "Airtight Lid", "Multi-use"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_cello_basket"
    },
    {
        "name": "Prestige Aluminium Pressure Cooker 5 Litre",
        "brand": "Prestige", "model": "Aluminium PC 5L", "category": "pressure cooker",
        "selling_price": 1799, "mrp": 3500, "rating": 4.5, "review_count": 21000,
        "features": ["5 Litre Capacity", "Aluminium Body", "ISI Certified", "Safety Valve"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_prestige_pc5l"
    },
    {
        "name": "Prestige 5 Litre Aluminium Pressure Cooker",
        "brand": "Prestige", "model": "Aluminium PC 5L", "category": "pressure cooker",
        "offer_price": 1699, "list_price": 3500, "rating": 4.6, "review_count": 33000,
        "features": ["5L Capacity", "Induction Compatible", "Safety Lid"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_prestige_pc5l"
    },
    {
        "name": "Milton Thermosteel Flask Water Bottle 500ml",
        "brand": "Milton", "model": "Thermosteel 500", "category": "water bottle",
        "selling_price": 649, "mrp": 1299, "rating": 4.4, "review_count": 19000,
        "features": ["500ml Capacity", "Keeps Hot 24H Cold 48H", "Stainless Steel", "Leak Proof"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_milton_flask"
    },
    {
        "name": "Milton Thermosteel Water Bottle 500ml",
        "brand": "Milton", "model": "Thermosteel 500", "category": "water bottle",
        "offer_price": 599, "list_price": 1299, "rating": 4.3, "review_count": 24000,
        "features": ["Double Wall Vacuum", "BPA Free", "Stainless Steel"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_milton_flask"
    },
    {
        "name": "Milton Steel Water Bottle 500ml",
        "brand": "Milton", "model": "Thermosteel 500", "category": "water bottle",
        "current_price": 549, "mrp": 1299, "rating": 4.2, "review_count": 7600,
        "features": ["Thermal Insulation", "Stainless Steel Body", "Leak Proof Cap"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_milton_flask"
    },

    # =========================================================================
    # STATIONERY
    # =========================================================================
    {
        "name": "Classmate Interleaf Spiral Notebook A4 200 Pages",
        "brand": "Classmate", "model": "Interleaf A4", "category": "notebook",
        "selling_price": 129, "mrp": 199, "rating": 4.3, "review_count": 15000,
        "features": ["200 Pages", "A4 Size", "Spiral Bound", "Single Line"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_classmate_nb"
    },
    {
        "name": "Classmate Spiral A4 Notebook 200 Pages",
        "brand": "Classmate", "model": "Interleaf A4", "category": "notebook",
        "offer_price": 119, "list_price": 199, "rating": 4.2, "review_count": 21000,
        "features": ["A4 Ruled Pages", "Spiral Binding", "200 Sheets"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_classmate_nb"
    },
    {
        "name": "Classmate A4 Spiral Notebook Single Line",
        "brand": "Classmate", "model": "Interleaf A4", "category": "notebook",
        "current_price": 109, "mrp": 199, "rating": 4.1, "review_count": 6200,
        "features": ["A4 Size", "200 Pages", "Ruled"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_classmate_nb"
    },

    # =========================================================================
    # BEAUTY & PERSONAL CARE
    # =========================================================================
    {
        "name": "Himalaya Purifying Neem Face Wash 150ml",
        "brand": "Himalaya", "model": "Neem Face Wash 150ml", "category": "face wash",
        "selling_price": 145, "mrp": 195, "rating": 4.4, "review_count": 89000,
        "features": ["Neem Extract", "Oil Control", "Anti-Acne", "Paraben Free"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_himalaya_fw"
    },
    {
        "name": "Himalaya Neem Purifying Face Wash 150ml",
        "brand": "Himalaya", "model": "Neem Face Wash 150ml", "category": "face wash",
        "offer_price": 135, "list_price": 195, "rating": 4.5, "review_count": 120000,
        "features": ["Deep Cleansing", "Neem & Turmeric", "All Skin Types"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_himalaya_fw"
    },
    {
        "name": "Himalaya Neem Face Wash 150 ml",
        "brand": "Himalaya", "model": "Neem Face Wash 150ml", "category": "face wash",
        "current_price": 125, "mrp": 195, "rating": 4.3, "review_count": 28000,
        "features": ["Neem & Aloe", "Gentle Cleansing"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_himalaya_fw"
    },

    # =========================================================================
    # TOYS
    # =========================================================================
    {
        "name": "Funskool Ludo & Snakes and Ladders Board Game",
        "brand": "Funskool", "model": "Ludo Snakes Ladders", "category": "board game",
        "selling_price": 299, "mrp": 499, "rating": 4.3, "review_count": 12400,
        "features": ["2-4 Players", "All Ages", "Classic Board Game", "Includes Dice"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1566454825481-9c31dbd79dc2?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_funskool_ludo"
    },
    {
        "name": "Funskool Ludo and Snakes Ladders Game",
        "brand": "Funskool", "model": "Ludo Snakes Ladders", "category": "board game",
        "offer_price": 249, "list_price": 499, "rating": 4.4, "review_count": 18900,
        "features": ["Classic Game", "Family Fun", "Folding Board"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1566454825481-9c31dbd79dc2?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_funskool_ludo"
    },
    {
        "name": "Funskool Board Game Ludo Snakes",
        "brand": "Funskool", "model": "Ludo Snakes Ladders", "category": "board game",
        "current_price": 229, "mrp": 499, "rating": 4.2, "review_count": 4700,
        "features": ["Fun for Kids", "Board Game", "2-4 Players"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1566454825481-9c31dbd79dc2?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_funskool_ludo"
    },

    # =========================================================================
    # DAILY NEEDS — HOUSEHOLD CLEANER
    # =========================================================================
    {
        "name": "Lizol Disinfectant Surface & Floor Cleaner 975ml",
        "brand": "Lizol", "model": "Disinfectant 975ml", "category": "household cleaner",
        "selling_price": 199, "mrp": 310, "rating": 4.4, "review_count": 34000,
        "features": ["Kills 99.9% Germs", "Pine Fragrance", "975ml", "All Floors"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_lizol_975"
    },
    {
        "name": "Lizol Floor Cleaner Disinfectant 975 ml",
        "brand": "Lizol", "model": "Disinfectant 975ml", "category": "household cleaner",
        "offer_price": 189, "list_price": 310, "rating": 4.5, "review_count": 48000,
        "features": ["Anti-Bacterial", "Multi Surface", "Pine Fresh"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_lizol_975"
    },
    {
        "name": "Lizol 975ml Pine Disinfectant Floor Cleaner",
        "brand": "Lizol", "model": "Disinfectant 975ml", "category": "household cleaner",
        "current_price": 175, "mrp": 310, "rating": 4.3, "review_count": 11000,
        "features": ["Floor Disinfectant", "Pine Scent", "Kills Germs"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_lizol_975"
    },

    # =========================================================================
    # DAILY NEEDS — STORAGE ORGANIZER
    # =========================================================================
    {
        "name": "Kuber Industries Bamboo Drawer Organizer Tray",
        "brand": "Kuber Industries", "model": "Bamboo Organizer", "category": "storage organizer",
        "selling_price": 449, "mrp": 899, "rating": 4.2, "review_count": 5600,
        "features": ["Bamboo Material", "Multi-Section", "Kitchen & Desk", "Eco-Friendly"],
        "marketplace": "Amazon",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "amz_kuber_organizer"
    },
    {
        "name": "Kuber Industries Bamboo Drawer Organizer",
        "brand": "Kuber Industries", "model": "Bamboo Organizer", "category": "storage organizer",
        "offer_price": 399, "list_price": 899, "rating": 4.3, "review_count": 8200,
        "features": ["Eco-Friendly Bamboo", "Multi-Compartment", "Desk Organizer"],
        "marketplace": "Flipkart",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "fk_kuber_organizer"
    },
    {
        "name": "Kuber Bamboo Desk Drawer Organizer Tray",
        "brand": "Kuber Industries", "model": "Bamboo Organizer", "category": "storage organizer",
        "current_price": 369, "mrp": 899, "rating": 4.1, "review_count": 2100,
        "features": ["Bamboo Tray", "Storage Sections", "Home & Office"],
        "marketplace": "Meesho",
        "product_url": "unavailable",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=400&q=80",
        "source_product_id": "msh_kuber_organizer"
    },
]


def _build_search_index() -> Dict[str, List[int]]:
    """
    Pre-builds a term-to-product-index mapping for efficient category-agnostic search.
    """
    index: Dict[str, List[int]] = {}
    for i, item in enumerate(RAW_DEMO_PRODUCTS):
        # Index on name tokens
        for tok in item["name"].lower().split():
            if len(tok) > 2:
                index.setdefault(tok, []).append(i)
        # Index on category
        for tok in item["category"].lower().split():
            index.setdefault(tok, []).append(i)
        # Index on brand
        index.setdefault(item["brand"].lower(), []).append(i)
        # Index on model
        if item.get("model"):
            index.setdefault(item["model"].lower(), []).append(i)

    # Also index via category synonyms
    for canonical_cat, synonyms in CATEGORY_SYNONYMS.items():
        # Find products that belong to this canonical category
        product_indices = [
            i for i, item in enumerate(RAW_DEMO_PRODUCTS)
            if item["category"] == canonical_cat
        ]
        for synonym in synonyms:
            for tok in synonym.lower().split():
                for idx in product_indices:
                    index.setdefault(tok, []).append(idx)

    return index


# Build once at module load
_SEARCH_INDEX: Dict[str, List[int]] = _build_search_index()


def _find_matching_indices(query: str, category: str = "") -> List[int]:
    """
    Category-agnostic fuzzy token-based search.
    Returns de-duplicated list of matching product indices.
    """
    matched_indices: List[int] = []

    # Tokenize query and category
    all_terms = []
    if query:
        all_terms += [t.lower() for t in query.split() if len(t) > 2]
    if category:
        all_terms += [t.lower() for t in category.split() if len(t) > 2]
        # Also expand synonyms for the given category
        for canonical, synonyms in CATEGORY_SYNONYMS.items():
            if category.lower() in synonyms or category.lower() == canonical:
                all_terms += [t for s in synonyms for t in s.split() if len(t) > 2]
                break

    seen = set()
    for term in all_terms:
        for idx in _SEARCH_INDEX.get(term, []):
            if idx not in seen:
                seen.add(idx)
                matched_indices.append(idx)

    return matched_indices


class DemoSourceAdapter(BaseSourceAdapter):
    """
    Category-agnostic demo source adapter.
    Accepts any natural-language query and returns all matching controlled demo products.
    """

    def __init__(self, marketplace_name: str = "DemoAll"):
        super().__init__(marketplace_name)

    def fetch_offers(self, query: str, category: Optional[str] = None, max_budget: Optional[float] = None) -> List[ProductOffer]:
        logger.info(f"DemoSourceAdapter fetching for query='{query}', category='{category}', budget={max_budget}")

        matched_indices = _find_matching_indices(query or "", category or "")

        # If no tokens matched, return empty — do NOT fabricate data
        matched_offers: List[ProductOffer] = []
        seen_source_ids = set()

        for idx in matched_indices:
            raw_item = RAW_DEMO_PRODUCTS[idx]
            sid = raw_item.get("source_product_id", "")
            if sid in seen_source_ids:
                continue
            seen_source_ids.add(sid)
            marketplace = raw_item.get("marketplace", "DemoStore")
            offer = normalize_offer(raw_item, marketplace)
            matched_offers.append(offer)

        return matched_offers
