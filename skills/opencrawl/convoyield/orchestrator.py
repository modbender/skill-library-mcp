"""
ConvoYield Orchestrator — The Bloomberg Terminal for Conversations.

This is the main entry point. It wires together all five engines and produces
a unified YieldResult for every message processed.

Usage is dead simple:

    from convoyield import ConvoYield

    engine = ConvoYield()

    # Process each user message
    result = engine.process_user_message("I'm really frustrated with Salesforce")
    print(result.recommended_play)       # "competitor_displacement"
    print(result.estimated_yield)         # 89.50
    print(result.top_arbitrage.type)      # "frustration_capture"

    # Process bot responses to track the full conversation
    engine.record_bot_response("I completely understand. What specifically isn't working?")

    # Next user message
    result = engine.process_user_message("Their reporting is terrible and costs a fortune")
    print(result.estimated_yield)         # 127.30 (yield is GROWING)

Integration with ANY bot framework:
    - Discord: Hook into on_message
    - Telegram: Hook into message handler
    - Slack: Hook into event listener
    - OpenClaw: Register as a skill
    - Custom: Just call process_user_message()
"""

from __future__ import annotations

import time
from typing import Optional

from convoyield.engines.sentiment_arbitrage import SentimentArbitrage
from convoyield.engines.micro_conversion import MicroConversionTracker
from convoyield.engines.momentum import MomentumScorer
from convoyield.engines.yield_forecaster import YieldForecaster
from convoyield.engines.play_caller import PlayCaller
from convoyield.models.conversation import ConversationState, Speaker, Turn
from convoyield.models.yield_result import YieldResult


class ConvoYield:
    """
    The Conversational Yield Optimization Engine.

    Treats every conversation as a yield-bearing financial instrument and
    maximizes the value extracted from each interaction.

    Zero external dependencies. Zero API costs. Pure behavioral algorithms.

    Args:
        base_conversation_value: Expected average value of a conversation in dollars.
            Adjust this to match your business model.
            E-commerce: $15-50, SaaS: $50-200, Enterprise: $200-5000
        momentum_lookback: Number of recent turns to analyze for momentum.
    """

    def __init__(
        self,
        base_conversation_value: float = 25.0,
        momentum_lookback: int = 6,
    ):
        self._sentiment = SentimentArbitrage()
        self._micro = MicroConversionTracker()
        self._momentum = MomentumScorer(lookback_window=momentum_lookback)
        self._forecaster = YieldForecaster(base_conversation_value=base_conversation_value)
        self._play_caller = PlayCaller()

        self._state = ConversationState()
        self._total_captured = 0.0

    @property
    def state(self) -> ConversationState:
        """Access the underlying conversation state."""
        return self._state

    @property
    def total_yield_captured(self) -> float:
        """Total dollar value captured across all micro-conversions."""
        return self._total_captured

    def reset(self):
        """Reset for a new conversation."""
        self._state = ConversationState()
        self._total_captured = 0.0

    def process_user_message(self, text: str, timestamp: Optional[float] = None) -> YieldResult:
        """
        Process a user message and return the full yield analysis.

        This is the main method your bot calls for every incoming user message.
        It returns a YieldResult containing:
            - Sentiment analysis and delta
            - Arbitrage opportunities
            - Micro-conversion opportunities
            - Momentum score
            - Yield forecast
            - Recommended plays with execution guidance
            - Risk assessment
            - Recommended tone and response length

        Args:
            text: The user's message text.
            timestamp: Optional Unix timestamp. Defaults to now.

        Returns:
            YieldResult with complete analysis and recommendations.
        """
        # Record the turn
        kwargs = {}
        if timestamp is not None:
            kwargs["timestamp"] = timestamp
        self._state.add_turn(Speaker.USER, text, **kwargs)

        # ── Engine 1: Sentiment Arbitrage ────────────────────────────────
        sentiment, sentiment_delta = self._sentiment.get_sentiment_with_context(self._state)
        self._state.sentiment_history.append(sentiment)

        arbitrage_ops = self._sentiment.detect_arbitrage(self._state)

        # ── Engine 2: Micro-Conversions ──────────────────────────────────
        micro_conversions = self._micro.scan(self._state)

        # ── Engine 3: Momentum ───────────────────────────────────────────
        momentum = self._momentum.score(self._state)
        self._state.momentum_history.append(momentum)

        # ── Engine 4: Yield Forecast ─────────────────────────────────────
        estimated_yield = self._forecaster.forecast(
            state=self._state,
            arbitrage_ops=arbitrage_ops,
            micro_conversions=micro_conversions,
            momentum=momentum,
            sentiment=sentiment,
        )

        risk = self._forecaster.calculate_risk(
            state=self._state,
            momentum=momentum,
            sentiment=sentiment,
        )

        # ── Engine 5: Play Caller ────────────────────────────────────────
        arbitrage_types = [op.type for op in arbitrage_ops]
        plays = self._play_caller.call_plays(
            state=self._state,
            sentiment=sentiment,
            momentum=momentum,
            risk=risk,
            arbitrage_types=arbitrage_types,
        )

        recommended_tone = self._play_caller.get_recommended_tone(plays)
        response_length = self._momentum.recommend_response_length(momentum, self._state.phase.value)

        # ── Assemble Result ──────────────────────────────────────────────
        result = YieldResult(
            current_sentiment=round(sentiment, 3),
            sentiment_delta=round(sentiment_delta, 3),
            momentum_score=round(momentum, 3),
            estimated_yield=estimated_yield,
            yield_captured_so_far=round(self._total_captured, 2),
            arbitrage_opportunities=arbitrage_ops,
            micro_conversions=micro_conversions,
            recommended_plays=plays,
            recommended_play=plays[0].name if plays else None,
            recommended_tone=recommended_tone,
            phase=self._state.phase.value,
            risk_level=round(risk, 2),
            optimal_response_length=response_length,
            urgency=max((op.urgency for op in arbitrage_ops), default=0.0),
        )

        return result

    def record_bot_response(self, text: str, timestamp: Optional[float] = None):
        """
        Record the bot's response to maintain full conversation state.

        Call this after your bot sends its response so the engines can
        track the full conversation flow for momentum and phase detection.
        """
        kwargs = {}
        if timestamp is not None:
            kwargs["timestamp"] = timestamp
        self._state.add_turn(Speaker.BOT, text, **kwargs)

    def mark_conversion(self, conversion_type: str, value: Optional[float] = None):
        """
        Mark a micro-conversion as successfully captured.

        Call this when your bot successfully extracts value (e.g., user
        provides their email, states their budget, etc.)

        Args:
            conversion_type: The type of conversion (e.g., "email_capture_opportunity")
            value: Optional override for the dollar value. If None, uses the
                   engine's estimated value.
        """
        self._micro.mark_captured(self._state, conversion_type)
        if value is not None:
            self._total_captured += value
        else:
            # Use estimated value from last scan
            self._total_captured += 2.0  # Conservative default

    def get_dashboard(self) -> dict:
        """
        Get a real-time dashboard view of the conversation.

        Returns a dictionary suitable for displaying in a UI or logging.
        Perfect for building a live "conversation value" dashboard.
        """
        last_sentiment = self._state.sentiment_history[-1] if self._state.sentiment_history else 0.0
        last_momentum = self._state.momentum_history[-1] if self._state.momentum_history else 0.0

        return {
            "session": {
                "turn_count": self._state.turn_count,
                "phase": self._state.phase.value,
                "duration_seconds": round(self._state.conversation_duration, 1),
            },
            "yield": {
                "estimated_total": round(
                    self._forecaster.forecast(
                        self._state, [], [], last_momentum, last_sentiment
                    ), 2
                ) if self._state.turns else 0.0,
                "captured": round(self._total_captured, 2),
                "micro_conversions_captured": len(self._state.micro_conversions_captured),
            },
            "health": {
                "sentiment": round(last_sentiment, 2),
                "momentum": round(last_momentum, 2),
                "momentum_label": self._momentum.get_momentum_label(last_momentum),
                "risk": round(
                    self._forecaster.calculate_risk(self._state, last_momentum, last_sentiment), 2
                ) if self._state.turns else 0.0,
            },
            "active_plays": self._state.active_plays,
        }

    def process_conversation(self, messages: list[dict]) -> YieldResult:
        """
        Process an entire conversation history at once.

        Useful for analyzing existing conversation logs.

        Args:
            messages: List of dicts with "role" ("user" or "bot") and "text" keys.
                      Optional "timestamp" key.

        Returns:
            YieldResult for the final message.
        """
        result = None
        for msg in messages:
            role = msg["role"]
            text = msg["text"]
            ts = msg.get("timestamp")

            if role == "user":
                result = self.process_user_message(text, timestamp=ts)
            elif role == "bot":
                self.record_bot_response(text, timestamp=ts)

        if result is None:
            # No user messages — return empty result
            result = YieldResult(
                current_sentiment=0.0,
                sentiment_delta=0.0,
                momentum_score=0.0,
                estimated_yield=0.0,
                yield_captured_so_far=0.0,
            )

        return result
