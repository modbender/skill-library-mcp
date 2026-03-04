#!/usr/bin/env python3
"""OpenClaw bridge responder for Maylo.

Watches bridge/request.json and writes bridge/response.json.
Instead of a stub response, it runs an actual OpenClaw agent turn locally:

  openclaw agent --agent milo --local --message <text> --json

This keeps everything on the Mac mini and avoids chat delivery side-effects.

Run (normally started by run_macmini.sh):
  source venv/bin/activate
  python bridge/milo_responder_openclaw.py

Env:
  MAYLO_OPENCLAW_AGENT_ID   (default: milo)
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "bridge"
REQ = BRIDGE / "request.json"
RESP = BRIDGE / "response.json"

AGENT_ID = (subprocess.os.getenv("MAYLO_OPENCLAW_AGENT_ID") or "milo").strip() or "milo"

print(f"OpenClaw responder running. agentId={AGENT_ID}. Waiting for request.json ...")

last_seen_id = None


def run_openclaw(message: str) -> str:
    # NOTE: --local runs embedded agent and returns JSON with payloads[].text
    cmd = [
        "openclaw",
        "agent",
        "--agent",
        AGENT_ID,
        "--local",
        "--message",
        message,
        "--json",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or f"openclaw agent failed ({p.returncode})")

    data = json.loads(p.stdout)
    payloads = data.get("payloads") or []
    if payloads and isinstance(payloads[0], dict) and isinstance(payloads[0].get("text"), str):
        return payloads[0]["text"].strip()

    # fallback: try other shapes
    if isinstance(data.get("text"), str):
        return data["text"].strip()

    return "(Cevap üretilemedi)"


while True:
    if REQ.exists():
        try:
            data = json.loads(REQ.read_text(encoding="utf-8"))
        except Exception:
            data = None

        if isinstance(data, dict) and data.get("id") and data.get("id") != last_seen_id:
            last_seen_id = data["id"]
            text = (data.get("text") or "").strip()
            print(f"\n[REQUEST {last_seen_id}] {text}")

            try:
                reply = run_openclaw(text)
            except Exception as e:
                reply = f"Bir hata oldu: {e}"

            RESP.write_text(
                json.dumps({"id": last_seen_id, "text": reply}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"[RESPONSE {last_seen_id}] written")

    time.sleep(0.2)
