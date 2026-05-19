"""
config/settings.py
------------------
Central configuration for the Pakistan Service Orchestrator.
"""

import os
from pathlib import Path

# ── Project Paths ─────────────────────────────────────────────────────────────
BASE_DIR       = Path(__file__).resolve().parent.parent
DATA_DIR       = BASE_DIR / "data"
LOGS_DIR       = BASE_DIR / "logs"
PROMPTS_DIR    = BASE_DIR / "prompts"

PROVIDERS_FILE = DATA_DIR / "providers.json"

# ── Google Gemini / Antigravity ───────────────────────────────────────────────
GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY", "AIzaSyAsKduxVHl1RzRYQKoh0eZxZrEUqlZ2soI")
GEMINI_MODEL     = "gemini-2.0-flash"          # swap to gemini-1.5-pro for deeper reasoning
MAX_OUTPUT_TOKENS = 2048
TEMPERATURE       = 0.2                        # low temp → deterministic ranking

# ── Google Maps API ───────────────────────────────────────────────────────────
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# ── Orchestration Knobs ───────────────────────────────────────────────────────
TOP_K_PROVIDERS       = 5    # how many providers to shortlist after search
TOP_N_RANKED          = 3    # how many to surface after LLM ranking
MAX_DISTANCE_KM       = 15   # geo-filter radius
MIN_RATING            = 3.5  # exclude providers below this rating
BOOKING_CONFIRM_DELAY = 2    # seconds to simulate async booking confirmation

# ── Supported Languages ───────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = ["en", "ur", "roman_ur"]

# ── Category ↔ Keyword Mapping (for rule-based fallback) ─────────────────────
CATEGORY_KEYWORDS = {
    "AC Technician":  ["ac", "air condition", "cooling", "gas refill", "compressor",
                       "ای سی", "ٹھنڈک", "کولنگ"],
    "Plumber":        ["plumber", "pipe", "leak", "pani", "bathroom", "sewage",
                       "پلمبر", "پائپ", "پانی", "لیک"],
    "Electrician":    ["electrician", "wiring", "bijli", "current", "short circuit",
                       "الیکٹریشن", "بجلی", "وائرنگ"],
    "Beautician":     ["beauty", "makeup", "parlour", "mehndi", "facial", "waxing",
                       "بیوٹی", "میک اپ", "مہندی"],
    "Tutor":          ["tutor", "teacher", "ustad", "maths", "english", "chemistry",
                       "ٹیوٹر", "استاد", "ریاضی", "انگریزی"],
}

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"
LOG_FILE  = LOGS_DIR / "orchestrator.log"
