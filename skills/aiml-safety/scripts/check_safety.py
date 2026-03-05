#!/usr/bin/env python3
import argparse
import json
import os
import requests

DEFAULT_MODEL = "meta-llama/LlamaGuard-2-8b"

def parse_args():
    parser = argparse.ArgumentParser(description="Check content safety via AIMLAPI")
    parser.add_argument("--content", required=True, help="Text to check for safety")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Safety model ID")
    parser.add_argument("--verbose", action="store_true", help="Show full API response")
    return parser.parse_args()

DEFAULT_USER_AGENT = "openclaw-aimlapi-safety/1.0"

def check_safety(content, model, user_agent=DEFAULT_USER_AGENT):
    api_key = os.getenv("AIMLAPI_API_KEY")
    if not api_key:
        print("Error: AIMLAPI_API_KEY environment variable not set.")
        return None

    url = "https://api.aimlapi.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": user_agent
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": content}
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    args = parse_args()
    result = check_safety(args.content, args.model)
    
    if result:
        answer = result['choices'][0]['message']['content'].strip().lower()
        is_safe = "unsafe" not in answer
        
        status = "SAFE" if is_safe else "UNSAFE"
        print(f"Status: {status}")
        print(f"Analysis: {answer}")
        
        if args.verbose:
            print("\nFull Response:")
            print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
