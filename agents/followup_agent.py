"""
agents/followup_agent.py
-------------------------
Generates a friendly post-booking follow-up message for the user
in their detected language (English / Urdu / Roman Urdu).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Templates (used without LLM to keep follow-up fast) ──────────────────────

_TEMPLATES = {
    "en": (
        "✅ *Booking Confirmed!*\n\n"
        "Your booking ID is *{booking_id}*.\n"
        "📋 Service: {category} — {service_request}\n"
        "👨‍🔧 Provider: *{provider_name}* ({provider_phone})\n"
        "🕐 Scheduled: {scheduled_at}\n"
        "💰 Expected Cost: {price_range}\n\n"
        "The provider will contact you shortly. "
        "If you face any issue, call {provider_phone} directly.\n\n"
        "_Thank you for using the Pakistan Service Orchestrator!_ 🇵🇰"
    ),
    "ur": (
        "✅ *بکنگ کی تصدیق ہو گئی!*\n\n"
        "آپ کی بکنگ آئی ڈی: *{booking_id}*\n"
        "📋 سروس: {category} — {service_request}\n"
        "👨‍🔧 فراہم کنندہ: *{provider_name}* ({provider_phone})\n"
        "🕐 وقت: {scheduled_at}\n"
        "💰 متوقع لاگت: {price_range}\n\n"
        "فراہم کنندہ جلد آپ سے رابطہ کریں گے۔ "
        "کسی مسئلے کی صورت میں {provider_phone} پر کال کریں۔\n\n"
        "_پاکستان سروس آرکیسٹریٹر استعمال کرنے کا شکریہ!_ 🇵🇰"
    ),
    "roman_ur": (
        "✅ *Booking Confirm Ho Gayi!*\n\n"
        "Aap ki booking ID: *{booking_id}*\n"
        "📋 Service: {category} — {service_request}\n"
        "👨‍🔧 Provider: *{provider_name}* ({provider_phone})\n"
        "🕐 Waqt: {scheduled_at}\n"
        "💰 Andaza Kharcha: {price_range}\n\n"
        "Provider jald aap se rabta karega. "
        "Kisi masle mein {provider_phone} par call karein.\n\n"
        "_Pakistan Service Orchestrator use karne ka shukriya!_ 🇵🇰"
    ),
}


def generate_followup(
    booking: dict[str, Any],
    language: str = "roman_ur",
) -> str:
    """
    Returns a formatted follow-up message string based on the confirmed booking.
    """
    lang = language if language in _TEMPLATES else "roman_ur"
    template = _TEMPLATES[lang]

    price = booking.get("price_range", {})
    price_str = f"PKR {price.get('min', '?')}–{price.get('max', '?')}"

    message = template.format(
        booking_id=booking.get("booking_id", "N/A"),
        category=booking.get("category", "Service"),
        service_request=booking.get("service_request", ""),
        provider_name=booking.get("provider_name", ""),
        provider_phone=booking.get("provider_phone", ""),
        scheduled_at=booking.get("scheduled_at", "TBD"),
        price_range=price_str,
    )
    logger.info("generate_followup → booking=%s lang=%s", booking.get("booking_id"), lang)
    return message
