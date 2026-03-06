#!/usr/bin/env python3
"""
Telnyx RAG Memory - Semantic Search

Search your memory files using Telnyx AI similarity search.

Usage:
  ./search.py "What are David's preferences?"
  ./search.py "When did we set up voice calls?" --num 3
  ./search.py "project timeline" --json
  ./search.py "meetings" --priority   # Prioritize knowledge/ and skills/
  ./search.py "test" --bucket my-bucket  # Search specific bucket
"""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import time
import argparse
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "bucket": "chief-memory",
    "region": "us-central-1",
    "workspace": "/home/node/clawd",
    "priority_prefixes": ["memory/", "MEMORY.md"],
    "default_num_docs": 5,
}

def load_config():
    """Load configuration from file or defaults"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            user_config = json.load(f)
            return {**DEFAULT_CONFIG, **user_config}
    return DEFAULT_CONFIG

def load_credentials():
    """Load Telnyx API key from environment or .env file
    
    Returns:
        str: The Telnyx API key
        
    Raises:
        SystemExit: If no API key found
    """
    # Check environment first
    if os.environ.get("TELNYX_API_KEY"):
        return os.environ["TELNYX_API_KEY"]
    
    # Check for .env file in skill directory
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("TELNYX_API_KEY="):
                    return line.split("=", 1)[1].strip('"').strip("'")
    
    print("ERROR: No Telnyx API key found", file=sys.stderr)
    print("Set TELNYX_API_KEY environment variable or create .env file with:", file=sys.stderr)
    print("  TELNYX_API_KEY=your-api-key", file=sys.stderr)
    sys.exit(1)

def parse_telnyx_error(error_body):
    """Parse Telnyx API error response for better error messages
    
    Args:
        error_body (str): Raw error response body
        
    Returns:
        str: Human-readable error message
    """
    try:
        error_data = json.loads(error_body)
        if "errors" in error_data and error_data["errors"]:
            error = error_data["errors"][0]
            code = error.get("code", "unknown")
            detail = error.get("detail", "No details provided")
            return f"{code}: {detail}"
        elif "message" in error_data:
            return error_data["message"]
        else:
            return error_body.strip()
    except (json.JSONDecodeError, KeyError):
        return error_body.strip()

def similarity_search_with_retry(query, num_docs=5, bucket_name=None, timeout=30, max_retries=3):
    """Search memory using Telnyx similarity search API with retry logic
    
    Args:
        query (str): Search query text
        num_docs (int): Number of documents to return (default: 5)
        bucket_name (str): Override bucket name from config
        timeout (int): Request timeout in seconds (default: 30)
        max_retries (int): Maximum retry attempts (default: 3)
        
    Returns:
        dict: API response with search results or error info
    """
    config = load_config()
    api_key = load_credentials()
    
    # Use provided bucket or fall back to config
    bucket = bucket_name or config["bucket"]
    
    url = "https://api.telnyx.com/v2/ai/embeddings/similarity-search"
    
    payload = json.dumps({
        "bucket_name": bucket,
        "query": query,
        "num_docs": num_docs
    }).encode()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "openclaw-telnyx-rag/1.0"
    }
    
    # Retry with exponential backoff
    for attempt in range(max_retries):
        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_data = json.loads(response.read().decode())
                # Normalize API response format
                return normalize_api_response(response_data)
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='ignore')
            
            # Don't retry on certain error codes
            if e.code in [401, 403, 404]:
                return {
                    "error": f"HTTP {e.code}",
                    "details": parse_telnyx_error(error_body)
                }
            
            # Retry on 5xx errors or rate limits
            if attempt < max_retries - 1 and e.code >= 500:
                backoff = 2 ** attempt  # 1, 2, 4 seconds
                time.sleep(backoff)
                continue
            else:
                return {
                    "error": f"HTTP {e.code}",
                    "details": parse_telnyx_error(error_body)
                }
                
        except (urllib.error.URLError, OSError) as e:
            # Network errors - retry with backoff
            if attempt < max_retries - 1:
                backoff = 2 ** attempt
                time.sleep(backoff)
                continue
            else:
                return {"error": f"Network error: {str(e)}"}
        
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    return {"error": "Max retries exceeded"}

def normalize_api_response(response_data):
    """Normalize API response format for consistent handling
    
    Args:
        response_data (dict): Raw API response
        
    Returns:
        dict: Normalized response with consistent field names
    """
    # Handle both response formats consistently
    if "data" in response_data and isinstance(response_data["data"], list):
        normalized_data = []
        for doc in response_data["data"]:
            # Normalize field names
            normalized_doc = {
                "content": doc.get("document_chunk", doc.get("content", "")),
                "source": doc.get("metadata", {}).get("filename", doc.get("file_name", "unknown")),
                "certainty": doc.get("metadata", {}).get("certainty", doc.get("certainty", 0)),
                "distance": doc.get("distance", 0)
            }
            normalized_data.append(normalized_doc)
        
        return {"data": normalized_data}
    
    return response_data

def prioritize_results(results, priority_prefixes):
    """Re-rank results to prioritize certain directories
    
    Args:
        results (dict): Search results from API
        priority_prefixes (list): List of filename prefixes to prioritize
        
    Returns:
        dict: Results with re-ordered data array
    """
    if not results or "data" not in results:
        return results
    
    def priority_score(doc):
        filename = doc.get("source", "")
        for i, prefix in enumerate(priority_prefixes):
            if filename.startswith(prefix):
                return i  # Lower = higher priority
        return len(priority_prefixes)  # Non-priority files last
    
    def get_certainty(doc):
        return doc.get("certainty", 0)
    
    # Sort by priority first, then by certainty
    results["data"] = sorted(
        results["data"],
        key=lambda d: (priority_score(d), -get_certainty(d))
    )
    
    return results

def format_results(results, max_content_chars=500):
    """Format search results for display
    
    Args:
        results (dict): Search results from API
        max_content_chars (int): Maximum characters to display per result
        
    Returns:
        str: Formatted results string
    """
    if "error" in results:
        return f"❌ Error: {results['error']}\n{results.get('details', '')}"
    
    if "data" not in results or not results["data"]:
        return "No results found."
    
    output = []
    for i, doc in enumerate(results["data"], 1):
        certainty = doc.get("certainty", 0)
        filename = doc.get("source", "unknown")
        content = doc.get("content", "")
        
        # Truncate content if needed
        display_content = content[:max_content_chars]
        
        # Certainty indicator
        if certainty >= 0.9:
            conf = "🟢"
        elif certainty >= 0.85:
            conf = "🟡"
        else:
            conf = "🔴"
        
        output.append(f"--- Result {i} {conf} (certainty: {certainty:.3f}) ---")
        output.append(f"Source: {filename}")
        output.append(f"\n{display_content}")
        if len(content) > max_content_chars:
            output.append("...[truncated]")
        output.append("")
    
    return "\n".join(output)

def search_memory(query, num_docs=5, bucket_name=None, output_json=False, prioritize=True, timeout=30):
    """Main search function
    
    Args:
        query (str): Search query
        num_docs (int): Number of results to return
        bucket_name (str): Override bucket name
        output_json (bool): Return JSON instead of formatted text
        prioritize (bool): Apply priority ranking
        timeout (int): Request timeout in seconds
        
    Returns:
        str: Formatted results or JSON string
    """
    config = load_config()
    
    results = similarity_search_with_retry(
        query, 
        num_docs, 
        bucket_name, 
        timeout
    )
    
    if prioritize and "data" in results:
        results = prioritize_results(results, config.get("priority_prefixes", []))
    
    if output_json:
        return json.dumps(results, indent=2)
    else:
        return format_results(results)

def main():
    parser = argparse.ArgumentParser(description="Search memory with Telnyx RAG")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--num", "-n", type=int, default=5, help="Number of results")
    parser.add_argument("--bucket", "-b", help="Override bucket name from config")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--no-priority", action="store_true", help="Don't prioritize results")
    parser.add_argument("--full", "-f", action="store_true", help="Show full content")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Request timeout in seconds")
    
    args = parser.parse_args()
    
    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    query = " ".join(args.query)
    
    if not args.json:
        bucket_info = f" (bucket: {args.bucket})" if args.bucket else ""
        print(f"\n🔍 Searching: \"{query}\"{bucket_info}\n")
    
    results = search_memory(
        query=query,
        num_docs=args.num,
        bucket_name=args.bucket,
        output_json=args.json,
        prioritize=not args.no_priority,
        timeout=args.timeout
    )
    
    print(results)

if __name__ == "__main__":
    main()