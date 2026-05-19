"""
tools/provider_search.py
-------------------------
Searches and geo-filters the mock provider dataset based on
category, area, and minimum rating.
"""

from __future__ import annotations

import json
import math
import logging
from pathlib import Path
from typing import Any

from config.settings import PROVIDERS_FILE, MAX_DISTANCE_KM, MIN_RATING, TOP_K_PROVIDERS

logger = logging.getLogger(__name__)


# ── Haversine distance (km) ────────────────────────────────────────────────────
def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _load_providers() -> list[dict]:
    with open(PROVIDERS_FILE, encoding="utf-8") as f:
        return json.load(f)["providers"]


def search_providers(
    category: str,
    user_lat: float | None = None,
    user_lng: float | None = None,
    area_hint: str | None = None,
    max_distance_km: float = MAX_DISTANCE_KM,
    min_rating: float = MIN_RATING,
    top_k: int = TOP_K_PROVIDERS,
) -> list[dict[str, Any]]:
    """
    Returns up to `top_k` providers that:
      - Match `category` (case-insensitive)
      - Are within `max_distance_km` of the user (if coords supplied)
        OR whose area contains `area_hint` (if coords not supplied)
      - Have rating >= `min_rating`
    Each result has an injected `distance_km` field.
    """
    providers = _load_providers()
    results = []

    for p in providers:
        # Category filter
        if p["category"].lower() != category.lower():
            continue

        # Rating filter
        if p["rating"] < min_rating:
            continue

        # Geo filter
        dist = None
        if user_lat is not None and user_lng is not None:
            plat = p["location"]["lat"]
            plng = p["location"]["lng"]
            dist = _haversine(user_lat, user_lng, plat, plng)
            if dist > max_distance_km:
                continue
        elif area_hint:
            if area_hint.lower() not in p["location"]["area"].lower():
                # soft match — still include but mark distance unknown
                dist = None

        p_copy = dict(p)
        p_copy["distance_km"] = round(dist, 2) if dist is not None else None
        results.append(p_copy)

    # Sort: by distance (if available), then by rating desc
    results.sort(
        key=lambda x: (x["distance_km"] if x["distance_km"] is not None else 999, -x["rating"])
    )

    logger.info("search_providers → category=%s, found=%d", category, len(results[:top_k]))
    return results[:top_k]
