"""
Momentum Scorer — Is the conversation gaining or losing steam?

Like stock momentum indicators, this engine measures the DIRECTION and
VELOCITY of a conversation. Is the user getting more engaged or pulling away?

This is critical because:
- Positive momentum = push harder, the user is primed for conversion
- Negative momentum = pull back, empathize, re-engage before you lose them
- Neutral momentum = introduce a pattern interrupt to restart engagement

Signals measured (all zero-cost, no API):
- Message length trends (longer messages = more invested)
- Response time trends (faster responses = more engaged)
- Question density (more questions = more interested)
- Emotional intensity (increasing emotion = increasing engagement)
- Word diversity (richer vocabulary = deeper engagement)
"""

from __future__ import annotations

import math
from typing import Optional

from convoyield.models.conversation import ConversationState, Speaker


class MomentumScorer:
    """
    Calculates conversational momentum from -1.0 (hemorrhaging) to +1.0 (on fire).

    Uses zero-cost heuristic signals — no external APIs needed.
    """

    def __init__(self, lookback_window: int = 6):
        self._lookback = lookback_window

    def score(self, state: ConversationState) -> float:
        """
        Calculate the overall momentum score.

        Returns a float from -1.0 to +1.0:
            -1.0 = User is disengaging rapidly
             0.0 = Neutral / stable
            +1.0 = User is extremely engaged and accelerating
        """
        if state.turn_count < 2:
            return 0.0

        signals = [
            self._length_momentum(state),
            self._question_momentum(state),
            self._intensity_momentum(state),
            self._vocabulary_momentum(state),
        ]

        # Weighted average — length and questions matter most
        weights = [0.35, 0.25, 0.20, 0.20]
        weighted_sum = sum(s * w for s, w in zip(signals, weights))

        return max(-1.0, min(1.0, weighted_sum))

    def _length_momentum(self, state: ConversationState) -> float:
        """Are user messages getting longer (more engaged) or shorter (disengaging)?"""
        user_turns = state.user_turns[-self._lookback:]
        if len(user_turns) < 2:
            return 0.0

        lengths = [t.word_count for t in user_turns]
        if len(lengths) < 2:
            return 0.0

        # Calculate trend using simple linear regression slope
        slope = self._trend_slope(lengths)

        # Normalize: a slope of +5 words/turn = strong positive
        return max(-1.0, min(1.0, slope / 5.0))

    def _question_momentum(self, state: ConversationState) -> float:
        """Are users asking more questions? Questions = interest."""
        user_turns = state.user_turns[-self._lookback:]
        if len(user_turns) < 2:
            return 0.0

        questions = [1.0 if t.has_question else 0.0 for t in user_turns]
        mid = len(questions) // 2

        early_avg = sum(questions[:mid]) / max(1, mid)
        late_avg = sum(questions[mid:]) / max(1, len(questions) - mid)

        return max(-1.0, min(1.0, (late_avg - early_avg) * 2.0))

    def _intensity_momentum(self, state: ConversationState) -> float:
        """Is emotional intensity increasing? (Exclamations, caps, punctuation density)."""
        user_turns = state.user_turns[-self._lookback:]
        if len(user_turns) < 2:
            return 0.0

        intensities = [t.exclamation_density + t.caps_ratio for t in user_turns]
        slope = self._trend_slope(intensities)

        return max(-1.0, min(1.0, slope * 10.0))

    def _vocabulary_momentum(self, state: ConversationState) -> float:
        """Is vocabulary getting richer? Richer = deeper engagement."""
        user_turns = state.user_turns[-self._lookback:]
        if len(user_turns) < 2:
            return 0.0

        diversities = []
        for t in user_turns:
            words = t.text.lower().split()
            if not words:
                diversities.append(0.0)
                continue
            unique = len(set(words))
            diversities.append(unique / len(words))

        slope = self._trend_slope(diversities)
        return max(-1.0, min(1.0, slope * 5.0))

    @staticmethod
    def _trend_slope(values: list[float]) -> float:
        """Simple linear regression slope — which direction is the trend going?"""
        n = len(values)
        if n < 2:
            return 0.0

        x_mean = (n - 1) / 2.0
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def get_momentum_label(self, score: float) -> str:
        """Human-readable momentum label."""
        if score >= 0.6:
            return "surging"
        elif score >= 0.3:
            return "accelerating"
        elif score >= 0.1:
            return "building"
        elif score > -0.1:
            return "stable"
        elif score > -0.3:
            return "cooling"
        elif score > -0.6:
            return "declining"
        else:
            return "hemorrhaging"

    def recommend_response_length(self, momentum: float, phase: str) -> str:
        """Based on momentum, how long should the bot's response be?"""
        if momentum > 0.5:
            # User is highly engaged — match their energy
            return "medium"
        elif momentum > 0.1:
            # Positive momentum — keep it focused
            return "medium"
        elif momentum > -0.2:
            # Neutral — add value to re-engage
            return "medium"
        elif momentum > -0.5:
            # Losing them — short and punchy, pattern interrupt
            return "short"
        else:
            # Hemorrhaging — minimal, empathetic, ask one clear question
            return "short"
