"""
Tests for CartIQ Budget Preset Synchronization (Query to UI Filter Sync).

Verifies:
1. "laptop under ₹500" -> budget 500.0, mapped to "Under ₹500"
2. "laptop under ₹1000" -> budget 1000.0, mapped to "Under ₹1,000"
3. "shoes below ₹2000" -> budget 2000.0, mapped to "Under ₹2,000"
4. "phone under ₹5000" -> budget 5000.0, mapped to "Under ₹5,000"
5. "laptop" -> budget None, mapped to "Any"
6. "earbuds" -> budget None, mapped to "Any"
7. Phrasing variations: "less than ₹500", "within ₹500", "under 500", "below 1000", "less than 2000"
8. Non-standard preset budget "laptop under ₹1500" -> mapped to "Custom"
9. State updates: A new search query replaces the previously detected budget.
"""

from backend.services.query_service import extract_budget_from_query, map_budget_to_preset


def test_budget_sync_under_500():
    """laptop under ₹500 -> 500 -> Under ₹500."""
    b = extract_budget_from_query("laptop under ₹500")
    assert b == 500.0
    assert map_budget_to_preset(b) == "Under ₹500"


def test_budget_sync_under_1000():
    """laptop under ₹1000 -> 1000 -> Under ₹1,000."""
    b = extract_budget_from_query("laptop under ₹1000")
    assert b == 1000.0
    assert map_budget_to_preset(b) == "Under ₹1,000"


def test_budget_sync_below_2000():
    """shoes below ₹2000 -> 2000 -> Under ₹2,000."""
    b = extract_budget_from_query("shoes below ₹2000")
    assert b == 2000.0
    assert map_budget_to_preset(b) == "Under ₹2,000"


def test_budget_sync_under_5000():
    """phone under ₹5000 -> 5000 -> Under ₹5,000."""
    b = extract_budget_from_query("phone under ₹5000")
    assert b == 5000.0
    assert map_budget_to_preset(b) == "Under ₹5,000"


def test_budget_sync_no_budget_laptop():
    """laptop -> None -> Any."""
    b = extract_budget_from_query("laptop")
    assert b is None
    assert map_budget_to_preset(b) == "Any"


def test_budget_sync_no_budget_earbuds():
    """earbuds -> None -> Any."""
    b = extract_budget_from_query("earbuds")
    assert b is None
    assert map_budget_to_preset(b) == "Any"


def test_budget_sync_phrasing_variations():
    """Tests various natural language budget phrasings."""
    variations = [
        ("less than ₹500", 500.0, "Under ₹500"),
        ("within ₹500", 500.0, "Under ₹500"),
        ("under 500", 500.0, "Under ₹500"),
        ("below 1000", 1000.0, "Under ₹1,000"),
        ("less than 2000", 2000.0, "Under ₹2,000"),
    ]
    for query, expected_b, expected_preset in variations:
        b = extract_budget_from_query(query)
        assert b == expected_b, f"Query '{query}' expected budget {expected_b}, got {b}"
        assert map_budget_to_preset(b) == expected_preset


def test_budget_sync_custom_budget_unmatched_preset():
    """laptop under ₹1500 -> 1500 -> Custom (does not incorrectly snap to 1000)."""
    b = extract_budget_from_query("laptop under ₹1500")
    assert b == 1500.0
    assert map_budget_to_preset(b) == "Custom"


def test_new_search_replaces_previous_budget():
    """Simulates consecutive searches and verifies budget preset changes dynamically."""
    searches = [
        ("laptop under ₹500", "Under ₹500"),
        ("laptop under ₹2000", "Under ₹2,000"),
        ("laptop", "Any"),
    ]

    last_processed_query = None
    current_preset = None

    for user_query, expected_preset in searches:
        if last_processed_query != user_query:
            last_processed_query = user_query
            b = extract_budget_from_query(user_query)
            current_preset = map_budget_to_preset(b)

        assert current_preset == expected_preset, \
            f"Query '{user_query}' expected preset '{expected_preset}', got '{current_preset}'"
