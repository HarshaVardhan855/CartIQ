"""
Mandatory Unit Test for Gemini -> Groq LLM Provider Fallback Architecture.
Simulates Gemini rate-limit failure (HTTP 429) and verifies seamless automatic fallback to Groq or rule-based parser.
"""

from ai.provider_manager import ProviderManager

def test_gemini_to_groq_automatic_fallback():
    """
    Mandatory Spec Test:
    1. Triggers request with simulate_gemini_failure=True.
    2. ProviderManager catches Gemini 429 / retry failure.
    3. Verifies ProviderManager switches to Groq or deterministic fallback.
    4. Ensures system receives valid structured parameters and records provider_used != "gemini".
    """
    manager = ProviderManager()
    
    prompt = "Extract query: Earbuds under ₹1000"
    parsed_json, provider_used = manager.generate_json(
        prompt=prompt,
        simulate_gemini_failure=True
    )

    # Must NOT be Gemini since Gemini failed
    assert provider_used != "gemini"
    assert provider_used in ["groq", "deterministic_fallback"]
    
    # Must yield valid query parameters without crashing
    assert "category" in parsed_json or "budget" in parsed_json
    if parsed_json.get("budget"):
        assert parsed_json["budget"] == 1000.0 or parsed_json["budget"] == 1000

def test_text_generation_fallback():
    manager = ProviderManager()
    res_text, provider_used = manager.generate_text(
        prompt="Compare boAt 141 and Noise VS102",
        simulate_gemini_failure=True
    )

    assert provider_used != "gemini"
    assert len(res_text) > 0
