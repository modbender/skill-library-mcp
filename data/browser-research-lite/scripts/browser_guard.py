#!/usr/bin/env python3
import argparse
import glob
import json
import os
import subprocess
from typing import Dict, List


def recent_files(pattern: str, limit: int) -> List[str]:
    files = glob.glob(pattern)
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[:limit]


def read_tail(path: str, max_bytes: int = 20000) -> str:
    try:
        size = os.path.getsize(path)
        start = max(0, size - max_bytes)
        with open(path, "rb") as f:
            f.seek(start)
            return f.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sessions-dir", default=os.path.expanduser("~/.openclaw/agents/main/sessions"))
    p.add_argument("--file-limit", type=int, default=12)
    p.add_argument("--unavailable-threshold", type=int, default=2)
    args = p.parse_args()

    pattern = os.path.join(args.sessions_dir, "hle_eval_*.jsonl")
    files = recent_files(pattern, args.file_limit)
    browser_calls = 0
    unavailable_hits = 0

    for fp in files:
        tail = read_tail(fp)
        if not tail:
            continue
        browser_calls += tail.count('"toolName":"browser"') + tail.count('"name":"browser"')
        unavailable_hits += tail.lower().count("no connected browser-capable nodes")

    cli_running = None
    cli_cdp_ready = None
    cli_error = ""
    try:
        proc = subprocess.run(
            ["openclaw", "browser", "status", "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        # Extract first JSON object from noisy output.
        out = proc.stdout or ""
        lb = out.find("{")
        rb = out.rfind("}")
        if lb != -1 and rb != -1 and rb > lb:
            obj = json.loads(out[lb : rb + 1])
            cli_running = bool(obj.get("running"))
            cli_cdp_ready = bool(obj.get("cdpReady"))
    except Exception as e:
        cli_error = str(e)

    available_by_logs = unavailable_hits < args.unavailable_threshold
    cli_status_known = (cli_running is not None) or (cli_cdp_ready is not None)
    if cli_status_known:
        cli_ok = (cli_running is True) and (cli_cdp_ready is True)
    else:
        cli_ok = False if cli_error else True
    available = available_by_logs and cli_ok
    payload: Dict[str, object] = {
        "ok": True,
        "browser_available": available,
        "browser_calls_recent": browser_calls,
        "unavailable_hits_recent": unavailable_hits,
        "scanned_files": len(files),
        "browser_running": cli_running,
        "browser_cdp_ready": cli_cdp_ready,
        "cli_error": cli_error,
        "recommendation": (
            "browser_ok_use_once_then_verify"
            if available
            else "skip_browser_use_local_python_or_non_browser_sources_and_fix_browser_attach"
        ),
    }
    print(json.dumps(payload, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

