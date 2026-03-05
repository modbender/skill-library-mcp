"""
Tarot Skill (Python). See SKILL.md for entry points. Card data from data/cards.json (export from tarot_game).
"""

import random
from typing import Dict, List, Optional

from .types import (
    ReadingFocus,
    SpreadType,
    CardPosition,
    TarotReadingRequest,
    TarotReadingResult,
)
from .spreads import SPREAD_CONFIGS, suggest_spread
from .spread_layouts import SPREAD_LAYOUTS, IMAGE_ROOT, get_card_image_url
from .cards_loader import load_cards, draw_cards

DEFAULT_QUESTION_DAILY = "What does the universe want to tell me today?"


def _random_orientation(index: int, spread_type: SpreadType) -> bool:
    is_future_three = spread_type == "three" and index == 2
    return (random.random() < 0.35) if is_future_three else (random.random() < 0.5)


def perform_reading(req: TarotReadingRequest) -> TarotReadingResult:
    """Run one tarot reading (main entry)."""
    focus: ReadingFocus = req.get("focus") or "general"
    spread_type: SpreadType = req["spreadType"]
    config = SPREAD_CONFIGS[spread_type]
    question = (
        (req.get("question") or DEFAULT_QUESTION_DAILY).strip()
        if spread_type != "daily"
        else (req.get("question") or DEFAULT_QUESTION_DAILY)
    )

    if config["requires_question"] and not question:
        return {
            "ok": False,
            "question": "",
            "focus": focus,
            "spreadType": spread_type,
            "spread": [],
            "summary": "",
            "error": f"For this spread ({config['description']}), please provide your question or what you want to explore.",
        }

    deck = load_cards()
    drawn = draw_cards(deck, config["count"])
    spread: List[CardPosition] = []
    for i, card in enumerate(drawn):
        spread.append({
            "card": card,
            "positionName": config["positions"][i],
            "isReversed": _random_orientation(i, spread_type),
        })

    final_question = question or DEFAULT_QUESTION_DAILY
    summary = _build_summary(spread, final_question, focus)
    return {
        "ok": True,
        "question": final_question,
        "focus": focus,
        "spreadType": spread_type,
        "spread": spread,
        "summary": summary,
    }


def _get_meaning(pos: CardPosition, focus: ReadingFocus) -> str:
    meanings = pos["card"]["meanings"]
    lang = "en" if "en" in meanings else "zh"
    side = "reversed" if pos["isReversed"] else "upright"
    return meanings[lang][side][focus]


def _card_display_name(card: dict) -> str:
    name = card.get("name") or {}
    return name.get("en") or name.get("zh") or card.get("id", "?")


def _build_summary(
    spread: List[CardPosition], question: str, focus: ReadingFocus
) -> str:
    focus_label = {"general": "General", "love": "Love", "career": "Career"}[focus]
    lines = [f"[Focus] {focus_label}", f"[Question] {question}", ""]
    for pos in spread:
        orientation = "Reversed" if pos["isReversed"] else "Upright"
        meaning = _get_meaning(pos, focus)
        card_name = _card_display_name(pos["card"])
        lines.append(f"▸ {pos['positionName']}: {card_name} ({orientation})")
        lines.append(f"  {meaning}")
        lines.append("")
    return "\n".join(lines).strip()


def interpret_card(
    card_id: str, is_reversed: bool, focus: ReadingFocus
) -> Optional[Dict[str, str]]:
    """Get interpretation for a single card (no draw)."""
    deck = load_cards()
    for c in deck:
        if c["id"] == card_id:
            meanings = c["meanings"]
            lang = "en" if "en" in meanings else "zh"
            side = "reversed" if is_reversed else "upright"
            return {
                "cardName": _card_display_name(c),
                "meaning": meanings[lang][side][focus],
            }
    return None


__all__ = [
    "perform_reading",
    "interpret_card",
    "suggest_spread",
    "load_cards",
    "SPREAD_CONFIGS",
    "SPREAD_LAYOUTS",
    "IMAGE_ROOT",
    "get_card_image_url",
    "TarotReadingRequest",
    "TarotReadingResult",
    "ReadingFocus",
    "SpreadType",
]
