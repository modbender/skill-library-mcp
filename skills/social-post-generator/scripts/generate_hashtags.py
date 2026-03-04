#!/usr/bin/env python3
"""
Generate relevant hashtags from a topic keyword.
Usage: python generate_hashtags.py "your topic here"

Note: This script requires internet access to fetch trending data.
For offline use, use the built-in hashtag suggestions in SKILL.md.
"""

import sys
import urllib.request
import json

def generate_hashtags(topic, count=15):
    """
    Generate hashtags for a given topic.
    In production, this would call Twitter/Instagram APIs.
    For now, returns smart combinations based on topic.
    """
    # Clean topic
    topic_clean = topic.lower().replace(" ", "")
    
    # Generate variations
    hashtags = [
        f"#{topic_clean}",
        f"#{topic_clean}tips",
        f"#{topic_clean}life",
        f"#{topic_clean}community",
    ]
    
    # Add broad category tags based on topic keywords
    broad_tags = {
        "tech": ["#technology", "#tech", "#innovation"],
        "business": ["#business", "#entrepreneur", "#startup"],
        "marketing": ["#marketing", "#digitalmarketing", "#contentmarketing"],
        "fitness": ["#fitness", "#workout", "#health"],
        "food": ["#food", "#foodie", "#recipe"],
        "travel": ["#travel", "#wanderlust", "#adventure"],
    }
    
    for keyword, tags in broad_tags.items():
        if keyword in topic.lower():
            hashtags.extend(tags)
    
    return hashtags[:count]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_hashtags.py \"your topic\"")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    tags = generate_hashtags(topic)
    
    print(f"Hashtags for: {topic}")
    print(" ".join(tags))
