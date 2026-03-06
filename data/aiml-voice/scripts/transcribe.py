#!/usr/bin/env python3
import argparse
import json
import os
import pathlib
import time
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://api.aimlapi.com/v1"
DEFAULT_USER_AGENT = "openclaw-skill-aimlapi-voice/1.1"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe audio via AIMLAPI async STT")
    parser.add_argument("file", help="Path to the audio file")
    parser.add_argument("--model", default="#g1_whisper-medium", help="Model reference")
    parser.add_argument("--language", help="ISO language code (e.g. 'en')")
    parser.add_argument("--out", help="Output file path")
    parser.add_argument("--poll-interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--max-wait", type=int, default=300, help="Max wait time in seconds")
    parser.add_argument("--apikey-file", help="Path to a file containing the API key")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="User-Agent header")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

def load_api_key(args: argparse.Namespace) -> str:
    api_key = os.getenv("AIMLAPI_API_KEY")
    if api_key:
        return api_key
    if args.apikey_file:
        key = pathlib.Path(args.apikey_file).read_text(encoding="utf-8").strip()
        if key:
            return key
    raise SystemExit("Missing AIMLAPI_API_KEY")

def request(url: str, api_key: str, method: str = "GET", data: bytes = None, headers: dict = None, user_agent: str = DEFAULT_USER_AGENT) -> Any:
    default_headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": user_agent,
        "Accept": "application/json",
    }
    if headers:
        default_headers.update(headers)
    
    req = urllib.request.Request(url, data=data, headers=default_headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8") if exc.fp else str(exc)
        raise SystemExit(f"Request failed: {exc.code} {detail}") from exc

def main() -> None:
    args = parse_args()
    api_key = load_api_key(args)
    file_path = pathlib.Path(args.file)
    
    if not file_path.exists():
        raise SystemExit(f"File not found: {args.file}")

    # Multipart generation
    boundary = "----Boundary" + str(int(time.time()))
    parts = []
    
    # Model & Options
    parts.append(f"--{boundary}")
    parts.append(f'Content-Disposition: form-data; name="model"')
    parts.append("")
    parts.append(args.model)
    
    if args.language:
        parts.append(f"--{boundary}")
        parts.append(f'Content-Disposition: form-data; name="language"')
        parts.append("")
        parts.append(args.language)
    
    # Audio file field
    parts.append(f"--{boundary}")
    parts.append(f'Content-Disposition: form-data; name="audio"; filename="{file_path.name}"')
    
    # Simple mime detection based on suffix
    mime = "audio/mpeg"
    if file_path.suffix.lower() == ".ogg": mime = "audio/ogg"
    elif file_path.suffix.lower() == ".wav": mime = "audio/wav"
    elif file_path.suffix.lower() == ".m4a": mime = "audio/mp4"
    
    parts.append(f"Content-Type: {mime}")
    parts.append("")
    
    header_body = "\r\n".join(parts).encode("utf-8") + b"\r\n"
    footer_body = b"\r\n--" + boundary.encode("utf-8") + b"--\r\n"
    body = header_body + file_path.read_bytes() + footer_body

    # 1. Create Task
    if args.verbose: print(f"[info] Creating STT task for {file_path.name}...")
    create_url = f"{DEFAULT_BASE_URL}/stt/create"
    res = request(create_url, api_key, method="POST", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, user_agent=args.user_agent)
    
    gen_id = res.get("id") or res.get("generation_id")
    if not gen_id:
        raise SystemExit(f"No generation id returned: {res}")
    
    if args.verbose: print(f"[info] Task created. ID: {gen_id}. Polling...")

    # 2. Poll Status
    start_time = time.time()
    while time.time() - start_time < args.max_wait:
        poll_url = f"{DEFAULT_BASE_URL}/stt/{gen_id}"
        status_res = request(poll_url, api_key, user_agent=args.user_agent)
        
        status = status_res.get("status")
        if args.verbose: print(f"[debug] Status: {status}")
        
        if status in ["waiting", "active", "queued", "pending"]:
            time.sleep(args.poll_interval)
            continue
        
        if status == "completed":
            try:
                # Deep nesting as per example: result['results']["channels"][0]["alternatives"][0]["transcript"]
                transcript = status_res["result"]["results"]["channels"][0]["alternatives"][0]["transcript"]
                if args.out:
                    pathlib.Path(args.out).write_text(transcript, encoding="utf-8")
                    print(f"Saved to {args.out}")
                else:
                    print(transcript)
                return
            except KeyError as exc:
                raise SystemExit(f"Success, but result structure unexpected: {exc}\n{json.dumps(status_res, indent=2)}")
        
        raise SystemExit(f"Unexpected status: {status}\n{json.dumps(status_res, indent=2)}")

    print("Timeout reached.")

if __name__ == "__main__":
    main()
