"""
tests/test_orchestrator.py
---------------------------
Basic unit tests for the Pakistan Service Orchestrator.
Runs WITHOUT a real Gemini API key by using the fallback paths.
"""

import sys
import json
from pathlib import Path

# Make project root importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.provider_search  import search_providers
from tools.booking_simulator import create_booking, confirm_booking, cancel_booking
from agents.intent_parser   import _rule_based_fallback
from agents.provider_discovery import discover_providers
from agents.ranker          import _fallback_rank
from agents.followup_agent  import generate_followup


# ── 1. Provider Search ────────────────────────────────────────────────────────
def test_search_ac_technicians():
    results = search_providers("AC Technician", min_rating=4.0, top_k=5)
    assert len(results) > 0, "Should find AC technicians"
    assert all(p["category"] == "AC Technician" for p in results)
    assert all(p["rating"] >= 4.0 for p in results)
    print(f"✅ test_search_ac_technicians: found {len(results)} providers")


def test_search_with_geo():
    # G-13 coords
    results = search_providers("AC Technician", user_lat=33.6938, user_lng=73.0651, max_distance_km=10)
    assert isinstance(results, list)
    print(f"✅ test_search_with_geo: found {len(results)} providers within 10 km of G-13")


def test_search_no_category_match():
    results = search_providers("Carpenter")
    assert results == [], "Unknown category should return empty list"
    print("✅ test_search_no_category_match: returned empty list as expected")


# ── 2. Intent Fallback ────────────────────────────────────────────────────────
def test_rule_based_ac():
    intent = _rule_based_fallback("mujhe AC theek karna hai")
    assert intent is not None
    assert intent["category"] == "AC Technician"
    print("✅ test_rule_based_ac: category=AC Technician detected")


def test_rule_based_plumber_urdu():
    intent = _rule_based_fallback("پلمبر چاہیے")
    assert intent is not None
    assert intent["category"] == "Plumber"
    print("✅ test_rule_based_plumber_urdu: category=Plumber detected (Urdu)")


def test_rule_based_unknown():
    intent = _rule_based_fallback("kuch bhi")
    assert intent is None
    print("✅ test_rule_based_unknown: returned None as expected")


# ── 3. Discovery ──────────────────────────────────────────────────────────────
def test_discover_with_intent():
    intent = {
        "category":      "Electrician",
        "location_area": "G-13",
        "urgency":       "today",
    }
    providers = discover_providers(intent)
    assert isinstance(providers, list)
    print(f"✅ test_discover_with_intent: found {len(providers)} electricians")


# ── 4. Fallback Ranker ────────────────────────────────────────────────────────
def test_fallback_ranker():
    providers = search_providers("Tutor", top_k=5)
    intent = {"urgency": "flexible", "budget_hint": None}
    result = _fallback_rank(providers, intent)
    assert "ranked_providers" in result
    assert len(result["ranked_providers"]) <= 3
    assert result["ranked_providers"][0]["rank"] == 1
    print(f"✅ test_fallback_ranker: top pick = {result['ranked_providers'][0]['provider_name']}")


# ── 5. Booking Simulator ─────────────────────────────────────────────────────
def test_booking_lifecycle():
    providers = search_providers("Plumber", top_k=1)
    assert providers, "Need at least one plumber"
    p = providers[0]

    booking = create_booking(
        provider=p,
        user_name="Test User",
        user_phone="+92-300-9999999",
        service_request="Pipe leak in kitchen",
    )
    assert booking["status"] == "PENDING"

    confirmed = confirm_booking(booking["booking_id"])
    assert confirmed["status"] == "CONFIRMED"

    cancelled = cancel_booking(booking["booking_id"], reason="Test cancel")
    assert cancelled["status"] == "CANCELLED"
    print(f"✅ test_booking_lifecycle: {booking['booking_id']} → PENDING → CONFIRMED → CANCELLED")


# ── 6. Follow-up Messages ─────────────────────────────────────────────────────
def test_followup_all_languages():
    fake_booking = {
        "booking_id":      "BK-TEST001",
        "category":        "AC Technician",
        "service_request": "AC gas refill",
        "provider_name":   "Ustad Rafiq Ahmed",
        "provider_phone":  "+92-300-1234567",
        "scheduled_at":    "2026-05-16 18:00",
        "price_range":     {"min": 1500, "max": 5000},
    }
    for lang in ["en", "ur", "roman_ur"]:
        msg = generate_followup(fake_booking, language=lang)
        assert "BK-TEST001" in msg
        assert len(msg) > 50
    print("✅ test_followup_all_languages: messages generated in en / ur / roman_ur")


# ── Runner ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        test_search_ac_technicians,
        test_search_with_geo,
        test_search_no_category_match,
        test_rule_based_ac,
        test_rule_based_plumber_urdu,
        test_rule_based_unknown,
        test_discover_with_intent,
        test_fallback_ranker,
        test_booking_lifecycle,
        test_followup_all_languages,
    ]

    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"❌ {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print("="*50)
