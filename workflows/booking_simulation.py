"""
workflows/booking_simulation.py
--------------------------------
Workflow: Simulates checking availability, booking a slot, scheduling a reminder,
and generating a beautiful WhatsApp-style confirmation in 3 languages.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# Mock database for bookings
_BOOKINGS: dict[str, dict] = {}

# ── WhatsApp Style Templates ─────────────────────────────────────────────────

_WHATSAPP_TEMPLATES = {
    "en": (
        "🟢 *BOOKING CONFIRMED* 🟢\n"
        "Hello {user_name}! Your service request has been successfully booked.\n\n"
        "🧾 *Receipt & Details*\n"
        "▪️ *Booking ID:* {booking_id}\n"
        "▪️ *Service:* {service_type} ({sub_service})\n"
        "▪️ *Provider:* {provider_name}\n"
        "▪️ *Contact:* {provider_phone}\n"
        "▪️ *Scheduled Time:* {scheduled_time}\n"
        "▪️ *Estimated Cost:* {cost}\n\n"
        "💡 *Why we chose them:* {reasoning}\n\n"
        "🔔 _We have scheduled a reminder for you 1 hour before the service._\n"
        "Thank you for choosing Pakistan Service Orchestrator! 🇵🇰"
    ),
    "ur": (
        "🟢 *بکنگ کی تصدیق ہو گئی* 🟢\n"
        "السلام علیکم {user_name}! آپ کی سروس کی درخواست کامیابی سے بک ہو گئی ہے۔\n\n"
        "🧾 *تفصیلات اور رسید*\n"
        "▪️ *بکنگ آئی ڈی:* {booking_id}\n"
        "▪️ *سروس:* {service_type} ({sub_service})\n"
        "▪️ *فراہم کنندہ:* {provider_name}\n"
        "▪️ *رابطہ نمبر:* {provider_phone}\n"
        "▪️ *وقت:* {scheduled_time}\n"
        "▪️ *متوقع لاگت:* {cost}\n\n"
        "💡 *ہماری تجویز کی وجہ:* {reasoning}\n\n"
        "🔔 _سروس سے 1 گھنٹہ قبل آپ کو یاد دہانی کا پیغام بھیج دیا جائے گا۔_\n"
        "پاکستان سروس آرکیسٹریٹر استعمال کرنے کا شکریہ! 🇵🇰"
    ),
    "roman_ur": (
        "🟢 *BOOKING CONFIRMED - Service Orchestrator* 🟢\n"
        "Asalam-o-Alaikum {user_name}! Aap ki service request successfully book ho gayi hai. 🛠️\n\n"
        "🧾 *Booking Details*\n"
        "▪️ *Booking ID:* {booking_id}\n"
        "▪️ *Service:* {service_type} ({sub_service})\n"
        "▪️ *Assigned Professional:* {provider_name}\n"
        "▪️ *Contact:* {provider_phone}\n"
        "▪️ *Scheduled Time:* {scheduled_time}\n"
        "▪️ *Estimated Cost:* {cost}\n\n"
        "💡 *Agentic Decision Logic:* \n{reasoning}\n\n"
        "⏳ *Next Steps:*\n"
        "Aap ke provider jaldi aapse raabta karenge. Service se 1 ghanta pehle aap ko automatic reminder bhi mil jayega.\n\n"
        "Pakistan Service Orchestrator use karne ka shukriya! 🇵🇰"
    ),
}

def simulate_booking(
    provider: dict[str, Any],
    intent: dict[str, Any],
    user_name: str,
    user_phone: str
) -> dict[str, Any]:
    print("\n[Workflow: Booking Simulation] 📅 Checking availability and booking slot...")

    # 1. Check availability (Mock logic: always available)
    print(f"  ➜ Checking availability for {provider['name']}...")
    print(f"  ✅ Provider is available!")

    # 2. Book the slot
    booking_id = f"PK-{uuid.uuid4().hex[:8].upper()}"
    
    # Resolve scheduling time
    pref_time = intent.get("preferred_date_time")
    if not pref_time or pref_time.lower() == "flexible":
        # If flexible, default to 2 hours from now
        sched_time_obj = datetime.now() + timedelta(hours=2)
        scheduled_time = sched_time_obj.strftime("%Y-%m-%d %H:%M")
    else:
        scheduled_time = pref_time
        try:
            sched_time_obj = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
        except ValueError:
            sched_time_obj = datetime.now() + timedelta(hours=2)

    booking_record = {
        "booking_id": booking_id,
        "status": "CONFIRMED",
        "provider_id": provider["id"],
        "user_name": user_name,
        "user_phone": user_phone,
        "scheduled_time": scheduled_time,
        "created_at": datetime.now().isoformat()
    }
    
    # Save to mock in-memory DB
    _BOOKINGS[booking_id] = booking_record
    print(f"  ➜ Slot booked successfully! Booking ID: {booking_id}")

    # 3. Schedule Reminder
    reminder_time = sched_time_obj - timedelta(hours=1)
    print(f"  🔔 Reminder scheduled for: {reminder_time.strftime('%Y-%m-%d %H:%M')} (1 hour before)")

    # 4. Generate WhatsApp-style Confirmation
    language = intent.get("language", "roman_ur")
    if language not in _WHATSAPP_TEMPLATES:
        language = "roman_ur"
        
    template = _WHATSAPP_TEMPLATES[language]
    
    price = provider.get("price_range", {})
    cost_str = f"PKR {price.get('min', '?')} - {price.get('max', '?')}"
    
    whatsapp_msg = template.format(
        user_name=user_name,
        booking_id=booking_id,
        service_type=intent.get("service_type", "Service"),
        sub_service=intent.get("sub_service", ""),
        provider_name=provider["name"],
        provider_phone=provider["phone"],
        scheduled_time=scheduled_time,
        cost=cost_str,
        reasoning=provider.get("reasoning", "Highly rated and nearby.")
    )
    
    print("\n  📲 WhatsApp Confirmation Generated:")
    print("  " + "─"*50)
    for line in whatsapp_msg.split('\n'):
        print(f"  | {line}")
    print("  " + "─"*50)

    return {
        "booking": booking_record,
        "whatsapp_message": whatsapp_msg
    }
