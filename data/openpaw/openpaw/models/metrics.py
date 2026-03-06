"""Metrics, scores, and recommendation models for the ResonanceEngine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ResponseStyle(Enum):
    MIRROR = "mirror"           # Match user's style exactly
    CONTRAST = "contrast"       # Deliberately different style
    AMPLIFY = "amplify"         # Intensify current approach
    SOFTEN = "soften"           # Reduce intensity
    REDIRECT = "redirect"       # Change conversational direction


class ActionTiming(Enum):
    NOW = "now"                 # Act immediately
    NEXT_TURN = "next_turn"     # Wait one more exchange
    BUILD_MORE = "build_more"   # Need 2-3 more exchanges
    NOT_READY = "not_ready"     # User is far from ready


class UrgencyLevel(Enum):
    CRITICAL = "critical"       # Act now or lose them
    HIGH = "high"               # Strong signal, act soon
    MEDIUM = "medium"           # Developing, monitor
    LOW = "low"                 # Stable, maintain course


@dataclass
class FrequencyProfile:
    """The 4 core frequencies computed from conversational signals."""

    engagement: float = 0.0     # 0-1: How engaged is the user?
    trust: float = 0.0          # 0-1: How much does the user trust the bot?
    decision: float = 0.0       # 0-1: How close to converting/deciding?
    style_match: float = 0.0    # 0-1: How well is bot matching user's style?

    @property
    def composite(self) -> float:
        """Weighted composite score. Decision is weighted highest for revenue."""
        return (
            self.engagement * 0.25
            + self.trust * 0.30
            + self.decision * 0.30
            + self.style_match * 0.15
        )

    @property
    def resonance_level(self) -> str:
        score = self.composite
        if score >= 0.8:
            return "PEAK_RESONANCE"
        elif score >= 0.6:
            return "HIGH_RESONANCE"
        elif score >= 0.4:
            return "BUILDING"
        elif score >= 0.2:
            return "WEAK"
        else:
            return "NO_RESONANCE"


@dataclass
class ResonanceScore:
    """Overall resonance analysis for a conversation at a point in time."""

    profile: FrequencyProfile
    turn_number: int
    signals: dict = field(default_factory=dict)
    trend: str = "stable"       # "rising", "falling", "stable", "volatile"
    momentum: float = 0.0       # -1 to 1: negative = losing, positive = gaining

    @property
    def composite(self) -> float:
        return self.profile.composite

    @property
    def is_hot(self) -> bool:
        """User is in a high-conversion state."""
        return self.profile.decision >= 0.7 and self.profile.trust >= 0.5


@dataclass
class TuningRecommendation:
    """Specific guidance on how the bot should adjust its next response."""

    style: ResponseStyle
    timing: ActionTiming
    urgency: UrgencyLevel

    # Specific adjustments
    recommended_length: str = "medium"   # "very_short", "short", "medium", "long"
    use_questions: bool = False
    use_social_proof: bool = False
    use_scarcity: bool = False
    use_empathy: bool = False
    address_objection: Optional[str] = None
    mirror_language: bool = False
    confidence_level: str = "balanced"   # "humble", "balanced", "authoritative"

    # The core recommendation in plain language
    reasoning: str = ""
    action: str = ""

    def to_prompt_injection(self) -> str:
        """Generate a prompt fragment a bot can inject into its system prompt."""
        parts = [f"[RESONANCE TUNING] {self.action}"]

        if self.address_objection:
            parts.append(f"Address this concern: {self.address_objection}")

        style_hints = []
        if self.mirror_language:
            style_hints.append("mirror the user's language patterns")
        if self.use_empathy:
            style_hints.append("lead with empathy")
        if self.use_social_proof:
            style_hints.append("include social proof")
        if self.use_scarcity:
            style_hints.append("create appropriate urgency")
        if self.use_questions:
            style_hints.append("ask a focused question")

        if style_hints:
            parts.append("Style: " + ", ".join(style_hints))

        parts.append(f"Response length: {self.recommended_length}")
        parts.append(f"Tone: {self.confidence_level}")

        return " | ".join(parts)


@dataclass
class YieldPrediction:
    """Prediction of conversation outcome value."""

    conversion_probability: float = 0.0   # 0-1
    estimated_value: str = "unknown"      # "low", "medium", "high", "very_high"
    optimal_turns_remaining: int = 0      # Estimated turns to optimal close
    risk_factors: list[str] = field(default_factory=list)
    opportunity_factors: list[str] = field(default_factory=list)
    recommended_action: str = ""

    @property
    def should_close(self) -> bool:
        return self.conversion_probability >= 0.65 and self.optimal_turns_remaining <= 1
