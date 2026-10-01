"""
Streamlit UI Custom Components and CSS Styling for CartIQ.
"""

import streamlit as st
from data.schemas import GroupedProduct

def inject_custom_css():
    """
    Injects rich, modern dark-mode CSS with sleek gradients and card styling.
    """
    st.markdown("""
    <style>
    /* Import modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Hero Branding Header */
    .brand-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
        text-align: center;
    }

    .brand-subtitle {
        font-size: 1.25rem;
        color: #94a3b8;
        font-weight: 500;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Product Card Container */
    .product-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .product-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 12px 24px -10px rgba(99, 102, 241, 0.3);
    }

    /* Marketplace Offer Item */
    .offer-box {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .marketplace-badge-amazon {
        background: #ff9900;
        color: #000;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
    }

    .marketplace-badge-flipkart {
        background: #2874f0;
        color: #fff;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
    }

    .marketplace-badge-meesho {
        background: #f43397;
        color: #fff;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
    }

    .lowest-price-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff;
        font-weight: 700;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 1rem;
        display: inline-block;
        margin-top: 12px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    }

    .provider-status-tag {
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .freshness-tag {
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 4px;
    }

    /* Link button styling */
    .market-link-btn {
        background: #2563eb;
        color: #ffffff !important;
        text-decoration: none !important;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        transition: background 0.2s ease;
    }
    .market-link-btn:hover {
        background: #1d4ed8;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """
    Renders CartIQ Hero Title & Subtitle.
    """
    st.markdown('<div class="brand-title">CARTIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">Search Once. Compare Everywhere.</div>', unsafe_allow_html=True)

def render_provider_status(provider_used: str):
    """
    Renders subtle technical transparency status indicator.
    """
    icon_map = {
        "gemini": "⚡ Primary Provider: Gemini 1.5 Flash",
        "groq": "🛡️ Fallback Provider: Groq (Llama-3)",
        "deterministic_fallback": "⚙️ Deterministic Rule Parser",
        "none": "ℹ️ Direct Python Search"
    }
    label = icon_map.get(provider_used, f"Provider: {provider_used}")
    st.markdown(f'<div class="provider-status-tag">{label}</div>', unsafe_allow_html=True)

def render_product_card(product: GroupedProduct, is_selected: bool = False) -> bool:
    """
    Renders canonical result card with marketplace offers and direct product links.
    Returns True if user clicks compare checkbox.
    """
    with st.container():
        st.markdown(f"### 🎧 {product.canonical_name}")
        
        col_img, col_info = st.columns([1, 3])
        
        with col_img:
            if product.image_url:
                st.image(product.image_url, use_container_width=True)
            else:
                st.markdown("🖼️ *No Image*")

        with col_info:
            st.markdown(f"**Brand:** `{product.brand}` | **Model:** `{product.model}` | **Category:** `{product.category}`")
            
            # Key features tags
            if product.features:
                st.caption("✨ " + " • ".join(product.features[:4]))

            st.markdown("---")
            st.markdown("**Marketplace Offers:**")

            for offer in product.offers:
                badge_cls = f"marketplace-badge-{offer.marketplace.lower()}"
                
                c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1.5])
                with c1:
                    st.markdown(f"<span class='{badge_cls}'>{offer.marketplace}</span>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"**₹{offer.price:,.0f}**")
                    if offer.original_price and offer.original_price > offer.price:
                        st.caption(f"~~₹{offer.original_price:,.0f}~~ ({offer.discount:.0f}% off)")
                with c3:
                    st.markdown(f"⭐ **{offer.rating}** ({offer.review_count:,})")
                with c4:
                    if offer.product_url and offer.product_url != "Product link unavailable":
                        st.markdown(
                            f'<a href="{offer.product_url}" target="_blank" class="market-link-btn">View on {offer.marketplace} &rarr;</a>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.caption("Product link unavailable")

            st.markdown(
                f'<div class="lowest-price-badge">💰 Lowest Retrieved Price: ₹{product.lowest_price:,.0f} ({product.lowest_marketplace})</div>',
                unsafe_allow_html=True
            )
            st.markdown(f'<div class="freshness-tag">Price retrieved: {product.offers[0].last_updated} | Lowest retrieved price among available results.</div>', unsafe_allow_html=True)

        checked = st.checkbox(f"Compare {product.canonical_name}", value=is_selected, key=f"chk_{product.product_id}")
        st.markdown("<br>", unsafe_allow_html=True)
        return checked
