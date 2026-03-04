#!/usr/bin/env python3
"""
ConvoYield Basic Usage — See the engine in action.

Run this to see how ConvoYield transforms a simple customer conversation
into a yield-bearing financial instrument.

    python examples/basic_usage.py
"""

from convoyield import ConvoYield


def main():
    # Initialize the engine
    # Set base_conversation_value to match your business:
    #   E-commerce: $15-50
    #   SaaS: $50-200
    #   Enterprise sales: $200-5000
    engine = ConvoYield(base_conversation_value=50.0)

    print("=" * 70)
    print("  ConvoYield — Conversational Yield Optimization Engine")
    print("  Treating conversations as yield-bearing financial instruments")
    print("=" * 70)

    # ── Simulate a real customer conversation ────────────────────────────

    conversations = [
        {
            "user": "Hi, I'm looking for a project management tool for my team",
            "bot": "Welcome! I'd love to help you find the perfect solution. How many people are on your team?",
        },
        {
            "user": "We're about 25 people. We've been using Trello but it's getting messy",
            "bot": "25 people — that's a great team size! I hear you on Trello getting unwieldy at scale. What specifically is causing the most friction?",
        },
        {
            "user": "Honestly I'm frustrated with the lack of reporting. My boss keeps asking for project status and I spend hours compiling it manually every week",
            "bot": "That sounds incredibly time-consuming. Hours every week on manual reporting — that's probably costing you $500+/week in productivity alone. Our automated dashboards update in real-time and your boss can check status anytime. Would you like to see a quick demo?",
        },
        {
            "user": "That would be amazing! How much does it cost though? We're a startup so budget is tight",
            "bot": "Totally understand the startup budget reality. Our team plan is $12/user/month — for 25 people that's $300/month. But consider: you said you spend hours weekly on manual reporting. At even $50/hour, that's $200+/week you'd save. The tool pays for itself in the first week. Want me to set up a free 14-day trial?",
        },
        {
            "user": "Wow that's actually really reasonable. Yeah let's try it! Can you send the details to my email?",
            "bot": "Absolutely! I'm setting up your trial right now. What's the best email to send the setup guide to?",
        },
    ]

    for i, exchange in enumerate(conversations):
        print(f"\n{'─' * 70}")
        print(f"  Turn {i + 1}")
        print(f"{'─' * 70}")

        # User speaks
        print(f"\n  USER: {exchange['user']}")

        # ConvoYield analyzes
        result = engine.process_user_message(exchange["user"])

        # Display the yield analysis
        print(f"\n  ┌─ ConvoYield Analysis {'─' * 46}")
        print(f"  │ Sentiment:     {result.current_sentiment:+.2f} (delta: {result.sentiment_delta:+.2f})")
        print(f"  │ Momentum:      {result.momentum_score:+.2f}")
        print(f"  │ Phase:         {result.phase}")
        print(f"  │ Est. Yield:    ${result.estimated_yield:.2f}")
        print(f"  │ Risk Level:    {result.risk_level:.0%}")
        print(f"  │ Rec. Play:     {result.recommended_play or 'N/A'}")
        print(f"  │ Rec. Tone:     {result.recommended_tone}")
        print(f"  │ Resp. Length:  {result.optimal_response_length}")

        if result.arbitrage_opportunities:
            top = result.top_arbitrage
            print(f"  │")
            print(f"  │ ★ ARBITRAGE: {top.type}")
            print(f"  │   Value: ${top.estimated_value:.2f} | Confidence: {top.confidence:.0%}")
            print(f"  │   Action: {top.recommended_action[:70]}...")

        if result.micro_conversions:
            print(f"  │")
            print(f"  │ Micro-Conversions Detected:")
            for mc in result.micro_conversions[:3]:
                status = "✓" if mc.captured else "○"
                print(f"  │   {status} {mc.type}: ${mc.value:.2f}")

        if result.recommended_plays:
            print(f"  │")
            print(f"  │ Top Plays:")
            for play in result.recommended_plays[:3]:
                print(f"  │   → {play.name} (priority: {play.priority:.2f}, yield: ${play.expected_yield:.2f})")

        print(f"  └{'─' * 68}")

        # Bot responds
        print(f"\n  BOT: {exchange['bot']}")
        engine.record_bot_response(exchange["bot"])

    # ── Final Dashboard ──────────────────────────────────────────────────
    print(f"\n{'═' * 70}")
    print("  FINAL CONVERSATION DASHBOARD")
    print(f"{'═' * 70}")

    dashboard = engine.get_dashboard()
    print(f"\n  Session:    {dashboard['session']['turn_count']} turns | Phase: {dashboard['session']['phase']}")
    print(f"  Yield:      Est. ${dashboard['yield']['estimated_total']:.2f} | Captured: ${dashboard['yield']['captured']:.2f}")
    print(f"  Health:     Sentiment {dashboard['health']['sentiment']:+.2f} | Momentum: {dashboard['health']['momentum_label']}")
    print(f"  Risk:       {dashboard['health']['risk']:.0%}")

    print(f"\n{'═' * 70}")
    print("  Every conversation is a financial instrument.")
    print("  ConvoYield helps you maximize its yield.")
    print(f"{'═' * 70}\n")


if __name__ == "__main__":
    main()
