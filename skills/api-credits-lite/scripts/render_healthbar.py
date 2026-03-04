#!/usr/bin/env python3
"""
Render video-game style health bars for API credits.
"""

def render_bar(current, max_amount, width=10):
    """
    Render a health bar with block characters.
    
    Args:
        current: Current credit amount
        max_amount: Maximum credit amount
        width: Width of bar in characters (default 10)
    
    Returns:
        tuple: (bar_string, emoji, percentage)
    """
    if max_amount <= 0:
        return "░" * width, "⚪", 0
    
    percentage = (current / max_amount) * 100
    filled = int((current / max_amount) * width)
    empty = width - filled
    
    # Color-coded emoji based on percentage
    if percentage > 75:
        emoji = "🟩"
    elif percentage > 50:
        emoji = "🟨"
    elif percentage > 25:
        emoji = "🟧"
    else:
        emoji = "🟥"
    
    bar = "█" * filled + "░" * empty
    
    return bar, emoji, percentage


def format_credits(provider, current, max_amount, daily=None, weekly=None, last_sync=None):
    """
    Format complete credit display for a provider.
    
    Args:
        provider: Provider name (e.g., "OpenAI", "Anthropic")
        current: Current credit balance
        max_amount: Maximum credit amount
        daily: Optional daily spend
        weekly: Optional weekly spend
        last_sync: Optional last sync time string
    
    Returns:
        str: Formatted credit display
    """
    bar, emoji, pct = render_bar(current, max_amount)
    
    lines = []
    lines.append(f"{provider} {emoji}")
    lines.append(f"[{bar}] {pct:.0f}% (${current:.2f}/${max_amount:.2f})")
    
    # Optional stats line
    stats = []
    if daily is not None:
        stats.append(f"${daily:.2f} today")
    if weekly is not None:
        stats.append(f"${weekly:.2f} this week")
    if last_sync:
        stats.append(f"Last sync: {last_sync}")
    
    if stats:
        lines.append("↳ " + " • ".join(stats))
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test rendering
    print("Testing health bar rendering:\n")
    
    print(format_credits("OpenAI", 78.50, 100, daily=1.23, weekly=12.45))
    print()
    print(format_credits("Anthropic", 27.50, 50, last_sync="6h ago"))
    print()
    print(format_credits("Groq", 11, 50, daily=2.15))
