#!/usr/bin/env python3
"""
Suggestions module for daily briefing.
Generates actionable improvements to try.
"""

import random
import sys
from datetime import datetime


# Pool of actionable suggestions
SUGGESTIONS_POOL = [
    {
        "category": "Productivity",
        "suggestion": "Create a HEARTBEAT.md file with 2-3 periodic checks (email, calendar, news). Heartbeats batch tasks efficiently.",
    },
    {
        "category": "Skills",
        "suggestion": "Review your installed skills with 'ls ~/openclaw/skills/' - remove any you haven't used in 30 days to reduce context bloat.",
    },
    {
        "category": "Memory",
        "suggestion": "Spend 5 minutes reviewing yesterday's memory file and update MEMORY.md with anything worth keeping long-term.",
    },
    {
        "category": "Automation",
        "suggestion": "Set up a cron job for one repetitive task you do daily. Use 'openclaw cron create --help' for syntax.",
    },
    {
        "category": "Organization",
        "suggestion": "Clean up your workspace downloads folder - move important files to appropriate project directories.",
    },
    {
        "category": "Learning",
        "suggestion": "Try a new skill you haven't used before. Run 'ls ~/openclaw/skills/' and pick one at random.",
    },
    {
        "category": "Efficiency",
        "suggestion": "Create a shell alias for your most-used OpenClaw commands. Add to ~/.zshrc for persistence.",
    },
    {
        "category": "Health",
        "suggestion": "Set a 2-hour reminder to stand up and stretch. Use 'openclaw cron create' for the reminder.",
    },
    {
        "category": "Focus",
        "suggestion": "Enable Do Not Disturb for 90 minutes this morning to work on your most important task uninterrupted.",
    },
    {
        "category": "System",
        "suggestion": "Check your disk space with 'df -h'. If over 80% full, run a cleanup or archive old files.",
    },
    {
        "category": "Security",
        "suggestion": "Review recent commits in your main project. Run 'git log --oneline -20' to see what's changed.",
    },
    {
        "category": "Workflow",
        "suggestion": "Create a template file for recurring documents you create. Save it to ~/Templates/ for easy access.",
    },
    {
        "category": "Communication",
        "suggestion": "Unsubscribe from 3 email newsletters you haven't opened in the last month. Reduce the noise.",
    },
    {
        "category": "Development",
        "suggestion": "Run 'brew outdated' and update 2-3 packages to stay current with security patches.",
    },
    {
        "category": "Planning",
        "suggestion": "Write down your top 3 priorities for today. Keep them visible while you work.",
    },
    {
        "category": "Tools",
        "suggestion": "Try the canvas feature for your next complex explanation. 'openclaw canvas present' to start.",
    },
    {
        "category": "Knowledge",
        "suggestion": "Document a process you performed recently in TOOLS.md or AGENTS.md for future reference.",
    },
    {
        "category": "Reflection",
        "suggestion": "Review your calendar for the past week. Look for patterns in how you spent your time.",
    },
    {
        "category": "Optimization",
        "suggestion": "Identify one manual task you did yesterday and explore how to automate it with a skill or script.",
    },
    {
        "category": "Collaboration",
        "suggestion": "Share a useful skill you've created with a colleague or friend. Good tools deserve to spread.",
    },
]


def get_daily_suggestions(count=2, seed=None):
    """
    Get daily suggestions.
    Uses day of month as seed for variety while keeping suggestions
    consistent throughout a single day.
    """
    if seed is None:
        seed = datetime.now().day
    
    # Create a deterministic shuffle based on the day
    rng = random.Random(seed)
    shuffled = SUGGESTIONS_POOL.copy()
    rng.shuffle(shuffled)
    
    # Return top N suggestions
    selected = shuffled[:count]
    
    return selected


def format_suggestions(suggestions):
    """Format suggestions for output."""
    lines = []
    for i, suggestion in enumerate(suggestions, 1):
        cat = suggestion['category']
        text = suggestion['suggestion']
        lines.append(f"   {i}. [{cat}] {text}")
    
    # Add leading spaces to align with other sections
    return '\n'.join(lines)


def get_suggestions(count=2):
    """Get formatted suggestions."""
    suggestions = get_daily_suggestions(count=count)
    return format_suggestions(suggestions)


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    print(get_suggestions(count=count))
