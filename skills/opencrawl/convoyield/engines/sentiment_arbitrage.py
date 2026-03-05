"""
Sentiment Arbitrage Engine — The money-making core of ConvoYield.

In financial markets, arbitrage exploits price differences across markets.
In conversations, Sentiment Arbitrage exploits EMOTIONAL GAPS — moments where
the user's emotional state creates a revenue opportunity.

Example: A user says "I'm so frustrated with [competitor]"
    -> Frustration with a competitor = MASSIVE opportunity to position your product
    -> The "sentiment gap" between their pain and your solution IS the arbitrage
    -> A bot without this skill would just say "I'm sorry to hear that"
    -> A bot WITH this skill says "I completely understand. Here's how we solve
       exactly that problem, and we can get you set up in 5 minutes."

This engine runs on ZERO external APIs — pure regex + heuristic scoring.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from convoyield.models.conversation import ConversationState, Turn, Speaker
from convoyield.models.yield_result import ArbitrageOpportunity


# ── Sentiment Lexicon (zero-cost, no API needed) ─────────────────────────────
# Scored from -1.0 (extremely negative) to +1.0 (extremely positive)
# These are tuned for COMMERCIAL conversations specifically.

_POSITIVE_MARKERS = {
    # High-value positive signals
    "love": 0.8, "amazing": 0.8, "perfect": 0.9, "excellent": 0.8,
    "fantastic": 0.8, "awesome": 0.7, "great": 0.6, "wonderful": 0.8,
    "impressed": 0.7, "incredible": 0.8, "outstanding": 0.8,
    # Medium positive
    "good": 0.4, "nice": 0.4, "helpful": 0.5, "thanks": 0.3,
    "thank you": 0.4, "appreciate": 0.5, "glad": 0.5, "happy": 0.6,
    "pleased": 0.5, "satisfied": 0.5, "enjoy": 0.5, "like": 0.3,
    # Interest signals (these are GOLD for revenue)
    "interested": 0.6, "curious": 0.5, "tell me more": 0.7,
    "how does it work": 0.7, "sign me up": 0.9, "let's do it": 0.9,
    "sounds good": 0.6, "i'm in": 0.8, "deal": 0.7,
    "when can i start": 0.9, "where do i sign": 0.95,
}

_NEGATIVE_MARKERS = {
    # Frustration (HIGH arbitrage potential)
    "frustrated": -0.7, "annoying": -0.6, "annoyed": -0.6,
    "hate": -0.8, "terrible": -0.8, "awful": -0.8, "worst": -0.9,
    "horrible": -0.8, "disgusting": -0.7, "pathetic": -0.8,
    "useless": -0.7, "broken": -0.6, "doesn't work": -0.7,
    "waste of time": -0.8, "waste of money": -0.9, "scam": -0.9,
    # Disappointment (medium arbitrage)
    "disappointed": -0.6, "let down": -0.6, "expected more": -0.5,
    "not what i wanted": -0.5, "meh": -0.3, "underwhelming": -0.5,
    "mediocre": -0.4, "subpar": -0.5,
    # Confusion / Uncertainty (opportunity to anchor)
    "confused": -0.3, "don't understand": -0.3, "makes no sense": -0.4,
    "complicated": -0.3, "overwhelmed": -0.4, "lost": -0.3,
    # Urgency / Stress (premium positioning opportunity)
    "urgent": -0.4, "asap": -0.4, "emergency": -0.5, "deadline": -0.4,
    "running out of time": -0.5, "need this now": -0.4, "desperate": -0.6,
    # Cost concern (discount / value-stack opportunity)
    "expensive": -0.4, "too much": -0.4, "can't afford": -0.5,
    "overpriced": -0.5, "not worth": -0.6, "rip off": -0.7,
}

# ── Arbitrage Pattern Definitions ─────────────────────────────────────────────

@dataclass
class _ArbitragePattern:
    name: str
    patterns: list[str]          # Regex patterns
    base_value: float            # Base dollar value of the opportunity
    recommended_action: str
    urgency: float               # 0-1
    window_seconds: float        # How long the opportunity lasts


_ARBITRAGE_PATTERNS = [
    _ArbitragePattern(
        name="competitor_displacement",
        patterns=[
            r"\b(frustrat|annoy|hate|sick of|tired of|fed up).{0,30}(current|existing|other|their)\b",
            r"\b(switch|switching|migrate|moving) from\b",
            r"\b(competitor|alternative|other (provider|service|platform|tool))\b",
            r"\b(looking for (something|an?) (better|new|different))\b",
            r"\bused to use\b",
        ],
        base_value=45.0,
        recommended_action="Position as the solution to their specific pain. Mirror their exact complaint and show how you solve it. Offer immediate onboarding.",
        urgency=0.9,
        window_seconds=120.0,
    ),
    _ArbitragePattern(
        name="frustration_capture",
        patterns=[
            r"\b(frustrated|angry|furious|pissed|mad)\b",
            r"\b(doesn't work|not working|broken|keeps crashing)\b",
            r"\b(wast(e|ed|ing) (my |of )?(time|money))\b",
            r"\b(can't believe|unacceptable|ridiculous)\b",
        ],
        base_value=30.0,
        recommended_action="Lead with empathy, then pivot to solution. Frustrated users who feel heard become the most loyal customers.",
        urgency=0.95,
        window_seconds=60.0,
    ),
    _ArbitragePattern(
        name="excitement_amplification",
        patterns=[
            r"\b(love|amazing|awesome|incredible|wow)\b",
            r"\b(exactly what i (need|want))\b",
            r"\b(this is (perfect|great|exactly))\b",
            r"\b(!{2,})\b",
        ],
        base_value=35.0,
        recommended_action="Ride the dopamine wave. Upsell, cross-sell, or ask for a referral while emotional high is peaking.",
        urgency=0.7,
        window_seconds=180.0,
    ),
    _ArbitragePattern(
        name="uncertainty_anchoring",
        patterns=[
            r"\b(not sure|don't know|maybe|possibly|might)\b",
            r"\b(confused|overwhelmed|too many (options|choices))\b",
            r"\b(which (one|plan|option) (should|do|would))\b",
            r"\b(help me (decide|choose|pick))\b",
        ],
        base_value=25.0,
        recommended_action="Anchor them to your highest-margin option first. Reduce cognitive load by recommending ONE clear path. Uncertain users who receive clear guidance convert at 3x the rate.",
        urgency=0.6,
        window_seconds=300.0,
    ),
    _ArbitragePattern(
        name="urgency_premium",
        patterns=[
            r"\b(urgent|asap|emergency|right now|immediately)\b",
            r"\b(deadline|due (date|tomorrow|today|tonight))\b",
            r"\b(running out of time|last minute|crunch)\b",
            r"\b(need this (done|fixed|ready) (by|before|asap))\b",
        ],
        base_value=55.0,
        recommended_action="Users in a rush will pay premium for speed. Position premium/express options. Remove ALL friction from the conversion path.",
        urgency=1.0,
        window_seconds=30.0,
    ),
    _ArbitragePattern(
        name="social_proof_hunger",
        patterns=[
            r"\b(anyone (else|using)|do (others|people|companies))\b",
            r"\b(review|testimonial|case stud(y|ies))\b",
            r"\b(how many (users|customers|people))\b",
            r"\b(is (it|this) (legit|real|trustworthy|reliable))\b",
        ],
        base_value=20.0,
        recommended_action="They're looking for social validation. Deploy social proof: user counts, logos, testimonials, case studies. This is the tipping point — they WANT to buy but need permission.",
        urgency=0.5,
        window_seconds=600.0,
    ),
    _ArbitragePattern(
        name="budget_value_stack",
        patterns=[
            r"\b(expensive|cost|price|budget|afford)\b",
            r"\b(too much|cheaper|discount|coupon|deal)\b",
            r"\b(free (trial|version|tier|plan))\b",
            r"\b(worth (it|the (price|money|cost)))\b",
            r"\b(roi|return on investment|pay for itself)\b",
        ],
        base_value=40.0,
        recommended_action="Don't drop price — STACK value. Show ROI calculation. Reframe cost as investment. Offer payment plans. Only discount as absolute last resort with a time limit.",
        urgency=0.8,
        window_seconds=240.0,
    ),
]


class SentimentArbitrage:
    """
    Detects emotional gaps in conversations and identifies revenue opportunities.

    Zero external dependencies. Runs on pure pattern matching and heuristic scoring.
    """

    def __init__(self, custom_patterns: Optional[list[_ArbitragePattern]] = None):
        self._patterns = _ARBITRAGE_PATTERNS + (custom_patterns or [])
        self._compiled = [
            (p, [re.compile(r, re.IGNORECASE) for r in p.patterns])
            for p in self._patterns
        ]

    def score_sentiment(self, text: str) -> float:
        """
        Score the sentiment of a text from -1.0 to +1.0.
        Uses a weighted lexicon approach — zero cost, no API.
        """
        if not text:
            return 0.0

        lower = text.lower()
        scores = []

        for phrase, score in _POSITIVE_MARKERS.items():
            if phrase in lower:
                scores.append(score)

        for phrase, score in _NEGATIVE_MARKERS.items():
            if phrase in lower:
                scores.append(score)

        # Amplifiers based on punctuation and casing
        excl_count = text.count("!")
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, sum(1 for c in text if c.isalpha()))

        if not scores:
            # No lexicon hit — use structural signals
            if caps_ratio > 0.5 and len(text) > 10:
                return -0.2  # ALL CAPS usually means frustration
            if excl_count >= 3:
                return 0.1   # Multiple exclamation could be excitement
            return 0.0

        base = sum(scores) / len(scores)

        # Amplify based on intensity signals
        if caps_ratio > 0.4:
            base *= 1.3  # CAPS = stronger emotion
        if excl_count >= 2:
            base *= 1.15

        return max(-1.0, min(1.0, base))

    def detect_arbitrage(self, state: ConversationState) -> list[ArbitrageOpportunity]:
        """
        Scan the conversation for arbitrage opportunities.

        Returns opportunities sorted by estimated value (highest first).
        """
        if not state.turns:
            return []

        last_user = state.last_user_turn
        if not last_user:
            return []

        text = last_user.text
        opportunities = []

        for pattern_def, compiled_regexes in self._compiled:
            match_count = 0
            trigger = ""

            for regex in compiled_regexes:
                m = regex.search(text)
                if m:
                    match_count += 1
                    if not trigger:
                        trigger = m.group(0)

            if match_count == 0:
                continue

            # Confidence scales with number of pattern matches
            confidence = min(1.0, 0.4 + (match_count * 0.2))

            # Value scales with conversation engagement (longer convos = more invested users)
            engagement_multiplier = min(2.0, 1.0 + (state.turn_count * 0.1))

            # Recent context: check if sentiment has been trending in a useful direction
            sentiment_now = self.score_sentiment(text)
            sentiment_boost = 1.0
            if len(state.sentiment_history) >= 2:
                trend = sentiment_now - state.sentiment_history[-2]
                if trend < -0.2:
                    # Sentiment is DROPPING — urgency increases, opportunity grows
                    sentiment_boost = 1.4
                elif trend > 0.3:
                    # Sentiment is RISING — ride the wave
                    sentiment_boost = 1.2

            estimated_value = (
                pattern_def.base_value
                * confidence
                * engagement_multiplier
                * sentiment_boost
            )

            opportunities.append(ArbitrageOpportunity(
                type=pattern_def.name,
                confidence=round(confidence, 2),
                estimated_value=round(estimated_value, 2),
                trigger_phrase=trigger,
                recommended_action=pattern_def.recommended_action,
                urgency=pattern_def.urgency,
                window_seconds=pattern_def.window_seconds,
            ))

        # Sort by value — highest opportunity first
        opportunities.sort(key=lambda o: o.estimated_value * o.confidence, reverse=True)
        return opportunities

    def get_sentiment_with_context(self, state: ConversationState) -> tuple[float, float]:
        """
        Returns (current_sentiment, sentiment_delta).

        The delta is what matters for arbitrage — sudden shifts create opportunities.
        """
        if not state.last_user_turn:
            return 0.0, 0.0

        current = self.score_sentiment(state.last_user_turn.text)

        if not state.sentiment_history:
            return current, 0.0

        previous = state.sentiment_history[-1]
        delta = current - previous

        return current, delta
