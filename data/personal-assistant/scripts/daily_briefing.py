#!/usr/bin/env python3
"""
Personal daily briefing generator.
Usage: python3 daily_briefing.py --location Columbus --output briefing.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone

def generate_briefing(location="Columbus"):
    """
    Generate a personalized daily briefing.

    This focuses on personal productivity, routine, and well-being.
    """

    briefing = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'location': location,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'weekday': datetime.now().strftime('%A'),
        'sections': []
    }

    # Morning motivation
    briefing['sections'].append({
        'title': '🌅 Good Morning!',
        'content': 'Start your day with focus and intention.',
        'type': 'motivation'
    })

    # Weather reminder
    briefing['sections'].append({
        'title': '🌡 Weather Check',
        'content': f'Check the weather in {location} before heading out. Plan your day accordingly.',
        'type': 'weather'
    })

    # Priority tasks
    briefing['sections'].append({
        'title': '🎯 Today\'s Focus',
        'content': '''Top 3 priorities:
1. _______________________________________
2. _______________________________________
3. _______________________________________

Tip: Start with the hardest task first.''',
        'type': 'priorities'
    })

    # Habit tracking
    briefing['sections'].append({
        'title': '✅ Daily Habits',
        'content': '''Today's habits:
□ Morning routine (exercise, meditation, journal)
□ Hydration goals (8 glasses)
□ Learning time (30 min reading/course)
□ Evening review (what went well?)''',
        'type': 'habits'
    })

    # Self-care reminder
    briefing['sections'].append({
        'title': '💚 Self-Care',
        'content': '''Remember:
• Take breaks and rest your eyes
• Step away from screens for 5 min/hour
• Stay hydrated
• End work at a reasonable time''',
        'type': 'selfcare'
    })

    # Evening reflection
    briefing['sections'].append({
        'title': '🌙 Evening Review',
        'content': '''Before bed:
1. What did I accomplish today?
2. What am I grateful for?
3. What could I have done better?
4. Tomorrow's top priority?''',
        'type': 'reflection'
    })

    return briefing

def format_briefing(briefing):
    """Format briefing for human-readable output."""
    output = f"📋 Daily Briefing - {briefing['date']} ({briefing['weekday']})\n\n"

    for section in briefing['sections']:
        output += f"{section['title']}\n"
        if section['type'] in ['priorities', 'habits', 'reflection']:
            output += section['content'] + "\n"
        else:
            output += section['content'] + "\n"
        output += "\n"

    return output

def save_briefing(briefing, output_file='daily_briefing.json'):
    """Save briefing to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(briefing, f, indent=2, ensure_ascii=False)
    print(f"Saved briefing to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate personal daily briefing')
    parser.add_argument('--location', default='Columbus', help='Your location for weather context')
    parser.add_argument('--output', default='daily_briefing.json', help='Output file')
    parser.add_argument('--summary', action='store_true', help='Print human-readable summary')

    args = parser.parse_args()

    briefing = generate_briefing(args.location)

    if args.summary:
        print(format_briefing(briefing))

    save_briefing(briefing, args.output)

if __name__ == '__main__':
    main()
