"""
tools/booking_simulator.py
---------------------------
Simulates creating, confirming, and tracking a service booking.
No real external calls are made — all state is held in-memory for the demo.
"""

from __future__ import annotations

import uuid
import time
import logging
from datetime import datetime, timedelta
from typing import Any

from config.settings import BOOKING_CONFIRM_DELAY

logger = logging.getLogger(__name__)

# In-memory booking store (would be a DB in production)
_BOOKINGS: dict[str, dict] = {}


def create_booking(
    provider: dict[str, Any],
    user_name: str,
    user_phone: str,
    service_request: str,
    preferred_time: str | None = None,
) -> dict[str, Any]:
    """
    Creates a pending booking and returns a booking record.
    """
    booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
    eta_minutes  = provider.get("response_time_min", 45)
    scheduled_at = preferred_time or (
        datetime.now() + timedelta(minutes=eta_minutes)
    ).strftime("%Y-%m-%d %H:%M")

    booking = {
        "booking_id":       booking_id,
        "status":           "PENDING",
        "provider_id":      provider["id"],
        "provider_name":    provider["name"],
        "provider_phone":   provider["phone"],
        "category":         provider["category"],
        "user_name":        user_name,
        "user_phone":       user_phone,
        "service_request":  service_request,
        "scheduled_at":     scheduled_at,
        "eta_minutes":      eta_minutes,
        "price_range":      provider["price_range"],
        "created_at":       datetime.now().isoformat(),
    }
    _BOOKINGS[booking_id] = booking
    logger.info("create_booking → %s (PENDING)", booking_id)
    return booking


def confirm_booking(booking_id: str) -> dict[str, Any]:
    """
    Simulates provider acceptance with a short delay.
    """
    if booking_id not in _BOOKINGS:
        raise KeyError(f"Booking {booking_id} not found.")

    time.sleep(BOOKING_CONFIRM_DELAY)          # simulate async confirmation
    _BOOKINGS[booking_id]["status"] = "CONFIRMED"
    logger.info("confirm_booking → %s (CONFIRMED)", booking_id)
    return _BOOKINGS[booking_id]


def get_booking(booking_id: str) -> dict[str, Any]:
    if booking_id not in _BOOKINGS:
        raise KeyError(f"Booking {booking_id} not found.")
    return _BOOKINGS[booking_id]


def cancel_booking(booking_id: str, reason: str = "") -> dict[str, Any]:
    if booking_id not in _BOOKINGS:
        raise KeyError(f"Booking {booking_id} not found.")
    _BOOKINGS[booking_id]["status"] = "CANCELLED"
    _BOOKINGS[booking_id]["cancel_reason"] = reason
    logger.info("cancel_booking → %s", booking_id)
    return _BOOKINGS[booking_id]
