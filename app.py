from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# Must be very first Streamlit command
st.set_page_config(
    page_title="CartIQ — Search Once. Compare Everywhere.",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

from ui.components import inject_custom_css  # noqa: E402
from ui.pages import render_search_page, render_comparison_page  # noqa: E402

def main():
    inject_custom_css()

    # Top Navigation Tabs
    tab_search, tab_compare, tab_about = st.tabs([
        "🔍 Product Search & Discovery",
        "📊 Detailed Comparison Matrix",
        "ℹ️ Architecture & Spec"
    ])

    with tab_search:
        render_search_page()

    with tab_compare:
        render_comparison_page()

    with tab_about:
        st.header("🛒 CartIQ Architecture Overview")
        st.markdown("""
        ### Core Architecture Highlights
        - **Product Matching**: Explainable 5-step staged approach (Brand -> Model/SKU -> Name Similarity -> Spec Match -> Embedding).
        - **Deterministic Numerical Comparison**: Price comparison, lowest/highest price, price differences calculated strictly in Python, not LLM.
        - **Multi-LLM Resilience**: Automatic Gemini → Groq fallback architecture with retry/backoff on rate limits (429), quota errors, or timeouts.
        - **Modular Data Source Adapters**: Modular adapter system supporting Amazon, Flipkart, Meesho, and Demo feeds without rewriting comparison core.
        - **RAG Grounding**: LangChain + ChromaDB product Q&A strictly grounded on retrieved data facts.
        - **Direct Links**: Direct marketplace links pointing directly to original offer product pages.
        """)

if __name__ == "__main__":
    main()
