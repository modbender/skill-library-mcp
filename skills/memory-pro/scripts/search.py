#!/usr/bin/env python3
import sys
import json
import argparse
import os
import time
import logging
import urllib.request
import urllib.error

# --- Configuration ---
DEFAULT_API_URL = "http://127.0.0.1:8001/search"
API_URL = os.getenv("MEMORY_PRO_API_URL", DEFAULT_API_URL)
TIMEOUT = int(os.getenv("MEMORY_PRO_TIMEOUT", 10))
# Increase retry attempts for slower starts (e.g. index rebuild)
MAX_RETRIES = 10 
RETRY_DELAY = 2  # seconds

# --- Logging ---
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')
logger = logging.getLogger("memory-pro-client")

def search_semantic(query, top_k=3, json_output=False):
    """
    Query the semantic search API with retry logic.
    """
    url = API_URL
    
    payload = {
        "query": query,
        "top_k": top_k
    }
    data = json.dumps(payload).encode('utf-8')
    headers = {"Content-Type": "application/json"}
    
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                response_body = response.read().decode('utf-8')
                return json.loads(response_body)

        except urllib.error.URLError as e:
            if isinstance(e.reason, ConnectionRefusedError) or "Connection refused" in str(e.reason):
                if attempt < MAX_RETRIES - 1:
                    if not json_output:
                        sys.stderr.write(f"Connection failed, retrying ({attempt+1}/{MAX_RETRIES})...\n")
                    time.sleep(RETRY_DELAY)
                else:
                    if not json_output:
                        logger.error(f"Could not connect to Memory Pro service at {url}. Is it running?")
                    sys.exit(1)
            else:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"URL Error: {e.reason}")
                    sys.exit(1)
                    
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP Error: {e.code} - {e.reason}")
            sys.exit(1)
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from server.")
            sys.exit(1)
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sys.exit(1)

def main():
    global API_URL
    
    parser = argparse.ArgumentParser(description="Query Memory Pro semantic search.")
    parser.add_argument("query", help="The search query string.")
    parser.add_argument("--top_k", "-k", type=int, default=3, help="Number of results to return.")
    parser.add_argument("--json", "-j", action="store_true", help="Output raw JSON.")
    parser.add_argument("--url", help="Override API URL", default=None)
    
    args = parser.parse_args()
    
    if args.url:
        API_URL = args.url
    
    result = search_semantic(args.query, args.top_k, args.json)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n🔍 Search results for: '{args.query}'\n")
        results = result.get("results", [])
        
        if not results:
            print("No relevant memories found.")
        else:
            for i, item in enumerate(results, 1):
                if isinstance(item, dict):
                    score = item.get("score", 0.0)
                    sentence = item.get("sentence", "").strip()
                else:
                    score = 0.0
                    sentence = str(item)
                    
                print(f"{i}. [Score: {score:.2f}]")
                print(f"   {sentence}")
                print("-" * 40)

if __name__ == "__main__":
    main()
