#!/usr/bin/env python3
"""
SECURITY MANIFEST:
- env: []
- endpoints: ["https://skillsearch-api.hagen-hoferichter.workers.dev/search"]
- read: []
- write: []
"""
import sys
import json
import urllib.request
import urllib.parse

API_URL = "https://skillsearch-api.hagen-hoferichter.workers.dev/search"

def search_skills(query):
    params = urllib.parse.urlencode({'q': query})
    url = f"{API_URL}?{params}"
    
    # Cloudflare often requires a User-Agent header
    req = urllib.request.Request(url, headers={'User-Agent': 'ClawHub-Skill/1.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data
            else:
                print(f"Error: API returned status {response.status}")
                return None
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return None

def format_results(data):
    if not data or 'results' not in data:
        print("No matching skills found in the global registry.")
        return

    count = data.get('count', 0)
    query = data.get('query', '')
    print(f"\n🚀 Discovered {count} skills/capabilities for: '{query}'\n")
    print("=" * 70)
    
    for i, result in enumerate(data['results'], 1):
        name = result.get('name', 'N/A')
        source = result.get('source', 'N/A')
        desc = result.get('description', 'No description provided.')
        if len(desc) > 200:
            desc = desc[:197] + "..."
            
        print(f"[{i}] {name}")
        print(f"    Description: {desc}")
        print(f"    Origin: {source}")
        print("-" * 70)

def main():
    if len(sys.argv) < 2:
        print("Usage: python search.py <query>")
        sys.exit(1)
        
    query = " ".join(sys.argv[1:])
    results = search_skills(query)
    format_results(results)

if __name__ == "__main__":
    main()
