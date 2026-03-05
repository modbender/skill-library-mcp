"""
Yield Predictor.

Predicts the revenue/conversion yield of a conversation
based on frequencies and signals. Think of it as a financial
yield curve, but for conversations.

This is where the money lives.
"""

from __future__ import annotations

from openpaw.models.metrics import FrequencyProfile, YieldPrediction
from openpaw.resonance.signals import ConversationSignals


class YieldPredictor:
    """Predicts conversation outcome value and optimal timing."""

    def predict(
        self,
        profile: FrequencyProfile,
        signals: ConversationSignals,
        turn_number: int,
    ) -> YieldPrediction:

        conversion_prob = self._compute_conversion_probability(profile, signals)
        value = self._estimate_value(profile, signals)
        optimal_turns = self._estimate_optimal_turns(profile, signals, turn_number)
        risks = self._identify_risks(profile, signals)
        opportunities = self._identify_opportunities(profile, signals)
        action = self._recommend_action(conversion_prob, optimal_turns, profile)

        return YieldPrediction(
            conversion_probability=conversion_prob,
            estimated_value=value,
            optimal_turns_remaining=optimal_turns,
            risk_factors=risks,
            opportunity_factors=opportunities,
            recommended_action=action,
        )

    def _compute_conversion_probability(
        self, profile: FrequencyProfile, signals: ConversationSignals
    ) -> float:
        """Core conversion probability from 0 to 1."""
        # Base probability from composite score
        base = profile.composite

        # Boost from strong decision signals
        if signals.commitment_language > 0.4:
            base += 0.15
        if signals.urgency_markers > 0.3:
            base += 0.10
        if signals.action_language > 0.3:
            base += 0.05

        # Penalty from negative signals
        if signals.objection_frequency > 0.4:
            base -= 0.15
        if signals.hedge_ratio > 0.4:
            base -= 0.10
        if signals.momentum < -0.3:
            base -= 0.10

        # Trust gate — low trust caps conversion probability
        if profile.trust < 0.3:
            base = min(base, 0.3)

        return max(0.0, min(1.0, base))

    def _estimate_value(
        self, profile: FrequencyProfile, signals: ConversationSignals
    ) -> str:
        """Estimate the relative value of this conversion opportunity."""
        score = profile.composite

        # High urgency + high engagement = premium opportunity
        if signals.urgency_markers > 0.3 and profile.engagement > 0.6:
            score += 0.2

        # Detailed, specific engagement = higher value customer
        if signals.response_elaboration > 0.6 and signals.specificity_increase > 0.3:
            score += 0.15

        if score >= 0.75:
            return "very_high"
        elif score >= 0.55:
            return "high"
        elif score >= 0.35:
            return "medium"
        else:
            return "low"

    def _estimate_optimal_turns(
        self,
        profile: FrequencyProfile,
        signals: ConversationSignals,
        turn_number: int,
    ) -> int:
        """How many more turns before the optimal closing window."""
        if profile.decision >= 0.7 and profile.trust >= 0.5:
            return 0  # Close now

        if profile.decision >= 0.5:
            return 1  # One more turn

        trust_gap = max(0, 0.5 - profile.trust)
        decision_gap = max(0, 0.7 - profile.decision)
        gap = max(trust_gap, decision_gap)

        # Estimate ~2 turns per 0.2 gap
        estimated = int(gap / 0.1)

        # If momentum is positive, fewer turns needed
        if signals.momentum > 0.3:
            estimated = max(0, estimated - 1)

        # If momentum is negative, more turns needed
        if signals.momentum < -0.3:
            estimated += 2

        return min(estimated, 10)  # Cap at 10

    def _identify_risks(
        self, profile: FrequencyProfile, signals: ConversationSignals
    ) -> list[str]:
        """Identify factors that could kill the conversion."""
        risks = []

        if signals.message_length_trajectory < -0.5:
            risks.append("User responses are shrinking — losing interest")

        if signals.objection_frequency > 0.4:
            risks.append("High objection frequency — unresolved concerns")

        if signals.hedge_ratio > 0.5:
            risks.append("Heavy hedging language — low commitment confidence")

        if signals.volatility > 0.6:
            risks.append("Emotional volatility — unpredictable engagement")

        if profile.trust < 0.3 and profile.decision > 0.4:
            risks.append("Decision intent without trust — may abandon at last step")

        if signals.momentum < -0.4:
            risks.append("Negative momentum — conversation is dying")

        if signals.positive_sentiment_trend < -0.4:
            risks.append("Sentiment dropping rapidly — user becoming unhappy")

        return risks

    def _identify_opportunities(
        self, profile: FrequencyProfile, signals: ConversationSignals
    ) -> list[str]:
        """Identify factors that create conversion opportunities."""
        opportunities = []

        if signals.commitment_language > 0.3:
            opportunities.append("User using commitment language — decision readiness")

        if signals.urgency_markers > 0.2:
            opportunities.append("Urgency signals detected — time-sensitive need")

        if signals.mirror_behavior > 0.5:
            opportunities.append("Strong mirroring — deep rapport established")

        if signals.personal_disclosure > 0.3:
            opportunities.append("High personal disclosure — trust is building")

        if signals.action_language > 0.3:
            opportunities.append("Action-oriented language — ready to move")

        if signals.momentum > 0.4:
            opportunities.append("Strong positive momentum — ride the wave")

        if profile.engagement > 0.7 and profile.trust > 0.5:
            opportunities.append("High engagement + trust — prime for value delivery")

        return opportunities

    def _recommend_action(
        self,
        conversion_prob: float,
        optimal_turns: int,
        profile: FrequencyProfile,
    ) -> str:
        """Generate the top-level action recommendation."""
        if conversion_prob >= 0.7 and optimal_turns == 0:
            return "CLOSE NOW — Present the offer, CTA, or solution immediately"

        if conversion_prob >= 0.5 and optimal_turns <= 1:
            return (
                "PREPARE TO CLOSE — Set up the offer with one more "
                "value-building exchange"
            )

        if conversion_prob >= 0.3:
            if profile.trust < 0.4:
                return "BUILD TRUST — Focus on credibility, social proof, guarantees"
            return "NURTURE — Continue building engagement and demonstrating value"

        if profile.engagement < 0.3:
            return "RE-ENGAGE — Current approach isn't working, try a new angle"

        return "EXPLORE — Ask questions to understand needs and build connection"
