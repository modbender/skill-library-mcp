#!/usr/bin/env python3
"""
ResonanceEngine Demo — Support Conversation

Shows how the engine detects frustration, builds trust,
and identifies the optimal moment for resolution/upsell.

Run: python examples/demo_support_conversation.py
"""

from openpaw import ResonanceEngine
from openpaw.models import Conversation


def main():
    engine = ResonanceEngine()
    convo = Conversation(goal="support")

    print("=" * 70)
    print("  RESONANCE ENGINE DEMO — Support Conversation Analysis")
    print("=" * 70)
    print()

    turns = [
        # Turn 1: Frustrated user
        (
            "Hi, how can I help you today?",
            "Your app keeps crashing! This is terrible. I've been trying "
            "to use it all morning and I'm so frustrated.",
        ),
        # Turn 2: Empathy + diagnosis
        (
            "I'm really sorry you're experiencing this. Let me help fix "
            "this right away. Can you tell me which device you're using?",
            "iPhone 15. It crashes every time I try to open the dashboard. "
            "I've already tried restarting. It's been broken for days.",
        ),
        # Turn 3: Solution offered
        (
            "Thank you for those details. There was a known issue with "
            "the dashboard on iOS that we fixed yesterday. Could you "
            "update the app to version 4.2.1?",
            "Oh, I didn't know there was an update. Let me try... "
            "Ok it's updating now.",
        ),
        # Turn 4: Resolution
        (
            "Great! Once it's updated, the dashboard should work smoothly. "
            "Let me know if you need anything else.",
            "It works now! Thank you so much, you've been really helpful. "
            "I appreciate how quickly you resolved this.",
        ),
        # Turn 5: Upsell opportunity
        (
            "So glad it's working! By the way, our Premium plan includes "
            "priority support so you'd get instant help if anything "
            "comes up again. Would you like to hear more?",
            "Actually yes, that sounds great. I need reliable support "
            "for my business. How much is it?",
        ),
    ]

    for i, (bot_msg, user_msg) in enumerate(turns, 1):
        convo.add_bot_message(bot_msg)
        convo.add_user_message(user_msg)

        result = engine.analyze(convo)

        print(f"{'─' * 70}")
        print(f"  TURN {i}")
        print(f"{'─' * 70}")
        print(f"  BOT:  {bot_msg[:70]}...")
        print(f"  USER: {user_msg[:70]}...")
        print()
        print(result.summary())
        print()

    print("=" * 70)
    print("  SENTIMENT JOURNEY: Frustrated → Grateful → Ready to Buy")
    print("=" * 70)
    print()
    for i, result in enumerate(engine.history, 1):
        level = result.profile.resonance_level
        trust = result.profile.trust
        sentiment = result.signals.positive_sentiment_trend
        print(
            f"  Turn {i}: {level:>16s} | "
            f"Trust: {trust:.2f} | "
            f"Sentiment Trend: {sentiment:+.2f}"
        )
    print()


if __name__ == "__main__":
    main()
