#!/usr/bin/env python3
"""
Title optimizer with CTR patterns
SECURITY MANIFEST:
  Environment variables accessed: none
  External endpoints called: none
  Local files read: none
  Local files written: none
"""
import sys
import json

PATTERNS = {
    'how-to': "How to [action] [topic] in [timeframe]",
    'list': "[number] [topic] Mistakes Costing You [result]",
    'question': "Is [topic] Worth It? An Honest Review",
    'story': "I [action] for [timeframe] — Here's What Happened",
    'comparison': "[topic A] vs [topic B]: Which Is Better?",
    'secret': "The [topic] Secret Nobody Talks About",
    'stop': "Stop [action] — Do This Instead"
}

def optimize_titles(topic, target_patterns=None):
    """Generate titles using proven patterns"""
    results = []
    patterns_to_use = target_patterns or list(PATTERNS.keys())[:5]
    
    for pattern_name in patterns_to_use:
        pattern = PATTERNS[pattern_name]
        # This would be more sophisticated with actual topic parsing
        title = pattern.replace('[topic]', topic)
        results.append({
            'pattern': pattern_name,
            'title': title,
            'estimated_ctr': 'high' if pattern_name in ['story', 'question'] else 'medium'
        })
    
    return json.dumps({"titles": results})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing topic"}))
        sys.exit(1)
    
    topic = sys.argv[1]
    print(optimize_titles(topic))