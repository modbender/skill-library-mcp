"""Tests for signal extraction."""

import unittest

from openpaw.models.conversation import Conversation
from openpaw.resonance.signals import SignalExtractor


class TestSignalExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = SignalExtractor()

    def test_hedge_detection(self):
        convo = Conversation()
        convo.add_user_message(
            "Maybe I could possibly try it, I'm not sure if it might work"
        )
        signals = self.extractor.extract(convo)
        self.assertGreater(signals.hedge_ratio, 0.0)

    def test_commitment_detection(self):
        convo = Conversation()
        convo.add_user_message(
            "Yes absolutely, let's do it! Sign me up, I'm ready!"
        )
        signals = self.extractor.extract(convo)
        self.assertGreater(signals.commitment_language, 0.0)

    def test_objection_detection(self):
        convo = Conversation()
        convo.add_user_message(
            "That's too expensive, I'm worried about the risk and I don't "
            "think it's worth it. There's a problem with the pricing."
        )
        signals = self.extractor.extract(convo)
        self.assertGreater(signals.objection_frequency, 0.0)

    def test_message_length_trajectory_growing(self):
        convo = Conversation()
        convo.add_user_message("Hi")
        convo.add_user_message("Tell me more about this")
        convo.add_user_message(
            "I'm very interested in learning more about your features "
            "and how they compare to the competition"
        )
        signals = self.extractor.extract(convo)
        self.assertGreater(signals.message_length_trajectory, 0.0)

    def test_message_length_trajectory_shrinking(self):
        convo = Conversation()
        convo.add_user_message(
            "I have a lot of detailed questions about your product "
            "and I want to understand everything about how it works "
            "and what benefits it provides to teams like ours"
        )
        convo.add_user_message("Ok sure, whatever")
        convo.add_user_message("fine")
        signals = self.extractor.extract(convo)
        self.assertLess(signals.message_length_trajectory, 0.0)

    def test_question_density(self):
        convo = Conversation()
        convo.add_user_message(
            "What does this do? How much is it? Is there a free trial?"
        )
        signals = self.extractor.extract(convo)
        self.assertGreater(signals.question_density, 0.0)

    def test_personal_disclosure(self):
        convo = Conversation()
        convo.add_user_message(
            "I personally think my team and I need this. "
            "Honestly, I've been struggling with our current setup."
        )
        signals = self.extractor.extract(convo)
        self.assertGreater(signals.personal_disclosure, 0.0)

    def test_urgency_detection(self):
        convo = Conversation()
        convo.add_user_message(
            "I need this urgently, ASAP! We have a deadline today "
            "and need it immediately!"
        )
        signals = self.extractor.extract(convo)
        self.assertGreater(signals.urgency_markers, 0.0)

    def test_sentiment_trend(self):
        convo = Conversation()
        convo.add_user_message("This is terrible and frustrating")
        convo.add_user_message("Hmm, ok that's a bit better")
        convo.add_user_message("Actually this is great, I love it!")
        signals = self.extractor.extract(convo)
        self.assertGreater(signals.positive_sentiment_trend, 0.0)

    def test_all_signals_bounded(self):
        convo = Conversation()
        convo.add_bot_message("Hello!")
        convo.add_user_message("Hi there, I'm interested in your product")
        convo.add_bot_message("Great! What are you looking for?")
        convo.add_user_message("Something for my team of 20 people")
        signals = self.extractor.extract(convo)

        d = signals.to_dict()
        for key, value in d.items():
            if key in ("momentum", "message_length_trajectory",
                       "formality_drift", "positive_sentiment_trend",
                       "specificity_increase"):
                self.assertGreaterEqual(value, -1.0, f"{key} below -1")
                self.assertLessEqual(value, 1.0, f"{key} above 1")
            elif key in ("avg_sentence_length",):
                pass  # Unbounded raw value
            else:
                self.assertGreaterEqual(value, 0.0, f"{key} below 0")
                self.assertLessEqual(value, 1.0, f"{key} above 1")


if __name__ == "__main__":
    unittest.main()
