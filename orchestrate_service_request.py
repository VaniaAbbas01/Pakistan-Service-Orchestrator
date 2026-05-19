"""
orchestrate_service_request.py
================================
Main entry-point for the Pakistan Agentic AI Service Orchestrator.

Pipeline:
  Step 1: Intent Understanding
  Step 2: Provider Discovery & Ranking
  Step 3: Booking Simulation & Confirmation

Usage (CLI):
    python orchestrate_service_request.py [demo_index]
    python orchestrate_service_request.py --test
"""

from __future__ import annotations

import json
import logging
import sys
import argparse
from pathlib import Path
from typing import Any

# Ensure stdout can handle UTF-8 characters (like emojis) on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ── Make sub-packages importable when run from project root ───────────────────
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import LOG_LEVEL, LOG_FILE, LOGS_DIR
from config.global_rules import (
    print_global_rules, 
    STEP_1_HEADING, 
    STEP_2_HEADING, 
    STEP_3_HEADING
)
from skills.intent_parser import parse_intent
from workflows.provider_discovery import find_and_rank_providers
from workflows.booking_simulation import simulate_booking

# ── Logging setup ─────────────────────────────────────────────────────────────
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("orchestrator")


def orchestrate(
    user_request: str,
    user_name: str = "Customer",
    user_phone: str = "+92-300-0000000",
) -> dict[str, Any]:
    """
    End-to-end orchestration for a single service request using Skills & Workflows.
    """
    result: dict[str, Any] = {}

    print("\n" + "═" * 70)
    print("🇵🇰  Pakistan Agentic AI Service Orchestrator")
    print("═" * 70)
    print_global_rules()
    
    print(f"📥  Request : {user_request}")
    print(f"👤  Customer: {user_name}  |  📞 {user_phone}")
    print("═" * 70)

    # ── Step 1: Intent Understanding ──────────────────────────────────────────
    logger.info("STEP 1 ▶ Intent Parsing")
    print(f"\n{STEP_1_HEADING}")
    print("─" * len(STEP_1_HEADING))
    intent = parse_intent(user_request)
    result["intent"] = intent

    if not intent.get("service_type"):
        print("\n⚠️  Could not determine service category. Please rephrase your request.")
        return result

    # ── Step 2: Provider Discovery & Ranking ──────────────────────────────────
    logger.info("STEP 2 ▶ Provider Discovery")
    print(f"\n{STEP_2_HEADING}")
    print("─" * len(STEP_2_HEADING))
    discovery_result = find_and_rank_providers(intent)
    result["discovery"] = discovery_result
    
    ranked_providers = discovery_result.get("ranked_providers", [])

    if not ranked_providers:
        print("\n⚠️  No suitable providers found based on your request.")
        return result

    # ── Step 3: Booking Simulation & Confirmation ─────────────────────────────
    logger.info("STEP 3 ▶ Booking Simulation")
    print(f"\n{STEP_3_HEADING}")
    print("─" * len(STEP_3_HEADING))
    
    # Rule 3: Clearly log state changes
    print("  [State Change] Moving top provider to Booking Phase...")
    
    # Select the Top 1 provider for booking
    top_provider = ranked_providers[0]
    
    booking_result = simulate_booking(
        provider=top_provider,
        intent=intent,
        user_name=user_name,
        user_phone=user_phone
    )
    result["booking"] = booking_result

    print("\n  [State Change] Booking Flow Complete. Final Payload Generated.")
    print("\n" + "═" * 70 + "\n")
    return result


def test_full_flow():
    """Runs the complete end-to-end workflow as requested in the instructions."""
    print("\n🚀 Running Full End-to-End Test Flow...")
    orchestrate(
        user_request="Mujhe kal subah G-13 mein AC technician chahiye",
        user_name="Ali Raza",
        user_phone="+92-333-1234567"
    )


# ── Interactive CLI demo ───────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pakistan Service Orchestrator")
    parser.add_argument("demo_idx", nargs="?", type=int, help="Index of demo request to run")
    parser.add_argument("--test", action="store_true", help="Run the full test flow")
    
    args = parser.parse_args()

    if args.test:
        test_full_flow()
    else:
        DEMO_REQUESTS = [
            {
                "user_request": "mujhe kal subah AC mechanic chahiye G-13 mein",
                "user_name":    "Ahmed Raza",
                "user_phone":   "+92-311-1111111",
            },
            {
                "user_request": "میرے گھر میں پائپ لیک ہو رہی ہے، فوری پلمبر چاہیے",
                "user_name":    "Fatima Khan",
                "user_phone":   "+92-300-2222222",
            },
            {
                "user_request": "I need an O-Level Maths tutor in DHA next Friday evening",
                "user_name":    "Sara Ahmed",
                "user_phone":   "+92-321-3333333",
            },
        ]

        idx = args.demo_idx if args.demo_idx is not None else 0
        demo = DEMO_REQUESTS[idx % len(DEMO_REQUESTS)]
        orchestrate(**demo)
