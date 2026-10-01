"""
Streamlit Page Renderers for CartIQ Application.
"""

import streamlit as st
from backend.services.product_service import ProductService
from backend.services.query_service import QueryService
from backend.services.comparison_service import ComparisonService
from backend.services.email_service import EmailService
from ai.rag import CartIQRAGEngine
from ui.components import render_header, render_product_card, render_provider_status

product_service = ProductService()
query_service = QueryService()
comparison_service = ComparisonService()
email_service = EmailService()
rag_engine = CartIQRAGEngine()

def render_search_page():
    """
    Main Search & Comparison Page.
    """
    render_header()

    # Sidebar Options & Developer Options
    with st.sidebar:
        st.header("⚙️ Search Filters")
        
        # Dev Fallback Simulator Toggle
        st.subheader("🛠️ Developer Testing")
        simulate_gemini_fail = st.checkbox(
            "⚡ Simulate Gemini 429 Rate Limit",
            value=st.session_state.get("sim_fail", False),
            help="Forces ProviderManager to fail Gemini retries and trigger automatic fallback to Groq!"
        )
        st.session_state["sim_fail"] = simulate_gemini_fail

        st.markdown("---")

        # Marketplace Filter
        marketplace_filter = st.selectbox(
            "Marketplace",
            options=["All", "Amazon", "Flipkart", "Meesho"],
            index=0
        )

        # Sort Filter
        sort_by = st.selectbox(
            "Sort Results By",
            options=["Lowest Price", "Highest Rating", "Highest Discount"],
            index=0
        )

        # Budget Quick Filter
        st.markdown("---")
        st.subheader("💰 Maximum Budget")
        budget_preset = st.radio(
            "Budget Preset",
            options=["Any", "Under ₹500", "Under ₹1,000", "Under ₹2,000", "Under ₹5,000", "Custom"],
            index=2
        )

        custom_budget = None
        if budget_preset == "Under ₹500":
            custom_budget = 500.0
        elif budget_preset == "Under ₹1,000":
            custom_budget = 1000.0
        elif budget_preset == "Under ₹2,000":
            custom_budget = 2000.0
        elif budget_preset == "Under ₹5,000":
            custom_budget = 5000.0
        elif budget_preset == "Custom":
            custom_budget = st.number_input("Enter Max Budget (₹)", min_value=100.0, max_value=200000.0, value=1500.0, step=100.0)

    # Search Bar Section
    col_input, col_btn = st.columns([5, 1])
    
    with col_input:
        user_query = st.text_input(
            "Search for products across marketplaces",
            value=st.session_state.get("search_input", "Earbuds under ₹1000"),
            placeholder="e.g. Earbuds under ₹1,000, Shirts under ₹1,000, Books, Kitchen containers...",
            label_visibility="collapsed"
        )

    with col_btn:
        st.button("🔍 SEARCH", use_container_width=True)

    # Sample Quick Buttons — diverse categories
    st.caption("Try searching:")
    qb_cols = st.columns(4)
    quick_searches = [
        ("🎧 Earbuds under ₹1,000",   "Earbuds under ₹1000"),
        ("👕 Shirts under ₹1,000",     "Shirts under ₹1000"),
        ("📚 Books under ₹500",        "Books under ₹500"),
        ("🍱 Kitchen containers",      "kitchen containers"),
        ("👟 Shoes under ₹2,000",      "Shoes under ₹2000"),
        ("🎲 Board games",             "Board games"),
        ("💊 Face wash under ₹200",    "Face wash under ₹200"),
        ("🧹 Daily household needs",   "daily household cleaner"),
    ]
    for col, (label, search_val) in zip(qb_cols * 2, quick_searches):
        if col.button(label, key=f"quick_{search_val[:10]}"):
            st.session_state["search_input"] = search_val
            st.rerun()

    st.markdown("---")

    # Execute Search Logic
    if user_query:
        with st.spinner("Extracting intent and retrieving product offers..."):
            extracted = query_service.parse_query(
                user_query,
                simulate_gemini_failure=st.session_state.get("sim_fail", False)
            )

            budget_to_apply = custom_budget if custom_budget is not None else extracted.budget

            grouped_products, warnings = product_service.search_and_group(
                query=user_query,
                category=extracted.category,
                max_budget=budget_to_apply,
                marketplace_filter=marketplace_filter,
                sort_by=sort_by
            )

        # Top Bar: Intent & Provider Transparency Status
        c_status, c_intent = st.columns([1, 2])
        with c_status:
            render_provider_status(extracted.provider_used)
        with c_intent:
            intent_details = []
            if extracted.category:
                intent_details.append(f"Category: **{extracted.category.title()}**")
            if budget_to_apply:
                intent_details.append(f"Max Budget: **₹{budget_to_apply:,.0f}**")
            if extracted.requirements:
                intent_details.append(f"Requirements: **{', '.join(extracted.requirements)}**")
            st.markdown(" | ".join(intent_details) if intent_details else f"Query: *{user_query}*")

        # Display Source Warnings if any marketplace is down
        for warn in warnings:
            st.warning(f"⚠️ {warn}")

        if not grouped_products:
            st.warning(
                f"No products found for **'{user_query}'**. "
                "Try broadening your search — e.g. remove the budget qualifier, "
                "or try a category like *shirts*, *books*, *kitchen containers*, *shoes*, *board games*, or *face wash*."
            )
            return

        st.subheader(f"Results for '{user_query}' ({len(grouped_products)} Products Found)")

        # State tracking for comparison selection
        if "selected_prod_ids" not in st.session_state:
            st.session_state["selected_prod_ids"] = []

        # Render Product Cards
        for prod in grouped_products:
            is_sel = prod.product_id in st.session_state["selected_prod_ids"]
            checked = render_product_card(prod, is_selected=is_sel)
            if checked and prod.product_id not in st.session_state["selected_prod_ids"]:
                st.session_state["selected_prod_ids"].append(prod.product_id)
            elif not checked and prod.product_id in st.session_state["selected_prod_ids"]:
                st.session_state["selected_prod_ids"].remove(prod.product_id)

        # Selected Products Action Bar
        if st.session_state["selected_prod_ids"]:
            st.info(f"💡 **{len(st.session_state['selected_prod_ids'])}** products selected for comparison matrix.")

        # --- AI SHOPPING QUESTIONS SECTION (Section 20) ---
        st.markdown("---")
        st.subheader("🤖 Ask CartIQ AI Shopping Assistant")
        st.caption("Ask questions grounded strictly on current search results.")

        # Quick Question Buttons
        q_col1, q_col2, q_col3 = st.columns(3)
        ai_query = ""
        if q_col1.button("Which product has the lowest price?"):
            ai_query = "Which product has the lowest price?"
        if q_col2.button("Which one has the highest rating?"):
            ai_query = "Which product has the highest rating?"
        if q_col3.button("Compare battery life & features"):
            ai_query = "Which earbuds have the best battery-related features?"

        custom_ask = st.text_input("Or ask a custom question:", value=ai_query, placeholder="e.g. Which one is best for phone calls?")
        
        if custom_ask:
            with st.spinner("Generating grounded answer via CartIQ RAG..."):
                ask_res = rag_engine.ask_question(
                    question=custom_ask,
                    products=grouped_products,
                    simulate_gemini_failure=st.session_state.get("sim_fail", False)
                )
                
                st.markdown("#### 💡 AI Answer:")
                st.info(ask_res.answer)
                render_provider_status(ask_res.provider_used)

        # --- EMAIL COMPARISON RESULTS SECTION (Section 29) ---
        st.markdown("---")
        st.subheader("📧 Email Comparison Results")
        with st.form("email_form"):
            recipient = st.text_input("Enter your email address:", placeholder="user@example.com")
            send_btn = st.form_submit_button("Send Email Summary")
            
            if send_btn:
                if not recipient or "@" not in recipient:
                    st.error("Please enter a valid email address.")
                else:
                    with st.spinner("Dispatching comparison results via SendGrid..."):
                        res = email_service.send_comparison_email(
                            recipient_email=recipient,
                            search_query=user_query,
                            products=grouped_products
                        )
                        if res.get("success"):
                            st.success(res.get("message"))
                        else:
                            st.error(res.get("message"))

def render_comparison_page():
    """
    Detailed Product Comparison View Page (Section 28).
    """
    st.header("📊 PRODUCT COMPARISON MATRIX")
    
    sel_ids = st.session_state.get("selected_prod_ids", [])
    if not sel_ids:
        st.warning("No products selected for comparison. Please go back to Search and check the 'Compare' boxes on products.")
        return

    all_prods, _ = product_service.search_and_group(query="")
    selected_prods = [p for p in all_prods if p.product_id in sel_ids]

    if not selected_prods:
        st.warning("Selected products not found.")
        return

    matrix = comparison_service.build_comparison_matrix(selected_prods)

    st.markdown("### Factual Price & Feature Matrix")
    
    # Render Comparison Table
    headers = ["Feature / Metric"] + [p.canonical_name for p in selected_prods]
    
    row_lowest = ["Lowest Retrieved Price"] + [f"₹{p.lowest_price:,.0f} ({p.lowest_marketplace})" for p in selected_prods]
    row_highest = ["Highest Price"] + [f"₹{p.highest_price:,.0f}" for p in selected_prods]
    row_diff = ["Price Difference (Savings)"] + [f"₹{p.price_difference:,.0f}" for p in selected_prods]
    row_offers = ["Total Marketplace Offers"] + [f"{p.available_offers_count} Offers" for p in selected_prods]
    row_rating = ["Rating"] + [f"⭐ {max([o.rating for o in p.offers], default=0.0)}" for p in selected_prods]
    
    table_data = [row_lowest, row_highest, row_diff, row_offers, row_rating]

    st.table({
        headers[0]: [row[0] for row in table_data],
        **{headers[i+1]: [row[i+1] for row in table_data] for i in range(len(selected_prods))}
    })

    st.markdown("### 📝 Comparison Summary")
    st.info(matrix.summary)
