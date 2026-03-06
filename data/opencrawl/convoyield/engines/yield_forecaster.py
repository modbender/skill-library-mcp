"""
Yield Forecaster — Predict the total dollar value of the conversation.

Like a financial yield calculator, this engine estimates the total revenue
potential of the current conversation based on:

1. Detected micro-conversions (realized + unrealized)
2. Arbitrage opportunities
3. Conversation phase (later phases = more value)
4. User engagement signals
5. Historical conversion probability by pattern

Every bot operator can now see a LIVE dollar amount for each conversation,
which fundamentally changes how they prioritize and allocate resources.

Imagine a customer support dashboard where each active chat shows:
    "Estimated Value: $127.50 | Captured: $35.00 | At Risk: $92.50"

THAT changes behavior. THAT makes money.
"""

from __future__ import annotations

import math
from typing import Optional

from convoyield.models.conversation import ConversationState, ConversationPhase, Speaker
from convoyield.models.yield_result import (
    ArbitrageOpportunity,
    MicroConversion,
)


# ── Phase Value Multipliers ───────────────────────────────────────────────────
# Later phases carry more value because the user is more invested.

_PHASE_MULTIPLIERS = {
    ConversationPhase.OPENING: 0.6,
    ConversationPhase.DISCOVERY: 0.8,
    ConversationPhase.ENGAGEMENT: 1.0,
    ConversationPhase.NEGOTIATION: 1.5,   # Negotiation = they want to buy
    ConversationPhase.CLOSING: 1.2,
    ConversationPhase.POST_CLOSE: 0.7,    # Upsell territory
}

# ── Engagement Score Weights ──────────────────────────────────────────────────

_ENGAGEMENT_WEIGHTS = {
    "turn_count": 0.15,
    "avg_message_length": 0.20,
    "question_rate": 0.20,
    "response_consistency": 0.15,
    "emotional_investment": 0.30,
}


class YieldForecaster:
    """
    Predicts the total dollar value of a conversation in real-time.

    Updates with every message. Gives your bot a financial perspective
    on every interaction.
    """

    def __init__(self, base_conversation_value: float = 15.0):
        self._base_value = base_conversation_value

    def forecast(
        self,
        state: ConversationState,
        arbitrage_ops: list[ArbitrageOpportunity],
        micro_conversions: list[MicroConversion],
        momentum: float,
        sentiment: float,
    ) -> float:
        """
        Calculate the estimated total yield of the conversation.

        Returns a dollar amount representing the predicted total value.
        """
        # 1. Base value adjusted by conversation phase
        phase_mult = _PHASE_MULTIPLIERS.get(state.phase, 1.0)
        base = self._base_value * phase_mult

        # 2. Micro-conversion value (realized + potential)
        mc_realized = sum(mc.value for mc in micro_conversions if mc.captured)
        mc_potential = sum(mc.value for mc in micro_conversions if not mc.captured)
        # Potential value is discounted by capture probability
        mc_total = mc_realized + (mc_potential * self._capture_probability(state, momentum))

        # 3. Arbitrage value (weighted by confidence)
        arb_value = sum(
            op.estimated_value * op.confidence
            for op in arbitrage_ops
        )

        # 4. Engagement premium — more engaged users are worth more
        engagement = self._engagement_score(state)
        engagement_premium = base * engagement * 0.5

        # 5. Momentum premium — positive momentum compounds value
        momentum_premium = 0.0
        if momentum > 0:
            # Positive momentum compounds: each 0.1 of momentum adds ~10% value
            momentum_premium = base * (momentum * 0.5)
        elif momentum < -0.3:
            # Negative momentum risks value loss
            momentum_premium = base * (momentum * 0.3)  # Negative value

        # 6. Sentiment modifier
        sentiment_mod = 1.0
        if sentiment > 0.3:
            sentiment_mod = 1.0 + (sentiment * 0.3)  # Positive sentiment = value boost
        elif sentiment < -0.3:
            sentiment_mod = max(0.5, 1.0 + (sentiment * 0.2))  # Negative = value risk

        total = (base + mc_total + arb_value + engagement_premium + momentum_premium) * sentiment_mod

        return max(0.0, round(total, 2))

    def _capture_probability(self, state: ConversationState, momentum: float) -> float:
        """
        Estimate the probability of capturing uncaptured micro-conversions.

        Higher engagement and momentum = higher capture probability.
        """
        base_prob = 0.3  # Base 30% capture rate

        # More turns = user is more invested
        turn_bonus = min(0.2, state.turn_count * 0.02)

        # Positive momentum increases capture probability
        momentum_bonus = max(0.0, momentum * 0.15)

        # Negotiation phase has highest capture rate
        if state.phase == ConversationPhase.NEGOTIATION:
            phase_bonus = 0.25
        elif state.phase == ConversationPhase.ENGAGEMENT:
            phase_bonus = 0.1
        else:
            phase_bonus = 0.0

        return min(0.85, base_prob + turn_bonus + momentum_bonus + phase_bonus)

    def _engagement_score(self, state: ConversationState) -> float:
        """
        Calculate overall user engagement from 0.0 to 1.0.

        Uses multiple zero-cost signals.
        """
        if not state.user_turns:
            return 0.0

        scores = {}

        # Turn count (more turns = more engaged, diminishing returns)
        scores["turn_count"] = min(1.0, math.log1p(state.turn_count) / 3.0)

        # Average message length (longer = more invested)
        avg_len = state.avg_user_message_length
        scores["avg_message_length"] = min(1.0, avg_len / 30.0)

        # Question rate (questions = interest)
        user_turns = state.user_turns
        if user_turns:
            q_rate = sum(1 for t in user_turns if t.has_question) / len(user_turns)
            scores["question_rate"] = q_rate
        else:
            scores["question_rate"] = 0.0

        # Response consistency (answering bot questions = engaged)
        scores["response_consistency"] = min(1.0, len(state.user_turns) / max(1, len(state.bot_turns)))

        # Emotional investment (any strong emotion = deeply engaged)
        if state.sentiment_history:
            max_intensity = max(abs(s) for s in state.sentiment_history)
            scores["emotional_investment"] = max_intensity
        else:
            scores["emotional_investment"] = 0.0

        # Weighted average
        total = sum(
            scores.get(key, 0.0) * weight
            for key, weight in _ENGAGEMENT_WEIGHTS.items()
        )

        return min(1.0, total)

    def calculate_risk(
        self,
        state: ConversationState,
        momentum: float,
        sentiment: float,
    ) -> float:
        """
        Calculate the risk of losing the user (0.0 = safe, 1.0 = about to leave).

        This is critical: a $200 conversation with 0.8 risk is worth only $40 effectively.
        """
        risk = 0.0

        # Negative momentum is the #1 risk signal
        if momentum < 0:
            risk += abs(momentum) * 0.4

        # Negative sentiment adds risk
        if sentiment < 0:
            risk += abs(sentiment) * 0.3

        # Closing phase = inherently higher risk (they might leave)
        if state.phase in (ConversationPhase.CLOSING, ConversationPhase.POST_CLOSE):
            risk += 0.2

        # Very short messages from user = disengagement signal
        if state.last_user_turn and state.last_user_turn.word_count <= 2:
            risk += 0.15

        # Decreasing message lengths = classic disengagement
        user_turns = state.user_turns[-4:]
        if len(user_turns) >= 3:
            lengths = [t.word_count for t in user_turns]
            if all(lengths[i] >= lengths[i + 1] for i in range(len(lengths) - 1)):
                risk += 0.2

        return min(1.0, risk)
