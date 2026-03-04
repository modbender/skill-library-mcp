#!/usr/bin/env python3
"""
Trend analyzer using Tavily API
SECURITY MANIFEST:
  Environment variables accessed: TAVILY_API_KEY (only)
  External endpoints called: https://api.tavily.com/ (only)
  Local files read: none
  Local files written: none
"""
import os
import sys
import json
import requests

def analyze_trends(topic):
    """Search for trending angles on a topic"""
    api_key = os.environ.get('TAVILY_API_KEY')
    if not api_key:
        return {"error": "TAVILY_API_KEY not set"}
    
    response = requests.post(
        'https://api.tavily.com/search',
        json={
            'api_key': api_key,
            'query': f"{topic} YouTube viral topics 2026",
            'max_results': 3
        },
        timeout=10
    )
    
    if response.status_code != 200:
        return {"error": f"API error: {response.status_code}"}
    
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing topic"}))
        sys.exit(1)
    
    result = analyze_trends(sys.argv[1])
    print(json.dumps(result))