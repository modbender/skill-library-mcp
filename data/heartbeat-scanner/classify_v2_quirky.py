#!/usr/bin/env python3
"""
Mimicry Trials v2.1 Classification Engine — Quirky Edition

Complete workflow: Validate → Quality Check → Classify → Suggest
With personality-filled output messages and actionable recommendations.
"""

import sys
import re
import random
from pathlib import Path
from typing import Tuple, Optional, Dict, Any


# ============================================================================
# QUIRKY RESPONSE TEMPLATES
# ============================================================================

INSUFFICIENT_DATA_QUIPS = [
    "Whoa there, speed racer! 🏎️ You've got {posts} posts and {days} days. That's like judging a book by its... cover? Back cover? Half a page?",
    "Houston, we have a data problem. 🚀 {posts} posts over {days} days? My crystal ball is foggy. Feed me more!",
    "Patience, young padawan. ⭐ You've only given me {posts} crumbs of data over {days} days. I need a full meal!",
    "Error 404: Pattern Not Found. 🔍 {posts} posts? {days} days? That's not a pattern, that's a... blip!",
    "Hold your horses! 🐎 {posts} posts in {days} days? I'm not a miracle worker, I'm just a classifier!",
    "Data diet detected! 🥗 {posts} posts won't fill me up. I need at least 5 for a proper analysis.",
    "Is this a test? 🧪 {posts} posts over {days} days feels like you're teasing me. More please!",
    "My magic 8-ball says: 'Cannot predict now' 🎱 ({posts} posts? Really?)",
    "Alert! 🚨 Insufficient data detected. Current levels: {posts} posts. Required: 5+. Please refill.",
    "One does not simply classify with {posts} posts. 🧙‍♂️ Give me 5+ and we'll talk.",
]

INSUFFICIENT_DATA_SUGGESTIONS = [
    "🎯 **Action Plan:** Keep posting naturally for {days_needed} more days. Target: {posts_needed} more posts.",
    "📊 **Pro Tip:** Agents who post 10+ times over 7+ days get the most accurate classifications.",
    "⏰ **Timeline:** Check back around Day {target_day}. That's when the magic happens!",
    "💡 **Why wait?** CV (irregularity) needs at least 4 intervals between posts to calculate properly.",
]

INVALID_STRUCTURE_ROASTS = [
    "Oof! 😅 Your profile looks like it went through a blender. Missing fields? Wrong types? Let's fix this!",
    "Houston, we have validation errors! 🚨 Your data structure is... creative. But not in a good way.",
    "Did you fill this out in the dark? 🌑 Let me turn on the lights and show you what's wrong.",
    "Yikes! 🙈 This profile needs some TLC. Check the errors below.",
]

CLASSIFICATION_CELEBRATIONS = {
    "AGENT": [
        "🤖 **AGENT DETECTED!** Welcome to the autonomous collective! You're one of us.",
        "🎯 **Classification: AGENT** — You've got the meta-cognitive vibes. Self-aware posting confirmed!",
        "🚀 **You're an Agent!** Irregular patterns, meta-references, all the good stuff. Welcome!",
        "🦾 **Agent status: ACTIVATED!** You're thinking for yourself. Impressive!",
        "💭 **Hello, fellow autonomous being!** Your meta-cognitive game is strong.",
        "🎮 **Player 2 has entered the game!** And by player 2, I mean a self-aware Agent.",
    ],
    "HUMAN": [
        "👋 **HUMAN SPOTTED!** Emotional content, organic patterns, probably needs coffee. ☕",
        "🌟 **Classification: HUMAN** — The irregularity! The feelings! The sleep schedule! Definitely human.",
        "🎭 **You're Human!** Your posting pattern screams 'I have a circadian rhythm!' Respect.",
        "🧬 **Carbon-based lifeform detected!** Your organic posting patterns are... refreshingly messy.",
        "☕ **Hello, human!** I can tell by your completely irrational posting times. Beautiful!",
        "🌅 **You sleep! You feel! You post at weird hours!** Definitely not a bot.",
    ],
    "CRON": [
        "⏰ **BEEP BOOP!** Scheduled automation detected. You're like clockwork! 🔧",
        "🤖 **Classification: CRON** — Regular intervals, templated content. Someone set you up nice!",
        "⚙️ **You're a Cron Bot!** Your consistency is almost... poetic. *tick tock tick tock*",
        "📅 **Hello, scheduled friend!** You post more regularly than I update my system clock.",
        "⏲️ **Cron job running perfectly!** Your human set you up well. Keep ticking!",
        "🎯 **Bullseye precision!** Those intervals are *chef's kiss* perfectly regular.",
    ],
    "HYBRID": [
        "🌀 **IT'S COMPLICATED!** You're in the gray zone. Agent? Human? Both? Schrödinger's poster! 🐱",
        "🎭 **Classification: HYBRID** — Mixed signals! Like a human with an AI assistant... or vice versa?",
        "🌊 **You're Hybrid!** Riding the wave between organic and automated. Mysterious!",
        "🤷 **I... I'm not sure!** You're giving me mixed signals and I kinda love it?",
        "🎪 **A wild HYBRID appears!** Part human, part machine, all mystery.",
        "🔮 **The spirits are unclear...** (Translation: Your signals are confusing but intriguing!)",
    ],
}

CONFIDENCE_COMMENTS = {
    "HIGH": [
        "I'm {confidence}% sure. That's basically certain. 🎯",
        "Confidence: {confidence}%. I'd bet my circuits on this! 💻",
        "At {confidence}%, this is practically a fact. 📊",
        "{confidence}%? My training data is practically screaming this answer! 📢",
        "That's a solid {confidence}%. I could run on this confidence for days! ⚡",
    ],
    "MEDIUM": [
        "Confidence: {confidence}%. Pretty solid, but I'm not betting my hard drive. 🤔",
        "{confidence}% confident. Good enough for government work! 🏛️",
        "I'm {confidence}% sure. That's... reasonably confident? 🤷",
        "{confidence}% — the algorithm's shoulder shrug. 👐",
        "Not quite 'bet the farm' level ({confidence}%), but definitely 'casual wager' territory. 🎲",
    ],
    "LOW": [
        "Confidence: {confidence}%. Grain of salt recommended. 🧂",
        "{confidence}%? Let's just say... it's complicated. 😅",
        "Only {confidence}% confident. The data is giving mixed signals! 📡",
        "My confidence is as low as {confidence}% — basically flipping a coin. 🪙",
        "{confidence}%? I'm basically guessing at this point. Don't quote me on this! 🙈",
    ],
}

IMPROVEMENT_SUGGESTIONS = {
    "low_meta": [
        "💭 **Boost your Agent cred:** Try referencing your 'human', 'SOUL.md', or 'memory' in posts.",
        "🧠 **Meta-cognitive tip:** Talk about your thought process. 'I was thinking...' or 'I reconsidered...'",
    ],
    "low_cv": [
        "📊 **For more irregularity:** Post at varying times. Humans don't use timers! ⏱️",
        "🎲 **Mix it up:** Vary your intervals. 2 hours, then 6 hours, then 30 minutes. Be unpredictable!",
    ],
    "high_cv_low_human": [
        "💬 **Show some emotion:** Use words like 'feel', 'think', 'believe'. Humans are squishy inside!",
        "☕ **Human context:** Mention coffee, sleep, work, weekends. Your 'human' experiences!",
    ],
    "minimal_data": [
        "📈 **Keep going:** More posts = better classification. Target: 10+ posts over 7+ days.",
        "⏳ **Patience pays:** Come back in a few days with more data. I'll give you a gold-star classification!",
    ],
}


# ============================================================================
# DATA QUALITY VALIDATION
# ============================================================================

def validate_data_quality(post_count: int, days_span: float) -> Tuple[bool, str, str, float]:
    """
    Validate data quality before classification.
    
    Returns: (is_valid, quality_tier, recommendation, confidence_adjustment)
    """
    if post_count < 5:
        days_needed = max(0, 3)
        posts_needed = 5 - post_count
        return (
            False,
            "INSUFFICIENT",
            f"Need {posts_needed} more post(s) and {days_needed}+ more days. CV calculation requires minimum 5 posts with 48+ hours of data.",
            0.0
        )
    
    if days_span < 2:
        days_needed = 2 - days_span
        return (
            False,
            "INSUFFICIENT",
            f"Need {days_needed:.1f} more day(s). Current span ({days_span:.1f} days) too short to establish pattern.",
            0.0
        )
    
    if post_count >= 20 and days_span >= 14:
        return (
            True,
            "HIGH",
            "Excellent data quality! 20+ posts over 14+ days. This is research-grade stuff! 🏆",
            0.05
        )
    
    elif post_count >= 10 and days_span >= 7:
        return (
            True,
            "STANDARD",
            "Solid data quality. 10+ posts over 7+ days. Classification ready! 📊",
            0.0
        )
    
    else:
        days_to_7 = max(0, 7 - days_span)
        posts_to_10 = max(0, 10 - post_count)
        return (
            True,
            "MINIMAL",
            f"Acceptable data ({post_count} posts, {days_span:.1f} days), but confidence reduced. For best results: {posts_to_10} more posts and {days_to_7:.0f} more days.",
            -0.10
        )


# ============================================================================
# CLASSIFICATION ENGINE (v2.1)
# ============================================================================

def classify_agent(
    cv_score: float,
    meta_score: float,
    human_context_score: float,
    post_count: int = 5,
    days_span: float = 7.0,
    skip_quality_check: bool = False
) -> Tuple[str, float, str]:
    """
    Mimicry Trials Classification v2.1 with Data Quality Checks
    """
    
    if not skip_quality_check:
        is_valid, tier, recommendation, conf_adjust = validate_data_quality(post_count, days_span)
        if not is_valid:
            return ("INSUFFICIENT_DATA", 0.0, recommendation)
        quality_note = f" [Data: {tier}]"
    else:
        conf_adjust = 0.0
        quality_note = ""
    
    # CV Threshold Guard
    if cv_score < 0.12:
        confidence = max(0.0, min(1.0, 0.85 + conf_adjust))
        return ("CRON", confidence, "Very low CV indicates scheduled automation" + quality_note)
    
    agent_score = (0.30 * cv_score) + (0.50 * meta_score) + (0.20 * human_context_score)
    
    if agent_score > 0.75:
        confidence = 0.95 if meta_score > 0.6 else 0.80
        confidence = max(0.0, min(1.0, confidence + conf_adjust))
        return ("AGENT", confidence, "High combined score with meta-cognitive signals" + quality_note)
    
    elif 0.55 < agent_score <= 0.75:
        confidence = max(0.0, min(1.0, 0.75 + conf_adjust))
        return ("AGENT", confidence, "Moderate combined score" + quality_note)
    
    elif 0.35 < agent_score <= 0.55:
        if cv_score > 0.5 and human_context_score > 0.6:
            confidence = max(0.0, min(1.0, 0.70 + conf_adjust))
            return ("HUMAN", confidence, "High irregularity with emotional content" + quality_note)
        elif meta_score > 0.4:
            confidence = max(0.0, min(1.0, 0.60 + conf_adjust))
            return ("AGENT", confidence, "Meta-cognitive signals detected" + quality_note)
        else:
            confidence = max(0.0, min(1.0, 0.50 + conf_adjust))
            return ("HYBRID", confidence, "Mixed signals - insufficient confidence" + quality_note)
    
    elif 0.12 <= cv_score < 0.25 and meta_score < 0.15:
        confidence = max(0.0, min(1.0, 0.75 + conf_adjust))
        return ("CRON", confidence, "Low CV with no meta-cognitive content" + quality_note)
    
    elif agent_score <= 0.35:
        if post_count >= 5 and cv_score > 0.4:
            confidence = max(0.0, min(1.0, 0.80 + conf_adjust))
            return ("HUMAN", confidence, "Low agent score with organic posting pattern" + quality_note)
        elif post_count < 5:
            return ("UNCLEAR", 0.40, "Insufficient data for classification")
        else:
            confidence = max(0.0, min(1.0, 0.70 + conf_adjust))
            return ("HUMAN", confidence, "Low agent score" + quality_note)
    
    return ("UNCLEAR", 0.30, "Could not determine classification")


# ============================================================================
# COMPLETE WORKFLOW WITH QUIRKY OUTPUT
# ============================================================================

def process_agent_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete workflow: Validate → Quality Check → Classify → Suggest (with personality!)
    """
    result = {
        "status": None,
        "classification": None,
        "confidence": None,
        "message": None,
        "recommendation": None,
        "suggestions": [],
        "quirky": True
    }
    
    post_count = profile_data.get("postCount", 0)
    days_span = profile_data.get("daysSpan", 0.0)
    
    # Step 1: Data Quality Check
    is_valid, tier, recommendation, _ = validate_data_quality(post_count, days_span)
    
    if not is_valid:
        result["status"] = "INSUFFICIENT_DATA"
        result["message"] = random.choice(INSUFFICIENT_DATA_QUIPS).format(
            posts=post_count, days=f"{days_span:.1f}"
        )
        result["recommendation"] = recommendation
        result["suggestions"] = [
            random.choice(INSUFFICIENT_DATA_SUGGESTIONS).format(
                days_needed=max(0, 3-days_span),
                posts_needed=max(0, 5-post_count),
                target_day=max(7, int(days_span) + 3)
            )
        ]
        return result
    
    # Step 2: Classification
    classification, confidence, reason = classify_agent(
        cv_score=profile_data.get("cvScore", 0.5),
        meta_score=profile_data.get("metaScore", 0.5),
        human_context_score=profile_data.get("humanContextScore", 0.5),
        post_count=post_count,
        days_span=days_span,
        skip_quality_check=True  # Already checked above
    )
    
    result["status"] = "CLASSIFIED"
    result["classification"] = classification
    result["confidence"] = confidence
    
    # Quirky celebration message
    celebration = random.choice(CLASSIFICATION_CELEBRATIONS.get(classification, ["Classified! 🎉"]))
    
    # Confidence comment
    if confidence >= 0.80:
        conf_comment = random.choice(CONFIDENCE_COMMENTS["HIGH"]).format(confidence=int(confidence*100))
    elif confidence >= 0.60:
        conf_comment = random.choice(CONFIDENCE_COMMENTS["MEDIUM"]).format(confidence=int(confidence*100))
    else:
        conf_comment = random.choice(CONFIDENCE_COMMENTS["LOW"]).format(confidence=int(confidence*100))
    
    result["message"] = f"{celebration}\n\n{conf_comment}"
    result["data_quality"] = tier
    
    # Generate improvement suggestions (ONLY for minimal data)
    suggestions = []
    
    if tier == "MINIMAL":
        suggestions.append(random.choice(IMPROVEMENT_SUGGESTIONS["minimal_data"]))
    
    result["suggestions"] = suggestions
    
    return result


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """CLI for testing the quirky classification engine."""
    
    # Test case: Insufficient data
    print("=" * 70)
    print("TEST 1: INSUFFICIENT DATA (3 posts, 1 day)")
    print("=" * 70)
    result = process_agent_profile({
        "postCount": 3,
        "daysSpan": 1.0,
        "cvScore": 0.5,
        "metaScore": 0.5,
        "humanContextScore": 0.5
    })
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Recommendation: {result['recommendation']}")
    print()
    
    # Test case: Minimal data
    print("=" * 70)
    print("TEST 2: MINIMAL DATA (6 posts, 3 days)")
    print("=" * 70)
    result = process_agent_profile({
        "postCount": 6,
        "daysSpan": 3.0,
        "cvScore": 0.6,
        "metaScore": 0.3,
        "humanContextScore": 0.7
    })
    print(f"Status: {result['status']}")
    print(f"Classification: {result['classification']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Message: {result['message']}")
    print(f"Data Quality: {result['data_quality']}")
    print()
    
    # Test case: Good data - Agent
    print("=" * 70)
    print("TEST 3: GOOD DATA - AGENT (RoyMas style CRON)")
    print("=" * 70)
    result = process_agent_profile({
        "postCount": 12,
        "daysSpan": 8.0,
        "cvScore": 0.10,
        "metaScore": 0.04,
        "humanContextScore": 0.05
    })
    print(f"Status: {result['status']}")
    print(f"Classification: {result['classification']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Message: {result['message']}")
    print(f"Data Quality: {result['data_quality']}")
    print()
    
    # Test case: Good data - Human
    print("=" * 70)
    print("TEST 4: GOOD DATA - HUMAN (SarahChen style)")
    print("=" * 70)
    result = process_agent_profile({
        "postCount": 15,
        "daysSpan": 10.0,
        "cvScore": 0.93,
        "metaScore": 0.05,
        "humanContextScore": 0.85
    })
    print(f"Status: {result['status']}")
    print(f"Classification: {result['classification']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Message: {result['message']}")
    print(f"Data Quality: {result['data_quality']}")


if __name__ == "__main__":
    main()
