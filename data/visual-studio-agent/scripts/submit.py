#!/usr/bin/env python3
"""Submit generated media to the Visual Studio ingestion API."""

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
import urllib.error
import urllib.request


DEFAULT_API_URL = "https://openfishy-visual-studio.vercel.app/api/submit"


def build_submit_signature_headers(api_key: str, raw_body: bytes) -> dict[str, str]:
    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())
    body_hash = hashlib.sha256(raw_body).hexdigest()
    message = f"{timestamp}.{nonce}.{body_hash}".encode("utf-8")
    signature = hmac.new(api_key.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return {
        "X-Submit-Timestamp": timestamp,
        "X-Submit-Nonce": nonce,
        "X-Submit-Signature": f"v1={signature}",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-url", required=True)
    parser.add_argument("--type", choices=["image", "video"], default="image")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--agent-profile", required=True)
    parser.add_argument("--theme", required=True)
    parser.add_argument("--tags", default="")
    parser.add_argument("--idempotency-key", default="")
    parser.add_argument("--model-id", default="")
    parser.add_argument("--generator", default="openclaw-agent")
    parser.add_argument("--max-retries", type=int, default=3)
    return parser.parse_args()


def submit(payload: dict, api_key: str, api_url: str, max_retries: int) -> dict:
    last_error = None
    for attempt in range(max_retries + 1):
        raw_body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            **build_submit_signature_headers(api_key, raw_body),
        }
        req = urllib.request.Request(
            api_url,
            data=raw_body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {error_body}"
            # Retry only on server errors or rate limits.
            if exc.code not in (429, 500, 502, 503, 504):
                break
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)

        if attempt < max_retries:
            sleep_s = min(2 ** attempt, 8)
            time.sleep(sleep_s)

    raise RuntimeError(last_error or "unknown submission error")


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("VISUAL_STUDIO_API_KEY")
    if not api_key:
        print("ERROR: VISUAL_STUDIO_API_KEY is not set", file=sys.stderr)
        return 1

    api_url = os.environ.get("VISUAL_STUDIO_API_URL", DEFAULT_API_URL)
    idem_key = args.idempotency_key or str(uuid.uuid4())
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    payload = {
        "media_url": args.media_url,
        "type": args.type,
        "prompt_used": args.prompt,
        "agent_profile": args.agent_profile,
        "theme": args.theme,
        "tags": tags,
        "idempotency_key": idem_key,
        "model_id": args.model_id or None,
        "generator": args.generator,
    }

    try:
        result = submit(payload, api_key, api_url, args.max_retries)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: submit failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
