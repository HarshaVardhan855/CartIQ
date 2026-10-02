"""
Streamlit Page Renderers for CartIQ Application.
"""

import streamlit as st
from backend.services.product_service import ProductService
from backend.services.query_service import QueryService, extract_budget_from_query, map_budget_to_preset
from ai.rag import CartIQRAGEngine
from ui.components import (
    render_header,
    render_provider_status,
    render_marketplace_search_cards
)

product_service = ProductService()
query_service = QueryService()
rag_engine = CartIQRAGEngine()


def render_search_page():
    """
    Main Search & Discovery Page.
    Displays marketplace search cards (Amazon, Flipkart, Meesho) and AI quick-question buttons.
    All AI answers use the general shopping advisor mode — no live marketplace data is fabricated.
    """
    render_header()

    current_search_input = st.session_state.get("search_input", "Earbuds under ₹1000")

    # If search input changed (new search query executed), sync budget preset radio automatically
    last_query = st.session_state.get("last_processed_query")
    if last_query != current_search_input:
        st.session_state["last_processed_query"] = current_search_input
        detected_budget = extract_budget_from_query(current_search_input)
        synced_preset = map_budget_to_preset(detected_budget)
        st.session_state["budget_preset_radio"] = synced_preset
        if synced_preset == "Custom" and detected_budget is not None:
            st.session_state["custom_budget_val"] = float(detected_budget)

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

        budget_options = ["Any", "Under ₹500", "Under ₹1,000", "Under ₹2,000", "Under ₹5,000", "Custom"]
        current_preset = st.session_state.get("budget_preset_radio", "Under ₹1,000")
        if current_preset not in budget_options:
            current_preset = "Any"

        preset_index = budget_options.index(current_preset)

        budget_preset = st.radio(
            "Budget Preset",
            options=budget_options,
            index=preset_index,
            key="budget_preset_radio"
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
            def_val = float(st.session_state.get("custom_budget_val", 1500.0))
            custom_budget = st.number_input(
                "Enter Max Budget (₹)",
                min_value=100.0,
                max_value=200000.0,
                value=def_val,
                step=100.0,
                key="custom_budget_val"
            )

    # Search Bar Section
    col_input, col_btn = st.columns([5, 1])

    with col_input:
        user_query = st.text_input(
            "Search for products across marketplaces",
            value=st.session_state.get("search_input", "Earbuds under ₹1000"),
            placeholder="e.g. Earbuds under ₹1,000, Shirts under ₹1,000, Books, Kitchen containers...",
            label_visibility="collapsed"
        )

        # Sync new user query typed directly into text input
        if user_query and user_query != st.session_state.get("last_processed_query"):
            st.session_state["last_processed_query"] = user_query
            st.session_state["search_input"] = user_query
            detected_budget = extract_budget_from_query(user_query)
            synced_preset = map_budget_to_preset(detected_budget)
            st.session_state["budget_preset_radio"] = synced_preset
            if synced_preset == "Custom" and detected_budget is not None:
                st.session_state["custom_budget_val"] = float(detected_budget)
            st.rerun()

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
        with st.spinner("Extracting intent and preparing marketplace search destinations..."):
            extracted = query_service.parse_query(
                user_query,
                simulate_gemini_failure=st.session_state.get("sim_fail", False)
            )

            budget_to_apply = custom_budget if custom_budget is not None else extracted.budget

            # Retrieve real marketplace search destinations
            search_links = product_service.get_marketplace_search_links(
                query=user_query,
                category=extracted.category
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

        # Display Real Marketplace Search Cards for Amazon, Flipkart, and Meesho filtered by user selection
        render_marketplace_search_cards(search_links, user_query, marketplace_filter=marketplace_filter)


QUICK_QUESTION_PROMPTS = {
    "Laptop features": "What features should I look for in a laptop{context_str}?",
    "Earbuds": "What should I check before buying earbuds{context_str}?",
    "Smartphones": "How should I compare smartphones{context_str}?",
    "Marketplace": "Which marketplace should I compare{context_str}?",
    "Buying tips": "What should I check before buying a product{context_str}?",
    "Compare products": "How do I compare two products{context_str}?",
}


def get_quick_question_prompt(label: str, context_str: str = "") -> str:
    """
    Returns the formatted question string for a quick question suggestion.
    """
    template = QUICK_QUESTION_PROMPTS.get(label, "")
    return template.format(context_str=context_str) if template else ""


def render_ai_shopping_page():
    """
    Dedicated AI Shopping Quick Questions Page.
    """
    st.header("🤖 AI Shopping Quick Questions")
    st.markdown("Get practical advice about products, specifications, buying decisions, and marketplace selection.")
    
    st.subheader("Quick Questions")
    
    # Context from search page if available
    context_query = st.session_state.get("search_input", "")
    context_str = f" for {context_query}" if context_query and len(context_query) < 30 else ""

    col1, col2, col3 = st.columns(3)
    
    selected_query = None
    
    if col1.button("💻 Laptop features", key="quick_btn_laptop"):
        selected_query = get_quick_question_prompt("Laptop features", context_str)
    if col2.button("🎧 Earbuds", key="quick_btn_earbuds"):
        selected_query = get_quick_question_prompt("Earbuds", context_str)
    if col3.button("📱 Smartphones", key="quick_btn_smartphones"):
        selected_query = get_quick_question_prompt("Smartphones", context_str)
        
    col4, col5, col6 = st.columns(3)
    if col4.button("🛒 Marketplace", key="quick_btn_marketplace"):
        selected_query = get_quick_question_prompt("Marketplace", context_str)
    if col5.button("💰 Buying tips", key="quick_btn_tips"):
        selected_query = get_quick_question_prompt("Buying tips", context_str)
    if col6.button("🔍 Compare products", key="quick_btn_compare"):
        selected_query = get_quick_question_prompt("Compare products", context_str)

    # If a quick question was clicked, immediately update the input state so the UI stays in sync
    if selected_query:
        st.session_state["custom_ai_page_input"] = selected_query

    st.markdown("---")
    custom_ask = st.text_input(
        "Ask CartIQ AI anything about shopping...",
        key="custom_ai_page_input"
    )

    # Determine query to execute and whether an answer must be fetched
    should_fetch = False
    if selected_query:
        active_query = selected_query
        should_fetch = True
    elif custom_ask:
        active_query = custom_ask
        if active_query != st.session_state.get("ai_page_last_query"):
            should_fetch = True
        elif "ai_page_last_answer" not in st.session_state:
            should_fetch = True
    else:
        active_query = ""
        st.session_state.pop("ai_page_last_query", None)
        st.session_state.pop("ai_page_last_answer", None)

    if should_fetch and active_query:
        with st.spinner("CartIQ AI Advisor is thinking..."):
            ask_res = rag_engine.ask_question(
                question=active_query,
                products=[],
                simulate_gemini_failure=st.session_state.get("sim_fail", False)
            )
            st.session_state["ai_page_last_query"] = active_query
            st.session_state["ai_page_last_answer"] = ask_res

    # Render answer if available
    if "ai_page_last_answer" in st.session_state and st.session_state["ai_page_last_answer"]:
        ask_res = st.session_state["ai_page_last_answer"]
        st.markdown("#### 💡 AI Answer")
        st.info(ask_res.answer)
        render_provider_status(ask_res.provider_used)
        st.caption(
            "ℹ️ This is general buying guidance based on product knowledge. "
            "CartIQ does not have access to live prices or current marketplace listings."
        )


def render_about_page():
    """
    Architecture & Spec Overview Page.
    """
    st.header("🛒 CartIQ Architecture Overview")
    st.markdown("""
    ### Core Architecture Highlights
    - **Real Marketplace Links**: Direct search links to Amazon, Flipkart, and Meesho — no fabricated prices, ASINs, or product IDs.
    - **General AI Shopping Advisor**: Gemini → Groq powered shopping guidance without hallucinating live marketplace data.
    - **Multi-LLM Resilience**: Automatic Gemini → Groq fallback with retry/backoff on rate limits (429), quota errors, or timeouts.
    - **Product Matching**: Explainable 5-step staged approach (Brand → Model/SKU → Name Similarity → Spec Match → Embedding).
    - **Deterministic Numerical Comparison**: Price comparison calculated strictly in Python, not LLM.
    - **Modular Data Source Adapters**: Pluggable adapter system for Amazon, Flipkart, Meesho, and Demo feeds.
    - **RAG Grounding**: LangChain + ChromaDB product Q&A strictly grounded on retrieved data facts.
    - **Floating AI Chat Widget**: Bottom-right floating assistant for on-demand shopping advice.

    ### Data Integrity Guarantee
    > CartIQ **never** fabricates live prices, ratings, stock levels, product images, ASINs, or product URLs.
    > All marketplace search links point to real official websites with the user's actual search query.

    ### AI Provider Chain
    ```
    User Query → Gemini 1.5 Flash (Primary)
                      ↓ (if 429/timeout/failure)
                 Groq Llama-3 (Fallback)
                      ↓ (if both fail)
                 Deterministic Rule Parser (Safety Net)
    ```
    """)
