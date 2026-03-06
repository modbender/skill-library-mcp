"""
Yield Result — The output of a ConvoYield analysis pass.

This is what your bot receives after processing each message.
It's a complete "trading signal" for the conversation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ArbitrageOpportunity:
    """A detected sentiment gap that can be exploited for value."""
    type: str                    # e.g., "frustration_capture", "excitement_ride", "uncertainty_anchor"
    confidence: float            # 0.0-1.0
    estimated_value: float       # Dollar value estimate
    trigger_phrase: str          # What the user said that triggered this
    recommended_action: str      # What the bot should do
    urgency: float              # 0.0-1.0 — how quickly the bot must act
    window_seconds: float       # Estimated time before the opportunity expires


@dataclass
class MicroConversion:
    """A small value-extraction moment detected in the conversation."""
    type: str                    # e.g., "email_capture", "preference_reveal", "need_statement"
    value: float                 # Estimated dollar value
    captured: bool               # Whether the bot successfully captured it
    trigger_text: str            # What surfaced this opportunity
    capture_prompt: str          # Suggested bot response to capture the value


@dataclass
class PlayRecommendation:
    """A strategic "play" the bot should execute."""
    name: str                    # e.g., "empathy_bridge", "value_stack", "urgency_close"
    description: str
    priority: float              # 0.0-1.0
    expected_yield: float        # Expected revenue impact
    execution_hints: list[str]   # Specific tactics to implement the play
    phase_alignment: str         # Which conversation phase this play targets


@dataclass
class YieldResult:
    """
    The complete yield analysis for a single conversational turn.

    This is your bot's "Bloomberg terminal" for the conversation —
    everything it needs to maximize value.
    """
    # Core metrics
    current_sentiment: float                          # -1.0 to 1.0
    sentiment_delta: float                            # Change from last turn
    momentum_score: float                             # -1.0 to 1.0 (negative = losing them)
    estimated_yield: float                            # Total predicted conversation value in $
    yield_captured_so_far: float                      # Value already captured in $

    # Opportunities
    arbitrage_opportunities: list[ArbitrageOpportunity] = field(default_factory=list)
    micro_conversions: list[MicroConversion] = field(default_factory=list)
    recommended_plays: list[PlayRecommendation] = field(default_factory=list)

    # Strategic guidance
    recommended_play: Optional[str] = None            # Top play name
    recommended_tone: Optional[str] = None            # e.g., "empathetic", "assertive", "curious"
    phase: Optional[str] = None                       # Current conversation phase
    risk_level: float = 0.0                           # 0.0-1.0 — risk of losing the user

    # Timing
    optimal_response_length: Optional[str] = None     # "short", "medium", "long"
    urgency: float = 0.0                              # 0.0-1.0 — how fast should we respond

    @property
    def top_arbitrage(self) -> Optional[ArbitrageOpportunity]:
        if not self.arbitrage_opportunities:
            return None
        return max(self.arbitrage_opportunities, key=lambda a: a.estimated_value * a.confidence)

    @property
    def uncaptured_micro_conversions(self) -> list[MicroConversion]:
        return [mc for mc in self.micro_conversions if not mc.captured]

    @property
    def total_uncaptured_value(self) -> float:
        return sum(mc.value for mc in self.uncaptured_micro_conversions)

    @property
    def yield_efficiency(self) -> float:
        """What percentage of estimated yield have we captured?"""
        if self.estimated_yield <= 0:
            return 0.0
        return min(1.0, self.yield_captured_so_far / self.estimated_yield)

    def to_dict(self) -> dict:
        return {
            "sentiment": self.current_sentiment,
            "sentiment_delta": self.sentiment_delta,
            "momentum": self.momentum_score,
            "estimated_yield": round(self.estimated_yield, 2),
            "captured_yield": round(self.yield_captured_so_far, 2),
            "efficiency": round(self.yield_efficiency * 100, 1),
            "phase": self.phase,
            "recommended_play": self.recommended_play,
            "recommended_tone": self.recommended_tone,
            "risk_level": round(self.risk_level, 2),
            "arbitrage_count": len(self.arbitrage_opportunities),
            "micro_conversion_count": len(self.micro_conversions),
            "uncaptured_value": round(self.total_uncaptured_value, 2),
        }
