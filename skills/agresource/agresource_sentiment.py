#!/usr/bin/env python3
"""
AgResource Sentiment Analysis

Analyzes newsletter content for sentiment across multiple dimensions.
Compares to historical sentiment to detect trends.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

MEMORY_DIR = Path.home() / "clawd" / "memory" / "agresource"
SENTIMENT_FILE = MEMORY_DIR / "sentiment_history.json"

# Sentiment keywords for PRICE IMPACT detection
# BULLISH = Prices expected to go UP
# BEARISH = Prices expected to go DOWN

BULLISH_KEYWORDS = [
    # Direct price signals
    "prices advancing", "prices rally", "price strength", "higher prices",
    "support", "rally", "gains", "upward trend", "strength", "bullish",

    # Explicit bias/position statements
    "bullish bias", "bullish bias maintained", "bullish outlook",
    "favorable bias", "positive bias",

    # Demand signals (more demand = higher prices)
    "demand strong", "export demand rising", "strong demand", "demand solid",
    "china buying", "china purchases", "china advancing", "chinese imports",
    "record demand", "export sales", "new sales", "flash sales",

    # Supply constraints (less supply = higher prices)
    "production cuts", "production issues", "supply concerns",
    "tight supplies", "tight stocks", "stock drawdown", "inventory tight",

    # Weather stress on crops (less yield = higher prices)
    "drought", "drought stress", "heat stress", "excessive heat",
    "dry conditions", "moisture stress", "weather concerns",
    "weather damage", "crop stress", "yield pressure", "yield concerns",

    # Geopolitical/Supply chain
    "tariff threats", "supply disruptions", "logistics issues",
    "port strikes", "transport issues",

    # Index fund activity
    "index fund buying", "fund buying", "speculative buying",
]

BEARISH_KEYWORDS = [
    # Direct price signals
    "prices declining", "price weakness", "lower prices",
    "resistance", "sell-off", "losses", "downward trend", "weakness", "bearish",

    # Explicit bias/position statements
    "bearish bias", "bearish bias maintained", "bearish outlook",
    "negative bias", "unfavorable bias", "selling between", "enduring selling",
    "doubts.*push above", "resistance.*above", "capped.*rally", "capped.*between",

    # Demand weakness (less demand = lower prices)
    "weak demand", "demand concerns", "lackluster demand",
    "export concerns", "export weakness", "china auctioning", "china selling",

    # Supply glut (more supply = lower prices)
    "record crop", "record production", "large crop", "bumper crop",
    "production increasing", "supply ample", "supplies adequate",
    "stock buildup", "inventory building", "production on track for record",
    "harvest record", "record.*crop", "record.*production",

    # Favorable weather (more yield = lower prices)
    "favorable weather", "ideal conditions", "timely rains",
    "adequate moisture", "beneficial rainfall", "normal weather",
    "good growing conditions", "improved weather", "weather improving",
    "rain starting to fall", "rains.*starting", "rainfall.*slated",

    # Trade/tariff issues reducing exports
    "tariff concerns", "trade uncertainty", "trade barriers",
    "export competition", "south america", "brazil", "argentina production",
    "competition", "sa competition", "south american crop size",
    "dulling.*export", "export opportunity.*limited",

    # Index fund activity
    "index fund selling", "fund selling", "speculative selling",
    "fund rebalance", "index fund rebalance",
]

# These track the direction of weather/production events
# but their PRICE impact must be inverted
WEATHER_POSITIVE_FOR_CROPS = [
    "favorable", "beneficial", "improving", "adequate moisture",
    "timely rains", "ideal conditions", "normal", "good weather"
]

WEATHER_NEGATIVE_FOR_CROPS = [
    "drought", "excessive", "flooding", "heat stress",
    "dry conditions", "moisture stress", "weather concerns",
    "hot and dry", "below normal moisture", "stress"
]

SALES_ADVICE_KEYWORDS = [
    "buy", "sell", "hold", "recommend", "recommendation",
    "position", "catch up", "current positioning"
]

def analyze_sentiment(text: str) -> Dict:
    """
    Analyze newsletter text for sentiment across dimensions.

    Returns:
        dict: Sentiment scores and key phrases
    """
    text_lower = text.lower()

    # Detect explicit bias statements from AgResource (AUTHORITATIVE)
    # These should dominate sentiment determination
    explicit_bias_keywords = {
        "bullish": [
            "bullish bias", "bullish bias maintained", "bullish outlook",
            "favorable bias", "positive bias"
        ],
        "bearish": [
            "bearish bias", "bearish bias maintained", "bearish outlook",
            "negative bias", "unfavorable bias"
        ]
    }

    explicit_bullish = [kw for kw in explicit_bias_keywords["bullish"] if kw in text_lower]
    explicit_bearish = [kw for kw in explicit_bias_keywords["bearish"] if kw in text_lower]

    # If explicit bias exists, it dominates (weight 100x vs keyword count)
    # This ensures AgResource's stated bias always wins over scattered keywords
    if explicit_bullish and not explicit_bearish:
        market_mood = "bullish"
        bias_source = explicit_bullish[0]
    elif explicit_bearish and not explicit_bullish:
        market_mood = "bearish"
        bias_source = explicit_bearish[0]
    elif explicit_bullish and explicit_bearish:
        # Conflicting explicit statements - use whichever appears more or later
        # For now, take the last mentioned
        last_bullish = max(text_lower.find(kw) for kw in explicit_bullish)
        last_bearish = max(text_lower.find(kw) for kw in explicit_bearish)
        if last_bearish > last_bullish:
            market_mood = "bearish"
            bias_source = explicit_bearish[0]
        else:
            market_mood = "bullish"
            bias_source = explicit_bullish[0]
    else:
        # No explicit bias - fall back to keyword counting
        bullish_count = sum(1 for kw in BULLISH_KEYWORDS if kw in text_lower)
        bearish_count = sum(1 for kw in BEARISH_KEYWORDS if kw in text_lower)

        bullish_total = bullish_count
        bearish_total = bearish_count

        if bullish_total > bearish_total + 2:
            market_mood = "bullish"
            bias_source = "keyword analysis"
        elif bearish_total > bullish_total + 1:
            market_mood = "bearish"
            bias_source = "keyword analysis"
        else:
            market_mood = "neutral"
            bias_source = "keyword analysis"

    # Detect weather impact on PRODUCTION (not prices)
    # This tracks what the weather means for crops, NOT for prices
    weather_pos = sum(1 for kw in WEATHER_POSITIVE_FOR_CROPS if kw in text_lower)
    weather_neg = sum(1 for kw in WEATHER_NEGATIVE_FOR_CROPS if kw in text_lower)

    if weather_pos > weather_neg:
        weather_impact = "positive_for_crops"  # Good for crops = BEARISH for prices
    elif weather_neg > weather_pos:
        weather_impact = "negative_for_crops"  # Bad for crops = BULLISH for prices
    elif weather_pos > 0 or weather_neg > 0:
        weather_impact = "mixed"
    else:
        weather_impact = "neutral"

    # Detect production outlook (PRICE IMPACT)
    # Optimistic production = more supply = BEARISH for prices
    # Cautious production = potential supply issues = BULLISH for prices
    optimistic_words = ["optimistic", "positive", "improving", "good"]
    cautious_words = ["cautious", "concerns", "uncertain", "wait"]

    opt_count = sum(1 for w in optimistic_words if w in text_lower)
    ca_count = sum(1 for w in cautious_words if w in text_lower)

    # Note: optimistic production outlook = bearish for prices
    # We'll track the production outlook separately from price sentiment
    if opt_count > ca_count:
        production_outlook = "optimistic"  # More supply = BEARISH price implication
    elif ca_count > opt_count:
        production_outlook = "cautious"  # Supply concerns = BULLISH price implication
    else:
        production_outlook = "uncertain"

    # Extract key phrases (order by position in text, except explicit bias goes first)
    key_phrases = []

    # Add explicit bias statement first if found
    if explicit_bullish or explicit_bearish:
        bias_phrases = explicit_bullish if explicit_bullish else explicit_bearish
        for bp in bias_phrases:
            if bp not in key_phrases:
                key_phrases.append(bp)

    # Add other phrases, ordered by their position in text
    phrase_positions = []
    for kw in BULLISH_KEYWORDS + BEARISH_KEYWORDS:
        if kw in text_lower and kw not in key_phrases:  # Don't duplicate bias statements
            pos = text_lower.find(kw)
            phrase_positions.append((pos, kw))

    # Sort by position and extract phrases
    phrase_positions.sort(key=lambda x: x[0])
    for pos, kw in phrase_positions:
        key_phrases.append(kw)

    # Detect sales advice
    if "catch up" in text_lower:
        sales_advice = "Catch up sales recommended"
    elif "no sales recommended" in text_lower or "hold" in text_lower:
        sales_advice = "No sales recommended at this time"
    elif "buy" in text_lower or "sell" in text_lower or "recommend" in text_lower:
        sales_advice = "New sales advice detected"
    else:
        sales_advice = "Position status unchanged"

    # Determine confidence based on unique signals
    unique_bullish = len(set(kw for kw in BULLISH_KEYWORDS if kw in text_lower))
    unique_bearish = len(set(kw for kw in BEARISH_KEYWORDS if kw in text_lower))
    unique_weather = len(set(kw for kw in WEATHER_POSITIVE_FOR_CROPS + WEATHER_NEGATIVE_FOR_CROPS if kw in text_lower))
    unique_production = len(set(w for w in optimistic_words + cautious_words if w in text_lower))

    total_unique_signals = unique_bullish + unique_bearish + unique_weather + unique_production
    if total_unique_signals >= 8:
        confidence = "high"
    elif total_unique_signals >= 5:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "market_mood": market_mood,
        "weather_impact": weather_impact,
        "production_outlook": production_outlook,
        "sales_advice": sales_advice,
        "key_phrases": key_phrases,
        "confidence": confidence,
        "bias_source": bias_source  # What determined the sentiment
    }

def compare_to_history(current_sentiment: Dict) -> Dict:
    """
    Compare current sentiment to historical data to detect trends.

    Returns:
        dict: Trend analysis including previous mood and direction
    """
    # Load sentiment history
    if not SENTIMENT_FILE.exists():
        return {
            "trend_direction": "stable",
            "previous_mood": None,
            "confidence": "low"
        }

    with open(SENTIMENT_FILE, 'r') as f:
        data = json.load(f)

    history = data.get("sentiment_history", [])

    if not history:
        return {
            "trend_direction": "stable",
            "previous_mood": None,
            "confidence": "low"
        }

    # Get last few entries for trend analysis
    recent = history[-5:] if len(history) >= 5 else history
    if not recent:
        return {
            "trend_direction": "stable",
            "previous_mood": None,
            "confidence": "low"
        }

    previous_mood = recent[-1].get("market_mood", "neutral")

    # Count mood distribution in recent history
    bullish_count = sum(1 for s in recent if s.get("market_mood") == "bullish")
    bearish_count = sum(1 for s in recent if s.get("market_mood") == "bearish")

    # Determine trend direction
    if current_sentiment["market_mood"] == "bullish" and previous_mood == "bearish":
        trend_direction = "improving"
    elif current_sentiment["market_mood"] == "bearish" and previous_mood == "bullish":
        trend_direction = "declining"
    elif bullish_count > bearish_count + 2:
        trend_direction = "improving"
    elif bearish_count > bullish_count + 2:
        trend_direction = "declining"
    else:
        trend_direction = "stable"

    return {
        "trend_direction": trend_direction,
        "previous_mood": previous_mood,
        "confidence": current_sentiment.get("confidence", "low")
    }

def detect_sales_advice_change(current_sales_advice: str) -> Dict:
    """
    Compare current sales advice to previous to detect changes.

    Returns:
        dict: Change status and alert needed flag
    """
    if not SENTIMENT_FILE.exists():
        return {"changed": False, "alert_needed": False, "previous": None}

    with open(SENTIMENT_FILE, 'r') as f:
        data = json.load(f)

    history = data.get("sentiment_history", [])
    if not history:
        return {"changed": False, "alert_needed": False, "previous": None}

    previous_advice = history[-1].get("sales_advice", "No data")

    # Normalize for comparison
    current_normalized = normalize_sales_advice(current_sales_advice)
    previous_normalized = normalize_sales_advice(previous_advice)

    changed = current_normalized != previous_normalized

    # Alert only on NEW advice or CHANGE from previous
    alert_needed = (
        "New sales advice" in current_sales_advice or
        ("New sales advice" in previous_advice and current_sales_advice != previous_advice) or
        ("New sales advice" in current_sales_advice and "no sales recommended" in previous_advice.lower())
    )

    return {
        "changed": changed,
        "alert_needed": alert_needed,
        "previous": previous_advice
    }

def normalize_sales_advice(advice: str) -> str:
    """Normalize sales advice text for comparison."""
    advice_lower = advice.lower()
    if "catch up" in advice_lower:
        return "catch_up"
    elif "no sales recommended" in advice_lower:
        return "none"
    elif "buy" in advice_lower or "sell" in advice_lower:
        return "action"
    else:
        return "unchanged"

def format_telegram_alert(sentiment: Dict, trend: Dict, newsletter: Dict) -> str:
    """
    Format Telegram alert with key information.

    Returns:
        str: Formatted alert message
    """
    emoji = "🌾"
    timestamp = newsletter.get("timestamp", datetime.now().strftime("%Y-%m-%d %I:%M %p"))
    summary = sentiment.get("sales_advice", "No data")

    mood = sentiment.get("market_mood", "neutral").capitalize()
    direction = trend.get("trend_direction", "stable")

    # Trend emoji
    trend_emoji = {
        "improving": "↗️",
        "declining": "↘️",
        "stable": "➡️"
    }.get(direction, "➡️")

    alert = f"{emoji} AgResource - {timestamp}\n\n"
    alert += f"Summary: {summary}\n"
    alert += f"Sentiment: {mood} ({trend_emoji} {direction})\n\n"
    alert += f"Full details in ~/clawd/memory/agresource/"

    return alert

def analyze_full_newsletter(text: str, newsletter_metadata: Dict) -> Dict:
    """
    Full analysis pipeline: sentiment + trend + alert.

    Returns:
        dict: Complete analysis including alert message
    """
    # Analyze sentiment
    sentiment = analyze_sentiment(text)

    # Compare to history
    trend = compare_to_history(sentiment)

    # Check for sales advice changes
    sales_change = detect_sales_advice_change(sentiment["sales_advice"])

    # Build complete sentiment data (merge sentiment with trend, but keep sentiment confidence)
    complete_sentiment = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": newsletter_metadata.get("time", "08:30 AM"),
        **sentiment,
        **{k: v for k, v in trend.items() if k != "confidence"}  # Don't overwrite confidence
    }

    # Format Telegram alert
    telegram_alert = format_telegram_alert(sentiment, trend, newsletter_metadata)

    return {
        "sentiment": complete_sentiment,
        "trend": trend,
        "sales_change": sales_change,
        "telegram_alert": telegram_alert
    }

if __name__ == "__main__":
    # Test with sample text
    sample_text = "Prices are advancing due to strong export demand. Favorable weather in the Midwest is improving yield potential."

    result = analyze_full_newsletter(sample_text, {"timestamp": "2026-01-08 8:30 AM"})
    print(json.dumps(result, indent=2))
