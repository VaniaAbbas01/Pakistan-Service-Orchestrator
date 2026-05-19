"""
agents/ranker.py
-----------------
Uses Gemini to rank shortlisted providers with natural-language reasoning
in the user's detected language (EN / Urdu / Roman Urdu).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from google import genai
from google.genai import types

from config.settings import (
    GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE,
    MAX_OUTPUT_TOKENS, PROMPTS_DIR, TOP_N_RANKED,
)

logger = logging.getLogger(__name__)
_client = genai.Client(api_key=GEMINI_API_KEY)


def _load_system_prompt() -> str:
    return (PROMPTS_DIR / "ranking_prompt.txt").read_text(encoding="utf-8")


def _score_provider(p: dict, intent: dict) -> float:
    """
    Lightweight local scorer used as fallback when LLM ranking fails.
    Returns a float 0–10.
    """
    score = p.get("rating", 3.0) * 1.5                    # 0–7.5
    if p.get("verified"):
        score += 1.0
    if p.get("certifications"):
        score += 0.5
    resp = p.get("response_time_min", 60)
    score += max(0, (60 - resp) / 60)                      # faster → higher

    if intent.get("urgency") == "immediate":
        # Penalise slow responders hard
        score -= resp / 30

    if intent.get("budget_hint") == "low":
        min_price = p.get("price_range", {}).get("min", 5000)
        score += max(0, (3000 - min_price) / 1000)

    return round(min(score, 10.0), 2)


def _fallback_rank(providers: list[dict], intent: dict) -> dict:
    scored = sorted(providers, key=lambda p: _score_provider(p, intent), reverse=True)
    ranked = []
    for i, p in enumerate(scored[:TOP_N_RANKED], start=1):
        ranked.append({
            "rank":              i,
            "provider_id":       p["id"],
            "provider_name":     p["name"],
            "score":             _score_provider(p, intent),
            "reasoning":         f"Rated {p['rating']}/5 with {p['total_reviews']} reviews. "
                                 f"Located in {p['location']['area']}. "
                                 f"Response time ~{p.get('response_time_min')} min.",
            "strengths":         p.get("tags", [])[:3],
            "caveats":           [] if p.get("verified") else ["Not yet verified"],
            "estimated_cost_pkr": f"PKR {p['price_range']['min']}–{p['price_range']['max']}",
        })
    return {
        "ranked_providers": ranked,
        "summary":          f"Top pick: {ranked[0]['provider_name']} (score {ranked[0]['score']}/10).",
        "_source":          "fallback_ranker",
    }


def rank_providers(providers: list[dict[str, Any]], intent: dict[str, Any]) -> dict[str, Any]:
    """
    Calls Gemini to rank providers with reasoning.
    Falls back to local scoring if LLM fails.
    """
    if not providers:
        return {"ranked_providers": [], "summary": "No providers found.", "_source": "empty"}

    system_prompt = _load_system_prompt()
    user_message = json.dumps({
        "intent":     intent,
        "candidates": providers,
    }, ensure_ascii=False, indent=2)

    try:
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=TEMPERATURE,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            ),
        )
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        result = json.loads(raw)
        result["_source"] = "llm"
        logger.info("rank_providers → LLM ranked %d providers", len(result.get("ranked_providers", [])))
        return result

    except Exception as exc:
        logger.warning("LLM ranking failed (%s). Using fallback scorer.", exc)
        return _fallback_rank(providers, intent)
