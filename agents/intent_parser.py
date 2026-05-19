"""
agents/intent_parser.py
------------------------
Calls Gemini to extract structured intent from a raw user request
(English / Urdu / Roman Urdu).
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from google import genai
from google.genai import types

from config.settings import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE, MAX_OUTPUT_TOKENS, PROMPTS_DIR, CATEGORY_KEYWORDS

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=GEMINI_API_KEY)


def _load_system_prompt() -> str:
    return (PROMPTS_DIR / "intent_prompt.txt").read_text(encoding="utf-8")


def _rule_based_fallback(text: str) -> dict | None:
    """Simple keyword fallback when the LLM call fails."""
    text_lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return {
                "category":         category,
                "sub_service":      None,
                "location_area":    None,
                "urgency":          "flexible",
                "preferred_time":   None,
                "budget_hint":      None,
                "language_detected":"roman_ur",
                "raw_request":      text,
                "confidence":       0.55,
                "_source":          "rule_based_fallback",
            }
    return None


def parse_intent(user_text: str) -> dict:
    """
    Parses a raw user request into a structured intent dict.
    Falls back to keyword matching if the LLM call fails.
    """
    system_prompt = _load_system_prompt()

    try:
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=TEMPERATURE,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            ),
        )
        raw_text = response.text.strip()

        # Strip markdown fences if present
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
        raw_text = re.sub(r"\s*```$", "", raw_text)

        intent = json.loads(raw_text)
        intent["_source"] = "llm"
        logger.info("parse_intent → category=%s confidence=%.2f", intent.get("category"), intent.get("confidence", 0))
        return intent

    except Exception as exc:
        logger.warning("LLM intent parse failed (%s). Trying rule-based fallback.", exc)
        fallback = _rule_based_fallback(user_text)
        if fallback:
            return fallback
        return {
            "category":         None,
            "sub_service":      None,
            "location_area":    None,
            "urgency":          "flexible",
            "preferred_time":   None,
            "budget_hint":      None,
            "language_detected":"en",
            "raw_request":      user_text,
            "confidence":       0.0,
            "_source":          "failed",
        }
