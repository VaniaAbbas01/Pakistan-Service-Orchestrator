"""
agents/provider_discovery.py
-----------------------------
Bridges the parsed intent to the provider search tool.
Resolves area hints and coordinates from the intent, then calls search_providers.
"""

from __future__ import annotations

import logging
from typing import Any

from tools.provider_search import search_providers
from config.settings import TOP_K_PROVIDERS, MAX_DISTANCE_KM, MIN_RATING

logger = logging.getLogger(__name__)

# ── Rough lat/lng for known Islamabad/Rawalpindi areas ────────────────────────
AREA_COORDS: dict[str, tuple[float, float]] = {
    "g-13":               (33.6938, 73.0651),
    "g-11":               (33.7010, 73.0450),
    "g-10":               (33.7055, 73.0295),
    "g 13":               (33.6938, 73.0651),
    "g 11":               (33.7010, 73.0450),
    "g 10":               (33.7055, 73.0295),
    "dha":                (33.5350, 73.1200),
    "dha phase 1":        (33.5500, 73.1050),
    "dha phase 2":        (33.5333, 73.1167),
    "dha phase 4":        (33.5200, 73.1300),
    "e-11":               (33.7200, 73.0050),
    "f-10":               (33.7123, 73.0089),
    "i-8":                (33.6750, 73.0750),
    "i-9":                (33.6600, 73.0820),
    "rawalpindi saddar":  (33.5973, 73.0479),
    "rawalpindi cantt":   (33.5950, 73.0600),
    "cantt":              (33.5950, 73.0600),
    "bahria town":        (33.5380, 73.1850),
    "bahria":             (33.5380, 73.1850),
}


def _resolve_coords(area_hint: str | None) -> tuple[float | None, float | None]:
    if not area_hint:
        return None, None
    key = area_hint.lower().strip()
    for known, coords in AREA_COORDS.items():
        if known in key or key in known:
            return coords
    return None, None


def discover_providers(intent: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Accepts a parsed intent dict and returns a list of matching providers.
    """
    category     = intent.get("category")
    area_hint    = intent.get("location_area")

    if not category:
        logger.warning("discover_providers → no category in intent, returning empty list.")
        return []

    lat, lng = _resolve_coords(area_hint)

    providers = search_providers(
        category=category,
        user_lat=lat,
        user_lng=lng,
        area_hint=area_hint,
        max_distance_km=MAX_DISTANCE_KM,
        min_rating=MIN_RATING,
        top_k=TOP_K_PROVIDERS,
    )

    logger.info(
        "discover_providers → category=%s, area=%s, found=%d",
        category, area_hint, len(providers)
    )
    return providers
