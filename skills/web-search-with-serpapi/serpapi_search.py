import serpapi
import os
from typing import Optional

def serpapi_search(query: str, engine: str = "google") -> Optional[str]:
    # Get API key from environment variable or use default
    api_key = os.getenv("SERPAPI_API_KEY", "")
    if not api_key:
        return "Error: SerpAPI key not found. Set SERPAPI_API_KEY environment variable."

    try:
        client = serpapi.Client(api_key=api_key)
        results = client.search(q=query, engine=engine)
        return results.get("text_blocks", "No results found.")
    except Exception as e:
        return f"Search failed: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python serpapi_search.py <query> [engine]")
        sys.exit(1)
    query = sys.argv[1]
    engine = sys.argv[2] if len(sys.argv) > 2 else "google"
    print(serpapi_search(query, engine))
