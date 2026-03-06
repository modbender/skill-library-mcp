#!/usr/bin/env python3
"""
ConvoYield Batch Analysis — Analyze existing conversation logs.

Got historical conversation data? Feed it through ConvoYield to discover
how much money you've been leaving on the table.

This example processes conversation logs and generates a yield report
showing total value, capture rate, and missed opportunities.
"""

from convoyield import ConvoYield


def analyze_conversation_log(conversations: list[list[dict]]) -> dict:
    """
    Analyze a batch of conversation logs.

    Args:
        conversations: List of conversations, each being a list of
                      {"role": "user"|"bot", "text": "..."} dicts.

    Returns:
        Aggregate yield analysis report.
    """
    total_estimated = 0.0
    total_captured = 0.0
    total_arbitrage_count = 0
    total_micro_count = 0
    play_frequency: dict[str, int] = {}
    arbitrage_frequency: dict[str, int] = {}
    phase_distribution: dict[str, int] = {}

    for convo in conversations:
        engine = ConvoYield(base_conversation_value=25.0)
        result = engine.process_conversation(convo)

        total_estimated += result.estimated_yield
        total_captured += result.yield_captured_so_far
        total_arbitrage_count += len(result.arbitrage_opportunities)
        total_micro_count += len(result.micro_conversions)

        if result.recommended_play:
            play_frequency[result.recommended_play] = play_frequency.get(result.recommended_play, 0) + 1

        for arb in result.arbitrage_opportunities:
            arbitrage_frequency[arb.type] = arbitrage_frequency.get(arb.type, 0) + 1

        if result.phase:
            phase_distribution[result.phase] = phase_distribution.get(result.phase, 0) + 1

    return {
        "total_conversations": len(conversations),
        "total_estimated_yield": round(total_estimated, 2),
        "total_captured_yield": round(total_captured, 2),
        "yield_left_on_table": round(total_estimated - total_captured, 2),
        "capture_efficiency": round(
            (total_captured / total_estimated * 100) if total_estimated > 0 else 0, 1
        ),
        "avg_yield_per_convo": round(
            total_estimated / len(conversations) if conversations else 0, 2
        ),
        "total_arbitrage_opportunities": total_arbitrage_count,
        "total_micro_conversions": total_micro_count,
        "top_plays": sorted(play_frequency.items(), key=lambda x: x[1], reverse=True),
        "top_arbitrage_types": sorted(arbitrage_frequency.items(), key=lambda x: x[1], reverse=True),
        "phase_distribution": phase_distribution,
    }


def main():
    # Sample conversation logs
    sample_logs = [
        # Conversation 1: Frustrated customer switching from competitor
        [
            {"role": "user", "text": "Hi, I need a better email marketing tool"},
            {"role": "bot", "text": "Happy to help! What are you using currently?"},
            {"role": "user", "text": "Mailchimp, but I'm really frustrated with their pricing changes"},
            {"role": "bot", "text": "I hear that a lot. What specifically bothers you about the pricing?"},
            {"role": "user", "text": "They charge per subscriber now and we have 50k contacts. It's costing us $300/month for basic features"},
            {"role": "bot", "text": "That is steep. Our plan includes unlimited contacts for $99/month with all premium features."},
            {"role": "user", "text": "Wow that's way cheaper. Can I try it first?"},
        ],
        # Conversation 2: Quick information seeker
        [
            {"role": "user", "text": "How much is your pro plan?"},
            {"role": "bot", "text": "Our Pro plan is $49/month. It includes unlimited users, API access, and priority support."},
            {"role": "user", "text": "ok thanks"},
        ],
        # Conversation 3: Enterprise buyer with urgency
        [
            {"role": "user", "text": "We need an enterprise solution ASAP. Our current vendor just went down and we have a product launch next week"},
            {"role": "bot", "text": "I understand the urgency. Let's get you set up quickly. How many team members need access?"},
            {"role": "user", "text": "200 people across 3 offices. Budget isn't an issue, we just need reliability and fast onboarding"},
            {"role": "bot", "text": "Perfect. Our Enterprise plan supports unlimited users with 99.99% uptime SLA. We can have you migrated in 48 hours."},
            {"role": "user", "text": "That sounds perfect. Who do I talk to about getting the contract signed today?"},
        ],
        # Conversation 4: Price-sensitive small business
        [
            {"role": "user", "text": "Is there a free version of your tool?"},
            {"role": "bot", "text": "We offer a 14-day free trial of our full platform. After that, plans start at $19/month."},
            {"role": "user", "text": "That's too expensive for me. I'm just a small shop trying to get started"},
            {"role": "bot", "text": "I understand budget matters. Our Starter plan at $19/month typically pays for itself within the first week through time savings."},
            {"role": "user", "text": "Maybe. Let me think about it"},
        ],
    ]

    print("=" * 70)
    print("  ConvoYield — Batch Conversation Analysis")
    print("=" * 70)

    report = analyze_conversation_log(sample_logs)

    print(f"\n  Conversations Analyzed:    {report['total_conversations']}")
    print(f"  Total Estimated Yield:     ${report['total_estimated_yield']:.2f}")
    print(f"  Total Captured Yield:      ${report['total_captured_yield']:.2f}")
    print(f"  Value Left on Table:       ${report['yield_left_on_table']:.2f}")
    print(f"  Capture Efficiency:        {report['capture_efficiency']}%")
    print(f"  Avg Yield per Conversation: ${report['avg_yield_per_convo']:.2f}")
    print(f"  Arbitrage Opportunities:   {report['total_arbitrage_opportunities']}")
    print(f"  Micro-Conversions Found:   {report['total_micro_conversions']}")

    print(f"\n  Top Recommended Plays:")
    for play, count in report['top_plays'][:5]:
        print(f"    → {play}: {count}x")

    print(f"\n  Top Arbitrage Types:")
    for arb_type, count in report['top_arbitrage_types'][:5]:
        print(f"    → {arb_type}: {count}x")

    print(f"\n{'=' * 70}")
    print("  Stop leaving money on the table.")
    print("  Every conversation has a yield. ConvoYield helps you capture it.")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
