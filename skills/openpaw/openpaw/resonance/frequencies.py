"""
Frequency Computation Layer.

Transforms raw signals into the 4 core conversational frequencies:
  1. Engagement Frequency — Is the user leaning in or pulling away?
  2. Trust Frequency — How much does the user trust the bot?
  3. Decision Frequency — How close to converting/deciding?
  4. Style Match Frequency — How well is bot resonating with user's style?
"""

from __future__ import annotations

from openpaw.models.metrics import FrequencyProfile
from openpaw.resonance.signals import ConversationSignals


class FrequencyComputer:
    """Computes the 4 resonance frequencies from raw signals."""

    def compute(self, signals: ConversationSignals) -> FrequencyProfile:
        return FrequencyProfile(
            engagement=self._compute_engagement(signals),
            trust=self._compute_trust(signals),
            decision=self._compute_decision(signals),
            style_match=self._compute_style_match(signals),
        )

    def _compute_engagement(self, s: ConversationSignals) -> float:
        """Engagement = Are they investing energy in this conversation?"""
        raw = (
            _norm(s.message_length_trajectory) * 0.20    # Growing messages = engaged
            + s.question_density * 0.15                   # Questions = curious
            + s.response_elaboration * 0.25               # Detailed = invested
            + s.topic_persistence * 0.15                  # Staying on topic = focused
            + s.exclamation_energy * 0.10                 # Energy markers
            + _norm(s.positive_sentiment_trend) * 0.15    # Warming up
        )
        return _clamp(raw)

    def _compute_trust(self, s: ConversationSignals) -> float:
        """Trust = Are they opening up and lowering defenses?"""
        positive_trust = (
            s.personal_disclosure * 0.25      # Sharing personal info = trust
            + s.mirror_behavior * 0.20        # Mirroring = rapport
            + _norm(s.positive_sentiment_trend) * 0.15
            + _norm(-s.formality_drift) * 0.10  # Becoming casual = comfortable
        )
        negative_trust = (
            s.hedge_ratio * 0.15              # Hedging = uncertainty
            + s.objection_frequency * 0.15    # Objecting = resistance
        )
        return _clamp(positive_trust - negative_trust + 0.3)  # Base trust of 0.3

    def _compute_decision(self, s: ConversationSignals) -> float:
        """Decision = How close are they to pulling the trigger?"""
        pro_decision = (
            s.commitment_language * 0.30      # "Yes", "let's do it" = ready
            + s.urgency_markers * 0.15        # "Now", "ASAP" = urgent
            + s.action_language * 0.20        # "Do", "start", "make" = action
            + _norm(s.specificity_increase) * 0.10  # Getting specific = narrowing
        )
        anti_decision = (
            s.objection_frequency * 0.15      # "But", "however" = not ready
            + s.hedge_ratio * 0.10            # "Maybe" = uncommitted
        )
        return _clamp(pro_decision - anti_decision)

    def _compute_style_match(self, s: ConversationSignals) -> float:
        """Style Match = Is the bot's style resonating with the user?"""
        return _clamp(
            s.mirror_behavior * 0.35          # Mirroring back = resonating
            + s.response_elaboration * 0.20   # Engaged enough to elaborate
            + _norm(s.positive_sentiment_trend) * 0.20
            + (1.0 - s.volatility) * 0.25     # Stable = good style fit
        )


def _norm(value: float) -> float:
    """Normalize a -1 to 1 value to 0 to 1."""
    return (value + 1.0) / 2.0


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))
