#!/usr/bin/env python3
"""Format NanoGPT web search output."""

import sys
import json


def format_output(data):
    """Format search results for display."""
    if "error" in data:
        print(f"Error: {data['error']}")
        sys.exit(1)
    
    metadata = data.get("metadata", {})
    print(f"\n🔍 Query: {metadata.get('query', 'N/A')}")
    print(f"📡 Provider: {metadata.get('provider', 'N/A')} ({metadata.get('depth', 'standard')})")
    print(f"💰 Cost: ${metadata.get('cost', 0)}")
    print("-" * 60)
    
    output_type = metadata.get("outputType", "searchResults")
    
    if output_type == "searchResults":
        results = data.get("data", [])
        for i, r in enumerate(results, 1):
            if r.get("type") == "text":
                print(f"\n{i}. {r.get('title', 'No title')}")
                print(f"   🔗 {r.get('url', '')}")
                snippet = r.get("snippet", "")
                if snippet:
                    print(f"   📝 {snippet[:200]}{'...' if len(snippet) > 200 else ''}")
            elif r.get("type") == "image":
                print(f"\n{i}. 🖼️ {r.get('title', 'Image')}")
                print(f"   🔗 {r.get('imageUrl', r.get('url', ''))}")
    
    elif output_type == "sourcedAnswer":
        answer_data = data.get("data", {})
        print(f"\n{answer_data.get('answer', 'No answer')}\n")
        sources = answer_data.get("sources", [])
        if sources:
            print("📚 Sources:")
            for s in sources:
                print(f"   • {s.get('name', 'Unknown')}: {s.get('url', '')}")


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
        format_output(data)
    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
