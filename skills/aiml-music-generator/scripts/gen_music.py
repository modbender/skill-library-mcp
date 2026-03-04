#!/usr/bin/env python3
import argparse
import json
import os
import pathlib
import time
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://api.aimlapi.com/v2"
DEFAULT_USER_AGENT = "openclaw-skill-aimlapi-music/1.1"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate music via AIMLAPI")
    parser.add_argument("--prompt", required=True, help="Music description")
    parser.add_argument("--model", default="minimax/music-2.0", help="Model")
    parser.add_argument("--lyrics", help="Lyrics for the song")
    parser.add_argument("--length", type=int, default=30000, help="Music length in ms")
    parser.add_argument("--out-dir", default="./out/music", help="Output directory")
    parser.add_argument("--poll-interval", type=int, default=15, help="Polling interval")
    parser.add_argument("--max-wait", type=int, default=1000, help="Max wait time")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

def load_api_key() -> str:
    key = os.getenv("AIMLAPI_API_KEY")
    if not key:
        raise SystemExit("Missing AIMLAPI_API_KEY")
    return key

def request(url: str, api_key: str, method: str = "GET", payload: dict = None) -> Any:
    data = json.dumps(payload).encode("utf-8") if payload else None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": DEFAULT_USER_AGENT,
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8")
        raise SystemExit(f"API Error ({e.code}): {detail}")

def download_file(url: str, path: pathlib.Path, user_agent: str, verbose: bool):
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    if verbose: print(f"Downloading: {url}")
    with urllib.request.urlopen(req) as res:
        path.write_bytes(res.read())

def main():
    args = parse_args()
    api_key = load_api_key()
    
    # 1. Start Generation
    payload = {
        "model": args.model,
        "prompt": args.prompt,
    }
    if args.lyrics: payload["lyrics"] = args.lyrics
    elif "minimax" in args.model: payload["lyrics"] = "[Instrumental]"
    
    if "elevenlabs" in args.model: payload["music_length_ms"] = args.length
    
    if args.verbose: print(f"Starting generation with model {args.model}...")
    gen_res = request(f"{DEFAULT_BASE_URL}/generate/audio", api_key, method="POST", payload=payload)
    
    gen_id = gen_res.get("id")
    if not gen_id:
        raise SystemExit(f"No ID returned: {gen_res}")
    
    if args.verbose: print(f"Generation ID: {gen_id}")

    # 2. Polling
    start_time = time.time()
    while time.time() - start_time < args.max_wait:
        poll_url = f"{DEFAULT_BASE_URL}/generate/audio?generation_id={gen_id}"
        status_res = request(poll_url, api_key)
        
        status = status_res.get("status")
        if args.verbose: print(f"Status: {status}. Checking again in {args.poll_interval} seconds.")
        
        if status in ["queued", "generating", "pending", "processing"]:
            time.sleep(args.poll_interval)
            continue
            
        if status == "completed":
            audio_url = status_res.get("audio_url")
            if not audio_url and "audio_file" in status_res:
                audio_url = status_res["audio_file"].get("url")
            
            if not audio_url:
                # Some models might have it in result nesting
                audio_url = status_res.get("audio", {}).get("url")

            if not audio_url:
                raise SystemExit(f"Completed but no audio URL found: {status_res}")
            
            # Download
            out_dir = pathlib.Path(args.out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            file_path = out_dir / f"music_{gen_id}.mp3"
            
            if args.verbose: print(f"Target path: {file_path}")
            download_file(audio_url, file_path, args.user_agent if hasattr(args, 'user_agent') else DEFAULT_USER_AGENT, args.verbose)
            
            print(f"SUCCESS: {file_path}")
            return
            
        if status == "failed":
            raise SystemExit(f"Generation failed: {status_res}")
            
        time.sleep(args.poll_interval)

    print("Timeout.")

if __name__ == "__main__":
    main()
