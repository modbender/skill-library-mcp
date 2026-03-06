"""Tests for the ResonanceEngine core."""

import unittest

from openpaw import ResonanceEngine
from openpaw.models import Conversation


class TestResonanceEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ResonanceEngine()

    def test_basic_analysis(self):
        convo = Conversation(goal="sale")
        convo.add_bot_message("Hi! How can I help you today?")
        convo.add_user_message("I'm looking for a project management tool")

        result = self.engine.analyze(convo)

        self.assertIsNotNone(result)
        self.assertEqual(result.turn_number, 2)
        self.assertGreaterEqual(result.profile.engagement, 0.0)
        self.assertLessEqual(result.profile.engagement, 1.0)
        self.assertGreaterEqual(result.profile.trust, 0.0)
        self.assertLessEqual(result.profile.trust, 1.0)

    def test_engagement_increases_with_elaboration(self):
        convo = Conversation(goal="sale")
        convo.add_bot_message("What are you looking for?")
        convo.add_user_message("tools")
        r1 = self.engine.analyze(convo)

        self.engine.reset()
        convo2 = Conversation(goal="sale")
        convo2.add_bot_message("What are you looking for?")
        convo2.add_user_message(
            "I'm looking for a comprehensive project management solution "
            "that integrates with our existing workflow. We need task tracking, "
            "time management, and team collaboration features. We've tried "
            "several options but none quite fit our needs."
        )
        r2 = self.engine.analyze(convo2)

        self.assertGreater(r2.profile.engagement, r1.profile.engagement)

    def test_commitment_language_boosts_decision(self):
        convo = Conversation(goal="sale")
        convo.add_bot_message("Our premium plan includes everything you need.")
        convo.add_user_message("Maybe I'll think about it later, not sure really")
        r1 = self.engine.analyze(convo)

        self.engine.reset()
        convo2 = Conversation(goal="sale")
        convo2.add_bot_message("Our premium plan includes everything you need.")
        convo2.add_user_message(
            "Yes absolutely, let's do it! Sign me up for the premium plan now!"
        )
        r2 = self.engine.analyze(convo2)

        self.assertGreater(r2.profile.decision, r1.profile.decision)

    def test_objections_lower_decision(self):
        convo = Conversation(goal="sale")
        convo.add_bot_message("The plan is $99/month.")
        convo.add_user_message(
            "That's too expensive. I'm concerned about the cost "
            "and I don't think it's worth that much. There are "
            "cheaper alternatives that might work."
        )
        result = self.engine.analyze(convo)

        self.assertLess(result.profile.decision, 0.5)
        self.assertGreater(result.signals.objection_frequency, 0.0)

    def test_trust_builds_with_personal_disclosure(self):
        convo = Conversation(goal="support")
        convo.add_bot_message("Tell me about your situation.")
        convo.add_user_message("ok")
        r1 = self.engine.analyze(convo)

        self.engine.reset()
        convo2 = Conversation(goal="support")
        convo2.add_bot_message("Tell me about your situation.")
        convo2.add_user_message(
            "Honestly, I've been struggling with my current setup "
            "for months. My team and I are frustrated. Personally, "
            "I think we need a complete overhaul of our workflow."
        )
        r2 = self.engine.analyze(convo2)

        self.assertGreater(r2.profile.trust, r1.profile.trust)

    def test_yield_prediction(self):
        convo = Conversation(goal="sale")
        convo.add_bot_message("Here's what our solution offers...")
        convo.add_user_message(
            "Yes, that sounds perfect! I need this right away. "
            "Let's do it, sign me up immediately!"
        )
        result = self.engine.analyze(convo)

        self.assertGreater(result.yield_prediction.conversion_probability, 0.3)
        self.assertIn(
            result.yield_prediction.estimated_value,
            ["low", "medium", "high", "very_high"],
        )

    def test_tuning_recommendation(self):
        convo = Conversation(goal="sale")
        convo.add_bot_message("Welcome! How can I help?")
        convo.add_user_message("Just browsing, not sure what I need")
        result = self.engine.analyze(convo)

        self.assertIsNotNone(result.recommendation.action)
        self.assertIsNotNone(result.recommendation.style)
        self.assertTrue(len(result.recommendation.action) > 0)

    def test_prompt_injection_output(self):
        convo = Conversation(goal="sale")
        convo.add_bot_message("Hi!")
        convo.add_user_message("I want to learn more about your product")
        result = self.engine.analyze(convo)

        injection = result.recommendation.to_prompt_injection()
        self.assertIn("[RESONANCE TUNING]", injection)
        self.assertIn("Response length:", injection)

    def test_multi_turn_conversation(self):
        convo = Conversation(goal="sale")

        convo.add_bot_message("Welcome! What brings you here today?")
        convo.add_user_message("Looking at your enterprise plan")
        r1 = self.engine.analyze(convo)

        convo.add_bot_message("Great choice! It includes advanced analytics and priority support.")
        convo.add_user_message(
            "That sounds interesting. My team of 50 really needs "
            "better analytics. Tell me more about the features."
        )
        r2 = self.engine.analyze(convo)

        convo.add_bot_message("Our analytics dashboard gives real-time insights...")
        convo.add_user_message(
            "Perfect, exactly what we need! How quickly can we "
            "get started? I want to set this up for my team today."
        )
        r3 = self.engine.analyze(convo)

        # Decision frequency should increase across the conversation
        self.assertGreater(r3.profile.decision, r1.profile.decision)

    def test_summary_output(self):
        convo = Conversation(goal="sale")
        convo.add_bot_message("Hi!")
        convo.add_user_message("Hello, I'm interested in your services")
        result = self.engine.analyze(convo)

        summary = result.summary()
        self.assertIn("RESONANCE ANALYSIS", summary)
        self.assertIn("Engagement:", summary)
        self.assertIn("Trust:", summary)
        self.assertIn("Decision:", summary)
        self.assertIn("ACTION", summary)

    def test_to_dict_output(self):
        convo = Conversation(goal="sale")
        convo.add_bot_message("Hi!")
        convo.add_user_message("Hello")
        result = self.engine.analyze(convo)

        d = result.to_dict()
        self.assertIn("frequencies", d)
        self.assertIn("recommendation", d)
        self.assertIn("yield", d)
        self.assertIn("signals", d)
        self.assertIn("resonance_level", d)

    def test_engine_reset(self):
        convo = Conversation(goal="sale")
        convo.add_bot_message("Hi!")
        convo.add_user_message("Hello")
        self.engine.analyze(convo)

        self.assertEqual(len(self.engine.history), 1)
        self.engine.reset()
        self.assertEqual(len(self.engine.history), 0)

    def test_empty_conversation(self):
        convo = Conversation()
        result = self.engine.analyze(convo)
        # Empty convo has base trust of 0.3 (design choice), so it's WEAK not NO_RESONANCE
        self.assertIn(result.profile.resonance_level, ("NO_RESONANCE", "WEAK"))
        self.assertLess(result.profile.composite, 0.4)


if __name__ == "__main__":
    unittest.main()
