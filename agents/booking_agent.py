"""
agents/booking_agent.py
------------------------
Handles booking creation and confirmation, given a ranked provider and user details.
"""

from __future__ import annotations

import logging
from typing import Any

from tools.booking_simulator import create_booking, confirm_booking

logger = logging.getLogger(__name__)


def book_top_provider(
    ranked_result: dict[str, Any],
    all_providers: list[dict[str, Any]],
    user_name: str,
    user_phone: str,
    service_request: str,
    preferred_time: str | None = None,
) -> dict[str, Any]:
    """
    Books the top-ranked provider and returns the confirmed booking record.

    Parameters
    ----------
    ranked_result   : Output from ranker.rank_providers()
    all_providers   : Full list of provider dicts from discovery
    user_name       : Customer's name
    user_phone      : Customer's phone number
    service_request : Original service description
    preferred_time  : Optional ISO-ish time string for scheduling
    """
    ranked = ranked_result.get("ranked_providers", [])
    if not ranked:
        logger.warning("book_top_provider → no ranked providers available.")
        return {"error": "No providers to book."}

    top = ranked[0]
    provider_id = top["provider_id"]

    # Resolve full provider record
    provider = next((p for p in all_providers if p["id"] == provider_id), None)
    if not provider:
        logger.error("book_top_provider → provider_id=%s not found in all_providers.", provider_id)
        return {"error": f"Provider {provider_id} not found."}

    booking = create_booking(
        provider=provider,
        user_name=user_name,
        user_phone=user_phone,
        service_request=service_request,
        preferred_time=preferred_time,
    )

    confirmed = confirm_booking(booking["booking_id"])
    logger.info("book_top_provider → booking %s CONFIRMED", confirmed["booking_id"])
    return confirmed
