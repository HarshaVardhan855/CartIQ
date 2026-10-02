"""
Tests for CartIQ AI Shopping Assistant — General Advisor Mode.

Verifies:
1. General shopping questions are answered.
2. Product-specific feature questions are answered.
3. Marketplace guidance questions are answered.
4. Assistant does not fabricate live marketplace prices.
5. Assistant does not claim live marketplace access when APIs are not configured.
6. Existing Gemini -> Groq fallback continues to work.
7. Existing marketplace search links continue to work.
8. Detailed Comparison Matrix is no longer rendered.
9. Floating assistant UI components do not break imports.
"""

import pytest
from unittest.mock import MagicMock, patch
from ai.rag import CartIQRAGEngine
from data.schemas import AskResponse
from utils.marketplace_links import build_marketplace_search_links


# =====================================================================
# 1. General shopping question can be answered (no products needed)
# =====================================================================

def test_general_shopping_question_no_products():
    """
    General shopping question must be answered even when products=[] is passed.
    Previously the engine returned a 'no products' error — now it uses
    GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT.
    """
    mock_pm = MagicMock()
    mock_pm.generate_text.return_value = (
        "When buying wireless earbuds, look for: battery life, ANC, water resistance, and codec support.",
        "gemini"
    )

    engine = CartIQRAGEngine(provider_manager=mock_pm)
    result = engine.ask_question(
        question="What should I look for when buying wireless earbuds?",
        products=[]
    )

    assert isinstance(result, AskResponse)
    assert result.answer != ""
    assert "no products" not in result.answer.lower()
    assert result.provider_used in ["gemini", "groq", "deterministic_fallback"]
    assert result.context_used_count == 0  # Correctly 0 — general mode


# =====================================================================
# 2. Product-specific feature question can be answered
# =====================================================================

def test_product_feature_question_answered():
    """
    Product feature question (e.g. specs to compare) can be answered in general advisor mode.
    """
    mock_pm = MagicMock()
    mock_pm.generate_text.return_value = (
        "For an HP Victus laptop, compare: processor (i5/i7/Ryzen), RAM (8/16GB), "
        "GPU (Nvidia GTX/RTX), display refresh rate, and storage (SSD vs HDD).",
        "groq"
    )

    engine = CartIQRAGEngine(provider_manager=mock_pm)
    result = engine.ask_question(
        question="What specs should I compare for HP Victus laptops?",
        products=[]
    )

    assert isinstance(result, AskResponse)
    assert result.answer != ""
    assert result.context_used_count == 0
    assert result.provider_used == "groq"


# =====================================================================
# 3. Marketplace guidance question answered
# =====================================================================

def test_marketplace_guidance_question():
    """
    Marketplace-specific guidance question (Amazon vs Flipkart vs Meesho) is answered.
    """
    mock_pm = MagicMock()
    mock_pm.generate_text.return_value = (
        "For electronics like laptops, Amazon typically offers the widest selection with verified sellers. "
        "Flipkart often runs good exchange offers. Meesho is better suited for fashion and household items.",
        "gemini"
    )

    engine = CartIQRAGEngine(provider_manager=mock_pm)
    result = engine.ask_question(
        question="Which marketplace is best for buying a laptop — Amazon, Flipkart, or Meesho?",
        products=[]
    )

    assert isinstance(result, AskResponse)
    assert result.answer != ""
    assert result.context_used_count == 0


# =====================================================================
# 4. Assistant does NOT fabricate live marketplace prices
# =====================================================================

def test_general_advisor_prompt_does_not_fabricate_prices():
    """
    The general advisor prompt is invoked when products=[].
    The GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT explicitly prohibits fabricating
    current prices. Verify the correct system prompt is passed to the LLM.
    """
    from ai.prompts import GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT

    mock_pm = MagicMock()
    mock_pm.generate_text.return_value = ("General advice here.", "gemini")

    engine = CartIQRAGEngine(provider_manager=mock_pm)
    engine.ask_question(question="What is the price of iPhone 15?", products=[])

    # Verify generate_text was called with the general shopping advisor system prompt
    assert mock_pm.generate_text.called, "generate_text must be called"

    call_kwargs = mock_pm.generate_text.call_args[1]  # keyword arguments
    system_prompt_used = call_kwargs.get("system_prompt", "")

    # The general shopping advisor prompt must contain anti-fabrication rules
    assert "NEVER" in system_prompt_used or "fabricate" in system_prompt_used.lower(), \
        f"General advisor prompt must contain anti-fabrication rules. Got: {system_prompt_used[:200]!r}"



# =====================================================================
# 5. Assistant does not claim live API access
# =====================================================================

def test_no_live_api_claims_in_response():
    """
    The answer from general advisor mode should not claim to have live API data.
    The response is mocked — we verify the system prompt guards are in place.
    """
    from ai.prompts import GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT

    # Verify the system prompt explicitly states no live data access
    assert "do NOT have access to live marketplace data" in GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT or \
           "NOT have access to live" in GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT, \
        "General advisor prompt must explicitly state it has no live marketplace access"

    # Verify the prompt prohibits fabricating current prices
    assert "NEVER" in GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT
    assert "fabricat" in GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT.lower() or \
           "invent" in GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT.lower()


# =====================================================================
# 6. Existing Gemini -> Groq fallback continues to work
# =====================================================================

def test_gemini_groq_fallback_still_works_for_advisor():
    """
    When simulate_gemini_failure=True, the engine must fall back to Groq or deterministic_fallback.
    """
    from ai.provider_manager import ProviderManager

    # Real provider manager with simulated Gemini failure
    pm = ProviderManager()
    engine = CartIQRAGEngine(provider_manager=pm)

    result = engine.ask_question(
        question="What are key features to check when buying a smartwatch?",
        products=[],
        simulate_gemini_failure=True
    )

    assert isinstance(result, AskResponse)
    assert result.answer != ""
    assert result.provider_used != "gemini"
    assert result.provider_used in ["groq", "deterministic_fallback"]


# =====================================================================
# 7. Existing marketplace search links continue to work
# =====================================================================

def test_marketplace_search_links_work():
    """
    Marketplace search links must still be generated correctly for all 3 platforms.
    """
    links = build_marketplace_search_links(query="Earbuds under 1000", category="earbuds")

    assert "amazon" in links
    assert "flipkart" in links
    assert "meesho" in links

    for market, info in links.items():
        assert "url" in info
        assert info["url"].startswith("https://")
        assert "earbuds" in info["url"].lower() or "earbuds" in info.get("query", "").lower()


def test_marketplace_search_links_no_fabricated_ids():
    """
    Search URLs must not contain fabricated ASINs or product IDs.
    They must be search results pages, not direct product pages.
    """
    links = build_marketplace_search_links(query="HP Victus Laptop")

    # Amazon search URL should use /s?k= not /dp/ (product page)
    amz_url = links.get("amazon", {}).get("url", "")
    assert "/dp/" not in amz_url, "Amazon URL must be search page, not direct product page"

    # Flipkart search URL should use /search? not direct product path
    fk_url = links.get("flipkart", {}).get("url", "")
    assert "search" in fk_url.lower() or "q=" in fk_url, "Flipkart URL must be a search page"


# =====================================================================
# 8. Detailed Comparison Matrix is no longer rendered
# =====================================================================

def test_detailed_comparison_matrix_removed_from_app():
    """
    The app.py must not import or call render_comparison_page.
    The Detailed Comparison Matrix tab must not be present.
    """
    import ast
    import os

    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        source = f.read()

    assert "render_comparison_page" not in source, \
        "render_comparison_page must not be called in app.py — Detailed Comparison Matrix was removed"
    assert "Detailed Comparison Matrix" not in source, \
        "Detailed Comparison Matrix tab must not be in app.py"


def test_render_comparison_page_removed_from_pages():
    """
    ui/pages.py must not define render_comparison_page anymore.
    """
    import os
    pages_path = os.path.join(os.path.dirname(__file__), "..", "ui", "pages.py")
    with open(pages_path, "r", encoding="utf-8") as f:
        source = f.read()

    assert "def render_comparison_page" not in source, \
        "render_comparison_page function must be removed from ui/pages.py"


# =====================================================================
# 9. Floating assistant UI components do not break imports
# =====================================================================

def test_floating_chat_widget_importable():
    """
    inject_floating_chat_widget must be importable from ui.components.
    """
    from ui.components import inject_floating_chat_widget
    assert callable(inject_floating_chat_widget), \
        "inject_floating_chat_widget must be a callable function in ui.components"


def test_all_component_imports_work():
    """
    All required UI component functions must be importable without errors.
    """
    from ui.components import (
        inject_custom_css,
        inject_floating_chat_widget,
        render_header,
        render_provider_status,
        render_marketplace_search_cards,
    )
    assert all([
        callable(inject_custom_css),
        callable(inject_floating_chat_widget),
        callable(render_header),
        callable(render_provider_status),
        callable(render_marketplace_search_cards),
    ])


def test_ask_ai_endpoint_importable():
    """
    The /ask_ai endpoint handler must be importable from backend.routes.ask.
    """
    from backend.routes.ask import ask_ai_floating, FloatingAskRequest
    assert callable(ask_ai_floating)


def test_render_about_page_importable():
    """
    render_about_page and render_ai_shopping_page must be importable.
    """
    from ui.pages import render_about_page, render_search_page, render_ai_shopping_page
    assert callable(render_about_page)
    assert callable(render_search_page)
    assert callable(render_ai_shopping_page)


# =====================================================================
# 10. AI Shopping Quick Questions — Six Suggestions & Submission Flow
# =====================================================================

def test_quick_question_prompts_configured():
    """
    Verify all 6 quick question suggestions are registered with non-empty templates.
    """
    from ui.pages import QUICK_QUESTION_PROMPTS, get_quick_question_prompt

    expected_suggestions = [
        "Laptop features",
        "Earbuds",
        "Smartphones",
        "Marketplace",
        "Buying tips",
        "Compare products"
    ]

    for label in expected_suggestions:
        assert label in QUICK_QUESTION_PROMPTS, f"Missing quick question suggestion: {label}"
        prompt = get_quick_question_prompt(label)
        assert prompt != "", f"Prompt for {label} must not be empty"
        assert "{" not in prompt, f"Prompt for {label} has unformatted placeholders: {prompt}"

    # Verify context formatting works as expected
    laptop_with_ctx = get_quick_question_prompt("Laptop features", " for gaming")
    assert "for gaming" in laptop_with_ctx


@pytest.mark.parametrize("suggestion_label,expected_topic", [
    ("Laptop features", "laptop"),
    ("Earbuds", "earbuds"),
    ("Smartphones", "smartphones"),
    ("Marketplace", "marketplace"),
    ("Buying tips", "buying"),
    ("Compare products", "compare"),
])
def test_all_six_quick_questions_produce_non_empty_answers(suggestion_label, expected_topic):
    """
    Verify that each of the six Quick Question suggestions produces a non-empty
    request prompt and a non-empty AskResponse from the AI Shopping Assistant.
    """
    from ui.pages import get_quick_question_prompt

    question = get_quick_question_prompt(suggestion_label)
    assert question != "", f"Prompt for {suggestion_label} must be non-empty"

    mock_pm = MagicMock()
    mock_pm.generate_text.return_value = (
        f"Here is practical advice regarding {expected_topic}.",
        "gemini"
    )

    engine = CartIQRAGEngine(provider_manager=mock_pm)
    result = engine.ask_question(question=question, products=[])

    assert isinstance(result, AskResponse)
    assert result.answer != ""
    assert result.context_used_count == 0
    assert result.provider_used == "gemini"
    mock_pm.generate_text.assert_called_once()


def test_quick_questions_typed_question_path():
    """
    Confirm typed question path directly returns a non-empty answer through the assistant.
    """
    mock_pm = MagicMock()
    mock_pm.generate_text.return_value = (
        "Look for active noise cancellation, comfort, battery life, and sound quality.",
        "groq"
    )

    engine = CartIQRAGEngine(provider_manager=mock_pm)
    result = engine.ask_question(
        question="Which noise-cancelling headphones should I consider for travel?",
        products=[]
    )

    assert isinstance(result, AskResponse)
    assert "noise cancellation" in result.answer
    assert result.provider_used == "groq"
    assert result.context_used_count == 0


def test_quick_question_button_immediate_submission_flow():
    """
    Simulate render_ai_shopping_page execution when a quick question button is clicked.
    Verify that clicking a button immediately invokes rag_engine.ask_question without
    requiring a separate text input click or secondary submit button.
    """
    from ui import pages

    # Mock session state dictionary
    mock_state = {"search_input": ""}

    # Create mock column objects where col1 (Laptop features) is clicked
    mock_col = MagicMock()
    mock_col.button.side_effect = lambda label, key=None: key == "quick_btn_laptop"

    with patch.object(pages, "st") as mock_st, \
         patch.object(pages, "rag_engine") as mock_engine:

        mock_st.session_state = mock_state
        mock_st.columns.return_value = [mock_col, mock_col, mock_col]
        mock_st.text_input.return_value = ""

        mock_ask_res = AskResponse(
            answer="Here are the top laptop features to evaluate: CPU, RAM, GPU, display, and battery.",
            context_used_count=0,
            provider_used="gemini"
        )
        mock_engine.ask_question.return_value = mock_ask_res

        # Call the page render function
        pages.render_ai_shopping_page()

        # 1. Verify session state for text input was updated with the clicked question
        assert mock_state.get("custom_ai_page_input") == "What features should I look for in a laptop?"

        # 2. Verify rag_engine.ask_question was immediately called with that question
        mock_engine.ask_question.assert_called_once()
        call_kwargs = mock_engine.ask_question.call_args[1]
        assert call_kwargs["question"] == "What features should I look for in a laptop?"
        assert call_kwargs["products"] == []

        # 3. Verify the generated answer was saved in session state and displayed
        assert mock_state.get("ai_page_last_answer") == mock_ask_res
        mock_st.info.assert_called_with(mock_ask_res.answer)

