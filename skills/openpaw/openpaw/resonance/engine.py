"""
ResonanceEngine — The Core.

The universal conversational amplifier. Reads invisible micro-signals
in every conversation and tells the bot exactly how to respond for
maximum impact. Zero cost. Zero APIs. Pure signal intelligence.

Usage:
    from openpaw import ResonanceEngine
    from openpaw.models import Conversation, Speaker

    engine = ResonanceEngine()
    convo = Conversation(goal="sale")

    convo.add_bot_message("Hi! How can I help you today?")
    convo.add_user_message("I've been looking at your premium plan...")

    result = engine.analyze(convo)
    print(result.recommendation.action)
    print(result.recommendation.to_prompt_injection())
    print(result.yield_prediction.conversion_probability)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from openpaw.models.conversation import Conversation
from openpaw.models.metrics import (
    FrequencyProfile,
    ResonanceScore,
    TuningRecommendation,
    YieldPrediction,
)
from openpaw.resonance.frequencies import FrequencyComputer
from openpaw.resonance.signals import ConversationSignals, SignalExtractor
from openpaw.resonance.tuner import ResponseTuner
from openpaw.resonance.yield_predictor import YieldPredictor


@dataclass
class ResonanceResult:
    """Complete analysis result from the ResonanceEngine."""

    signals: ConversationSignals
    profile: FrequencyProfile
    score: ResonanceScore
    recommendation: TuningRecommendation
    yield_prediction: YieldPrediction
    turn_number: int

    def summary(self) -> str:
        """Human-readable summary of the analysis."""
        lines = [
            f"=== RESONANCE ANALYSIS (Turn {self.turn_number}) ===",
            f"",
            f"Resonance Level: {self.profile.resonance_level}",
            f"Composite Score: {self.profile.composite:.2f}",
            f"",
            f"  Engagement:   {_bar(self.profile.engagement)} {self.profile.engagement:.2f}",
            f"  Trust:        {_bar(self.profile.trust)} {self.profile.trust:.2f}",
            f"  Decision:     {_bar(self.profile.decision)} {self.profile.decision:.2f}",
            f"  Style Match:  {_bar(self.profile.style_match)} {self.profile.style_match:.2f}",
            f"",
            f"Momentum: {self.signals.momentum:+.2f}  |  Trend: {self.score.trend}",
            f"",
            f"--- ACTION ---",
            f"{self.recommendation.action}",
            f"",
            f"--- YIELD ---",
            f"Conversion Probability: {self.yield_prediction.conversion_probability:.0%}",
            f"Estimated Value: {self.yield_prediction.estimated_value}",
            f"Optimal Turns Remaining: {self.yield_prediction.optimal_turns_remaining}",
        ]

        if self.yield_prediction.risk_factors:
            lines.append("")
            lines.append("Risks:")
            for risk in self.yield_prediction.risk_factors:
                lines.append(f"  ! {risk}")

        if self.yield_prediction.opportunity_factors:
            lines.append("")
            lines.append("Opportunities:")
            for opp in self.yield_prediction.opportunity_factors:
                lines.append(f"  + {opp}")

        lines.append("")
        lines.append(f"--- PROMPT INJECTION ---")
        lines.append(self.recommendation.to_prompt_injection())

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialize to dictionary for API/JSON usage."""
        return {
            "turn_number": self.turn_number,
            "resonance_level": self.profile.resonance_level,
            "composite_score": round(self.profile.composite, 3),
            "frequencies": {
                "engagement": round(self.profile.engagement, 3),
                "trust": round(self.profile.trust, 3),
                "decision": round(self.profile.decision, 3),
                "style_match": round(self.profile.style_match, 3),
            },
            "momentum": round(self.signals.momentum, 3),
            "trend": self.score.trend,
            "is_hot": self.score.is_hot,
            "recommendation": {
                "style": self.recommendation.style.value,
                "timing": self.recommendation.timing.value,
                "urgency": self.recommendation.urgency.value,
                "action": self.recommendation.action,
                "prompt_injection": self.recommendation.to_prompt_injection(),
                "length": self.recommendation.recommended_length,
                "confidence": self.recommendation.confidence_level,
            },
            "yield": {
                "conversion_probability": round(
                    self.yield_prediction.conversion_probability, 3
                ),
                "estimated_value": self.yield_prediction.estimated_value,
                "optimal_turns_remaining": self.yield_prediction.optimal_turns_remaining,
                "should_close": self.yield_prediction.should_close,
                "risks": self.yield_prediction.risk_factors,
                "opportunities": self.yield_prediction.opportunity_factors,
                "action": self.yield_prediction.recommended_action,
            },
            "signals": self.signals.to_dict(),
        }


class ResonanceEngine:
    """
    The ResonanceEngine.

    Analyzes conversations in real-time to compute resonance frequencies
    and generate tuning recommendations that maximize engagement,
    conversion, and revenue.

    Zero external dependencies. Zero API costs. Pure algorithmic intelligence.

    Args:
        history_window: Number of recent results to track for trend analysis.
    """

    def __init__(self, history_window: int = 10):
        self._signal_extractor = SignalExtractor()
        self._frequency_computer = FrequencyComputer()
        self._tuner = ResponseTuner()
        self._yield_predictor = YieldPredictor()
        self._history: list[ResonanceResult] = []
        self._history_window = history_window

    def analyze(self, conversation: Conversation) -> ResonanceResult:
        """
        Analyze the current state of a conversation.

        Call this after each user message to get updated recommendations
        for how the bot should respond.

        Returns a ResonanceResult with frequencies, recommendations,
        and yield predictions.
        """
        # 1. Extract signals
        signals = self._signal_extractor.extract(conversation)

        # 2. Compute frequencies
        profile = self._frequency_computer.compute(signals)

        # 3. Determine trend from history
        trend = self._compute_trend(profile)

        # 4. Build resonance score
        score = ResonanceScore(
            profile=profile,
            turn_number=conversation.turn_count,
            signals=signals.to_dict(),
            trend=trend,
            momentum=signals.momentum,
        )

        # 5. Generate tuning recommendation
        recommendation = self._tuner.tune(profile, signals)

        # 6. Predict yield
        yield_prediction = self._yield_predictor.predict(
            profile, signals, conversation.turn_count
        )

        # 7. Build result
        result = ResonanceResult(
            signals=signals,
            profile=profile,
            score=score,
            recommendation=recommendation,
            yield_prediction=yield_prediction,
            turn_number=conversation.turn_count,
        )

        # 8. Track history
        self._history.append(result)
        if len(self._history) > self._history_window:
            self._history = self._history[-self._history_window:]

        return result

    def reset(self) -> None:
        """Reset the engine's history for a new conversation."""
        self._history.clear()

    @property
    def history(self) -> list[ResonanceResult]:
        """Access the analysis history."""
        return list(self._history)

    @property
    def last_result(self) -> Optional[ResonanceResult]:
        """Get the most recent analysis result."""
        return self._history[-1] if self._history else None

    def _compute_trend(self, current: FrequencyProfile) -> str:
        """Determine if resonance is rising, falling, stable, or volatile."""
        if len(self._history) < 2:
            return "stable"

        recent_scores = [r.profile.composite for r in self._history[-4:]]
        recent_scores.append(current.composite)

        if len(recent_scores) < 3:
            return "stable"

        # Check for volatility
        diffs = [
            abs(recent_scores[i] - recent_scores[i - 1])
            for i in range(1, len(recent_scores))
        ]
        avg_diff = sum(diffs) / len(diffs)
        if avg_diff > 0.15:
            return "volatile"

        # Check direction
        first_half = sum(recent_scores[: len(recent_scores) // 2]) / (
            len(recent_scores) // 2
        )
        second_half = sum(recent_scores[len(recent_scores) // 2:]) / (
            len(recent_scores) - len(recent_scores) // 2
        )

        diff = second_half - first_half
        if diff > 0.05:
            return "rising"
        elif diff < -0.05:
            return "falling"
        else:
            return "stable"


def _bar(value: float, width: int = 20) -> str:
    """Generate a simple ASCII bar for visualization."""
    filled = int(value * width)
    return "[" + "#" * filled + "." * (width - filled) + "]"
