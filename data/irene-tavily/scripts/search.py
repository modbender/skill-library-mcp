#!/usr/bin/env python3
"""
Tavily Search Script for OpenClaw
Usage: python search.py "query" [options]
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timedelta

TAVILY_API_URL = "https://api.tavily.com/search"

def get_api_key():
    """Get Tavily API key from environment or config file."""
    # Check environment variable first
    api_key = os.environ.get('TAVILY_API_KEY')
    if api_key:
        return api_key
    
    # Check .env file in common locations
    env_paths = [
        os.path.expanduser('~/.openclaw/.env'),
        os.path.expanduser('~/.env'),
        '.env'
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('TAVILY_API_KEY='):
                        return line.strip().split('=', 1)[1].strip('"\'')
    
    return None

def search_tavily(query, max_results=5, search_depth="basic", 
                  include_answer=True, include_images=False, 
                  days=None, lang=None):
    """
    Perform a search using Tavily API.
    
    Args:
        query: Search query string
        max_results: Number of results (1-20)
        search_depth: "basic" or "advanced"
        include_answer: Include AI-generated answer
        include_images: Include related images
        days: Filter by last N days
        lang: Language preference ("zh" or "en")
    """
    api_key = get_api_key()
    if not api_key:
        return {
            "error": "TAVILY_API_KEY not found. Please set it in environment or ~/.openclaw/.env"
        }
    
    # Build request payload
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": min(max(1, max_results), 20),
        "search_depth": search_depth,
        "include_answer": include_answer,
        "include_images": include_images,
    }
    
    # Add time filter if specified
    if days:
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        payload["time_range"] = f"{from_date}.."
    
    # Add language hint
    if lang == "zh":
        payload["query"] = query  # Tavily handles Chinese well
    
    try:
        req = urllib.request.Request(
            TAVILY_API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'OpenClaw-Tavily-Search/1.0'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_data = json.loads(error_body)
            return {"error": error_data.get("detail", str(e))}
        except:
            return {"error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"error": str(e)}

def format_results(data, use_json=False):
    """Format search results for display."""
    if "error" in data:
        if use_json:
            return json.dumps({"error": data["error"]}, ensure_ascii=False, indent=2)
        return f"❌ Error: {data['error']}"
    
    if use_json:
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    # Text format
    output = []
    output.append(f"🔍 Tavily Search Results")
    output.append(f"Query: {data.get('query', 'N/A')}")
    output.append("")
    
    # AI Answer
    if data.get('answer'):
        output.append("🤖 AI Summary:")
        output.append(data['answer'])
        output.append("")
    
    # Results
    results = data.get('results', [])
    if results:
        output.append(f"📄 Found {len(results)} results:")
        output.append("")
        
        for i, result in enumerate(results, 1):
            output.append(f"{i}. {result.get('title', 'No title')}")
            output.append(f"   URL: {result.get('url', 'N/A')}")
            if result.get('content'):
                content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                output.append(f"   {content}")
            if result.get('published_date'):
                output.append(f"   📅 {result['published_date']}")
            output.append("")
    else:
        output.append("No results found.")
    
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description='Tavily Search for OpenClaw')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--max-results', type=int, default=5, help='Max results (1-20)')
    parser.add_argument('--search-depth', choices=['basic', 'advanced'], default='basic',
                       help='Search depth')
    parser.add_argument('--no-answer', action='store_true', help='Exclude AI answer')
    parser.add_argument('--include-images', action='store_true', help='Include images')
    parser.add_argument('--days', type=int, help='Filter by last N days')
    parser.add_argument('--lang', choices=['zh', 'en'], help='Language preference')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    result = search_tavily(
        query=args.query,
        max_results=args.max_results,
        search_depth=args.search_depth,
        include_answer=not args.no_answer,
        include_images=args.include_images,
        days=args.days,
        lang=args.lang
    )
    
    print(format_results(result, use_json=args.json))

if __name__ == '__main__':
    main()
