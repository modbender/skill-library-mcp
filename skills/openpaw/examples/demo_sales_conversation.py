#!/usr/bin/env python3
"""
ResonanceEngine Demo — Sales Conversation

Watch the engine analyze a real sales conversation in real-time,
computing frequencies and generating recommendations at each turn.

Run: python examples/demo_sales_conversation.py
"""

from openpaw import ResonanceEngine
from openpaw.models import Conversation


def main():
    engine = ResonanceEngine()
    convo = Conversation(goal="sale")

    print("=" * 70)
    print("  RESONANCE ENGINE DEMO — Live Sales Conversation Analysis")
    print("=" * 70)
    print()

    # Turn 1: Opening
    turns = [
        (
            "Hi there! Welcome to CloudStack. What brings you here today?",
            "I'm looking at project management tools for my team",
        ),
        # Turn 2: Discovery
        (
            "Great! How big is your team and what's your current workflow like?",
            "We're about 30 people. Right now we use spreadsheets and email, "
            "it's honestly a mess. I've been personally frustrated with it for months.",
        ),
        # Turn 3: Value presentation
        (
            "I hear you — that's a common pain point. Our platform replaces "
            "all of that with one unified workspace. Teams like yours "
            "typically see 40% time savings in the first month.",
            "That sounds interesting. What does it cost though? "
            "I'm worried it might be too expensive for our budget.",
        ),
        # Turn 4: Objection handling
        (
            "Totally understand the budget concern. Our Team plan is $12/user/month. "
            "But consider this: if each team member saves just 2 hours a week, "
            "that's over $50,000 in productivity gains annually.",
            "Hmm, that's actually a good point. My team wastes so much time "
            "on status meetings alone. Can we do a trial first?",
        ),
        # Turn 5: Closing
        (
            "Absolutely! We offer a 14-day free trial with full access. "
            "I can set your team up right now. Want to get started?",
            "Yes, let's do it! Can we start today? I want to get my team "
            "onboarded before our Monday standup. Sign us up!",
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

    # Final summary
    print("=" * 70)
    print("  CONVERSATION JOURNEY")
    print("=" * 70)
    print()
    for i, result in enumerate(engine.history, 1):
        level = result.profile.resonance_level
        prob = result.yield_prediction.conversion_probability
        action = result.yield_prediction.recommended_action
        print(
            f"  Turn {i}: {level:>16s} | "
            f"Conv: {prob:5.0%} | {action}"
        )
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
