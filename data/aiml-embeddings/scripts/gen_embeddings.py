#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://api.aimlapi.com/v1"
DEFAULT_USER_AGENT = "openclaw-aimlapi-embeddings/1.0"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate embeddings via AIMLAPI /v1/embeddings")
    parser.add_argument("--input", required=True, help="Input text to embed")
    parser.add_argument("--model", default="text-embedding-3-large", help="Model reference")
    parser.add_argument("--dimensions", type=int, help="The number of dimensions the resulting output embeddings should have")
    parser.add_argument("--encoding-format", default="float", choices=["float", "base64"], help="The format in which to return the embeddings")
    parser.add_argument("--out-dir", default="./out/embeddings", help="Output directory")
    parser.add_argument("--timeout", type=int, default=60, help="Request timeout in seconds")
    parser.add_argument("--apikey-file", default=None, help="Path to a file containing the API key")
    parser.add_argument("--retry-max", type=int, default=3, help="Retry attempts on failure")
    parser.add_argument("--retry-delay", type=float, default=1.0, help="Retry delay (seconds)")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="User-Agent header")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

def load_api_key(args: argparse.Namespace) -> str:
    api_key = os.getenv("AIMLAPI_API_KEY")
    if api_key: return api_key
    if args.apikey_file:
        key = pathlib.Path(args.apikey_file).read_text(encoding="utf-8").strip()
        if key: return key
    raise SystemExit("Missing AIMLAPI_API_KEY")

def request_json(url, payload, api_key, timeout, retry_max, retry_delay, user_agent, verbose):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": user_agent,
    }, method="POST")
    attempt = 0
    while True:
        try:
            if verbose: print(f"[debug] POST {url} attempt {attempt + 1}")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            if attempt < retry_max:
                attempt += 1
                time.sleep(retry_delay)
                continue
            raise SystemExit(f"Request failed: {exc}")

def main() -> None:
    args = parse_args()
    api_key = load_api_key(args)
    
    payload = {
        "model": args.model,
        "input": args.input,
        "encoding_format": args.encoding_format,
    }
    if args.dimensions:
        payload["dimensions"] = args.dimensions

    url = f"{DEFAULT_BASE_URL.rstrip('/')}/embeddings"
    response = request_json(url, payload, api_key, args.timeout, args.retry_max, args.retry_delay, args.user_agent, args.verbose)
    
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"embedding-{int(time.time())}.json"
    file_path = out_dir / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2)
        
    print(f"SUCCESS: Result saved to {file_path}")
    if args.verbose:
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()
