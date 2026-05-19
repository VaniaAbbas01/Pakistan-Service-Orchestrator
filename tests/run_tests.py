import sys
sys.path.insert(0, '.')

from tools.provider_search import search_providers
from tools.booking_simulator import create_booking, confirm_booking, cancel_booking
from agents.intent_parser import _rule_based_fallback
from agents.provider_discovery import discover_providers
from agents.ranker import _fallback_rank
from agents.followup_agent import generate_followup

passed = failed = 0

def ok(name):
    global passed
    passed += 1
    print("  PASS  " + name)

def fail(name, e):
    global failed
    failed += 1
    print("  FAIL  " + name + ": " + str(e))

try:
    r = search_providers("AC Technician", min_rating=4.0, top_k=5)
    assert len(r) > 0 and all(p["category"] == "AC Technician" for p in r)
    ok("search_ac_technicians (" + str(len(r)) + " found)")
except Exception as e:
    fail("search_ac_technicians", e)

try:
    r = search_providers("AC Technician", user_lat=33.6938, user_lng=73.0651, max_distance_km=10)
    ok("search_with_geo (" + str(len(r)) + " found)")
except Exception as e:
    fail("search_with_geo", e)

try:
    r = search_providers("Carpenter")
    assert r == []
    ok("search_no_match")
except Exception as e:
    fail("search_no_match", e)

try:
    i = _rule_based_fallback("mujhe AC theek karna hai")
    assert i and i["category"] == "AC Technician"
    ok("rule_based_ac")
except Exception as e:
    fail("rule_based_ac", e)

try:
    i = _rule_based_fallback("plumber chahiye")
    assert i and i["category"] == "Plumber"
    ok("rule_based_plumber")
except Exception as e:
    fail("rule_based_plumber", e)

try:
    i = _rule_based_fallback("kuch bhi")
    assert i is None
    ok("rule_based_unknown")
except Exception as e:
    fail("rule_based_unknown", e)

try:
    intent = {"category": "Electrician", "location_area": "G-13", "urgency": "today"}
    p = discover_providers(intent)
    assert isinstance(p, list)
    ok("discover_providers (" + str(len(p)) + " found)")
except Exception as e:
    fail("discover_providers", e)

try:
    providers = search_providers("Tutor", top_k=5)
    intent = {"urgency": "flexible", "budget_hint": None}
    result = _fallback_rank(providers, intent)
    assert "ranked_providers" in result and len(result["ranked_providers"]) <= 3
    top_name = result["ranked_providers"][0]["provider_name"]
    ok("fallback_ranker (top=" + top_name + ")")
except Exception as e:
    fail("fallback_ranker", e)

try:
    p = search_providers("Plumber", top_k=1)[0]
    b = create_booking(p, "Test", "+92-300-0", "Pipe leak")
    assert b["status"] == "PENDING"
    c = confirm_booking(b["booking_id"])
    assert c["status"] == "CONFIRMED"
    x = cancel_booking(b["booking_id"])
    assert x["status"] == "CANCELLED"
    ok("booking_lifecycle (" + b["booking_id"] + ")")
except Exception as e:
    fail("booking_lifecycle", e)

try:
    bk = {
        "booking_id": "BK-T01",
        "category": "AC Technician",
        "service_request": "gas refill",
        "provider_name": "Rafiq",
        "provider_phone": "+92-300-1",
        "scheduled_at": "2026-05-16 18:00",
        "price_range": {"min": 1500, "max": 5000}
    }
    for lang in ["en", "ur", "roman_ur"]:
        msg = generate_followup(bk, language=lang)
        assert "BK-T01" in msg and len(msg) > 50
    ok("followup_all_languages")
except Exception as e:
    fail("followup_all_languages", e)

print("")
print("Results: " + str(passed) + " passed, " + str(failed) + " failed")
