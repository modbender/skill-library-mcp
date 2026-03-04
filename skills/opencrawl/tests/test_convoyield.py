"""
Tests for ConvoYield — Conversational Yield Optimization Engine.

Tests cover all five engines and the main orchestrator.
"""

import pytest
from convoyield import ConvoYield
from convoyield.engines.sentiment_arbitrage import SentimentArbitrage
from convoyield.engines.micro_conversion import MicroConversionTracker
from convoyield.engines.momentum import MomentumScorer
from convoyield.engines.yield_forecaster import YieldForecaster
from convoyield.engines.play_caller import PlayCaller
from convoyield.models.conversation import (
    ConversationState,
    Speaker,
    Turn,
    ConversationPhase,
)
from convoyield.models.yield_result import YieldResult


# ── Sentiment Arbitrage Tests ────────────────────────────────────────────────

class TestSentimentArbitrage:
    def setup_method(self):
        self.engine = SentimentArbitrage()

    def test_positive_sentiment(self):
        score = self.engine.score_sentiment("This is amazing and I love it!")
        assert score > 0.5

    def test_negative_sentiment(self):
        score = self.engine.score_sentiment("This is terrible and broken")
        assert score < -0.4

    def test_neutral_sentiment(self):
        score = self.engine.score_sentiment("Can you tell me about your product?")
        assert -0.2 <= score <= 0.2

    def test_empty_text(self):
        score = self.engine.score_sentiment("")
        assert score == 0.0

    def test_frustration_arbitrage(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "I'm so frustrated with my current provider, nothing works")
        opportunities = self.engine.detect_arbitrage(state)
        assert len(opportunities) > 0
        types = [op.type for op in opportunities]
        assert "frustration_capture" in types

    def test_competitor_displacement_arbitrage(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "I want to switch from my existing tool, it's annoying")
        opportunities = self.engine.detect_arbitrage(state)
        assert len(opportunities) > 0
        types = [op.type for op in opportunities]
        assert "competitor_displacement" in types

    def test_urgency_arbitrage(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "I need this done ASAP, we have an urgent deadline tomorrow")
        opportunities = self.engine.detect_arbitrage(state)
        types = [op.type for op in opportunities]
        assert "urgency_premium" in types

    def test_budget_arbitrage(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "How much does it cost? Is it too expensive?")
        opportunities = self.engine.detect_arbitrage(state)
        types = [op.type for op in opportunities]
        assert "budget_value_stack" in types

    def test_no_arbitrage_neutral_message(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "Hello there")
        opportunities = self.engine.detect_arbitrage(state)
        assert len(opportunities) == 0

    def test_sentiment_with_context(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "This is great!")
        state.sentiment_history = [0.5]
        state.add_turn(Speaker.BOT, "Glad you like it!")
        state.add_turn(Speaker.USER, "Actually this is terrible")

        sentiment, delta = self.engine.get_sentiment_with_context(state)
        assert sentiment < 0
        assert delta < 0  # Sentiment dropped


# ── Micro-Conversion Tests ───────────────────────────────────────────────────

class TestMicroConversion:
    def setup_method(self):
        self.tracker = MicroConversionTracker()

    def test_budget_reveal(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "Our budget is around $5000 per month")
        conversions = self.tracker.scan(state)
        types = [c.type for c in conversions]
        assert "budget_reveal" in types

    def test_timeline_reveal(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "We need this by next month for our launch")
        conversions = self.tracker.scan(state)
        types = [c.type for c in conversions]
        assert "timeline_reveal" in types

    def test_email_capture_opportunity(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "Can you send me the details by email?")
        conversions = self.tracker.scan(state)
        types = [c.type for c in conversions]
        assert "email_capture_opportunity" in types

    def test_competitor_mention(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "We're currently using Slack but looking for an alternative")
        conversions = self.tracker.scan(state)
        types = [c.type for c in conversions]
        assert "competitor_mention" in types

    def test_need_statement(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "I need a way to track my team's performance")
        conversions = self.tracker.scan(state)
        types = [c.type for c in conversions]
        assert "need_statement" in types

    def test_feature_request(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "It would be great if you could support dark mode")
        conversions = self.tracker.scan(state)
        types = [c.type for c in conversions]
        assert "feature_request" in types

    def test_mark_captured(self):
        state = ConversationState()
        self.tracker.mark_captured(state, "email_capture_opportunity")
        assert "email_capture_opportunity" in state.micro_conversions_captured

    def test_value_calculation(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "Our budget is $10000 and we need it ASAP")
        conversions = self.tracker.scan(state)
        total = self.tracker.total_available_value(conversions)
        assert total > 0


# ── Momentum Tests ───────────────────────────────────────────────────────────

class TestMomentum:
    def setup_method(self):
        self.scorer = MomentumScorer()

    def test_increasing_engagement(self):
        state = ConversationState()
        # Short messages → longer messages = increasing engagement
        state.add_turn(Speaker.USER, "Hi")
        state.add_turn(Speaker.BOT, "Hello!")
        state.add_turn(Speaker.USER, "I have a question about your product")
        state.add_turn(Speaker.BOT, "Sure, what would you like to know?")
        state.add_turn(Speaker.USER, "I'm really interested in the enterprise features and want to know more about pricing and how it compares to other solutions we've been evaluating")

        momentum = self.scorer.score(state)
        assert momentum > 0  # Should be positive — user is getting more engaged

    def test_decreasing_engagement(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "I'm really excited about this product and all the amazing features you offer for enterprise teams")
        state.add_turn(Speaker.BOT, "Great! Let me tell you more.")
        state.add_turn(Speaker.USER, "Sure tell me")
        state.add_turn(Speaker.BOT, "Here are the details...")
        state.add_turn(Speaker.USER, "ok")
        state.add_turn(Speaker.BOT, "Want to learn more?")
        state.add_turn(Speaker.USER, "no")

        momentum = self.scorer.score(state)
        assert momentum < 0  # Should be negative — user is disengaging

    def test_empty_conversation(self):
        state = ConversationState()
        momentum = self.scorer.score(state)
        assert momentum == 0.0

    def test_momentum_labels(self):
        assert self.scorer.get_momentum_label(0.8) == "surging"
        assert self.scorer.get_momentum_label(0.4) == "accelerating"
        assert self.scorer.get_momentum_label(0.0) == "stable"
        assert self.scorer.get_momentum_label(-0.4) == "declining"
        assert self.scorer.get_momentum_label(-0.8) == "hemorrhaging"


# ── Yield Forecaster Tests ───────────────────────────────────────────────────

class TestYieldForecaster:
    def setup_method(self):
        self.forecaster = YieldForecaster(base_conversation_value=25.0)

    def test_basic_forecast(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "Hello")
        state.add_turn(Speaker.BOT, "Hi there!")

        yield_val = self.forecaster.forecast(state, [], [], 0.0, 0.0)
        assert yield_val > 0  # Should have some base value

    def test_higher_yield_with_arbitrage(self):
        from convoyield.models.yield_result import ArbitrageOpportunity

        state = ConversationState()
        state.add_turn(Speaker.USER, "I need this urgently")

        arb = ArbitrageOpportunity(
            type="urgency_premium",
            confidence=0.8,
            estimated_value=50.0,
            trigger_phrase="urgently",
            recommended_action="Offer premium",
            urgency=1.0,
            window_seconds=30.0,
        )

        yield_with = self.forecaster.forecast(state, [arb], [], 0.5, 0.5)
        yield_without = self.forecaster.forecast(state, [], [], 0.5, 0.5)
        assert yield_with > yield_without

    def test_risk_calculation(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "ok")

        # Negative momentum + negative sentiment = high risk
        risk = self.forecaster.calculate_risk(state, momentum=-0.5, sentiment=-0.5)
        assert risk > 0.3

        # Positive signals = low risk
        state2 = ConversationState()
        state2.add_turn(Speaker.USER, "This is really amazing, tell me more about everything!")
        risk2 = self.forecaster.calculate_risk(state2, momentum=0.5, sentiment=0.5)
        assert risk2 < risk


# ── Play Caller Tests ────────────────────────────────────────────────────────

class TestPlayCaller:
    def setup_method(self):
        self.caller = PlayCaller()

    def test_opening_play(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "Hello, I'm interested in your product")

        plays = self.caller.call_plays(state, sentiment=0.3, momentum=0.0, risk=0.2, arbitrage_types=[])
        assert len(plays) > 0
        # Should recommend an opening play
        play_names = [p.name for p in plays]
        assert "warm_handshake" in play_names or "pattern_interrupt" in play_names

    def test_frustration_play(self):
        state = ConversationState()
        # Move to discovery phase
        for i in range(4):
            state.add_turn(Speaker.USER, f"Message {i}")
            state.add_turn(Speaker.BOT, f"Response {i}")

        plays = self.caller.call_plays(
            state,
            sentiment=-0.6,
            momentum=-0.3,
            risk=0.5,
            arbitrage_types=["frustration_capture"],
        )
        assert len(plays) > 0
        # Should recommend empathy-based plays
        play_names = [p.name for p in plays]
        assert "empathy_bridge" in play_names or "momentum_recovery" in play_names

    def test_plays_sorted_by_priority(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "Tell me more")
        state.add_turn(Speaker.BOT, "Sure!")

        plays = self.caller.call_plays(state, sentiment=0.0, momentum=0.0, risk=0.3, arbitrage_types=[])
        if len(plays) >= 2:
            assert plays[0].priority >= plays[1].priority

    def test_recommended_tone(self):
        plays_empty = []
        tone = self.caller.get_recommended_tone(plays_empty)
        assert tone == "professional"  # Default


# ── Orchestrator Tests ───────────────────────────────────────────────────────

class TestOrchestrator:
    def test_basic_flow(self):
        engine = ConvoYield(base_conversation_value=25.0)
        result = engine.process_user_message("Hi, I need help with project management")

        assert isinstance(result, YieldResult)
        assert result.estimated_yield > 0
        assert result.phase is not None
        assert result.current_sentiment is not None

    def test_multi_turn_conversation(self):
        engine = ConvoYield(base_conversation_value=50.0)

        r1 = engine.process_user_message("Hello, I'm looking for a CRM")
        engine.record_bot_response("Welcome! What's your team size?")

        r2 = engine.process_user_message("50 people. We're frustrated with Salesforce")
        engine.record_bot_response("I hear you. What specifically isn't working?")

        r3 = engine.process_user_message("The reporting is terrible and it costs us $500/month")

        # Yield should grow as conversation reveals more value
        assert r3.estimated_yield > r1.estimated_yield
        # Should detect arbitrage opportunities
        assert len(r3.arbitrage_opportunities) > 0 or len(r2.arbitrage_opportunities) > 0

    def test_yield_result_dict(self):
        engine = ConvoYield()
        result = engine.process_user_message("I'm interested in your premium plan")
        d = result.to_dict()

        assert "sentiment" in d
        assert "momentum" in d
        assert "estimated_yield" in d
        assert "phase" in d

    def test_dashboard(self):
        engine = ConvoYield()
        engine.process_user_message("Hello")
        engine.record_bot_response("Hi there!")

        dashboard = engine.get_dashboard()
        assert "session" in dashboard
        assert "yield" in dashboard
        assert "health" in dashboard

    def test_mark_conversion(self):
        engine = ConvoYield()
        engine.process_user_message("Send me the details by email")
        engine.mark_conversion("email_capture_opportunity", 5.0)
        assert engine.total_yield_captured == 5.0

    def test_reset(self):
        engine = ConvoYield()
        engine.process_user_message("Hello")
        engine.reset()
        assert engine.state.turn_count == 0
        assert engine.total_yield_captured == 0.0

    def test_process_conversation_batch(self):
        engine = ConvoYield()
        messages = [
            {"role": "user", "text": "Hi there"},
            {"role": "bot", "text": "Hello!"},
            {"role": "user", "text": "I'm frustrated with my current tool"},
            {"role": "bot", "text": "I understand. Tell me more."},
            {"role": "user", "text": "It's broken and expensive, costs $200/month"},
        ]
        result = engine.process_conversation(messages)
        assert result.estimated_yield > 0
        assert result.phase is not None


# ── Conversation State Tests ─────────────────────────────────────────────────

class TestConversationState:
    def test_phase_auto_detection(self):
        state = ConversationState()
        state.add_turn(Speaker.USER, "Hello")
        assert state.phase == ConversationPhase.OPENING

        state.add_turn(Speaker.BOT, "Hi!")
        state.add_turn(Speaker.USER, "Tell me about your product")
        state.add_turn(Speaker.BOT, "Sure!")
        state.add_turn(Speaker.USER, "What features do you have?")
        assert state.phase in (ConversationPhase.DISCOVERY, ConversationPhase.ENGAGEMENT)

    def test_closing_detection(self):
        state = ConversationState()
        for i in range(6):
            state.add_turn(Speaker.USER, f"msg {i}")
            state.add_turn(Speaker.BOT, f"resp {i}")
        state.add_turn(Speaker.USER, "Thanks, goodbye!")
        assert state.phase == ConversationPhase.CLOSING

    def test_negotiation_detection(self):
        state = ConversationState()
        for i in range(4):
            state.add_turn(Speaker.USER, f"msg {i}")
            state.add_turn(Speaker.BOT, f"resp {i}")
        state.add_turn(Speaker.USER, "How much does it cost?")
        assert state.phase == ConversationPhase.NEGOTIATION

    def test_turn_properties(self):
        turn = Turn(speaker=Speaker.USER, text="Hello world! How are you?")
        assert turn.word_count == 5
        assert turn.has_question is True
        assert turn.exclamation_density > 0
