"""Sentiment interpretation for short-term market context."""

from __future__ import annotations

from typing import Any, Dict


def classify_market_sentiment(score: float) -> str:
    if score >= 80:
        return "very_bullish"
    if score >= 65:
        return "bullish"
    if score >= 50:
        return "neutral"
    if score >= 40:
        return "weak"
    return "risk_off"


def sentiment_summary(sentiment: Dict[str, Any]) -> Dict[str, Any]:
    score = float(sentiment.get("market_sentiment_score", 0))
    regime = classify_market_sentiment(score)
    can_open_position = score >= 40
    return {
        "score": round(score, 2),
        "regime": regime,
        "can_open_position": can_open_position,
        "note": "avoid new entries when sentiment < 40",
    }
