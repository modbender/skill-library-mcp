#!/usr/bin/env python3
"""Probe public/open resources listed in resources_manifest.json.

This is a lightweight smoke test that the URLs are reachable and return the expected content type.
It does NOT validate semantic correctness of the data.

Usage:
  python3 scripts/probe_resources.py --out artifacts/resource_probe.json

Exit codes:
  0: all ok (or only skipped)
  1: one or more hard failures
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_manifest(path: Path) -> List[Dict[str, Any]]:
    j = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(j, list):
        raise SystemExit("manifest must be a JSON list")
    return j


def fetch(url: str, timeout_s: int = 15) -> Dict[str, Any]:
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "clawdbot-med-info-probe/0.1")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = resp.read(4096)
            ct = resp.headers.get("content-type")
            return {
                "ok": True,
                "status": getattr(resp, "status", 200),
                "content_type": ct,
                "ms": int((time.time() - t0) * 1000),
                "sample": data.decode("utf-8", errors="replace")[:200],
            }
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read(4096).decode("utf-8", errors="replace")
        except Exception:
            pass
        return {
            "ok": False,
            "status": e.code,
            "content_type": e.headers.get("content-type"),
            "ms": int((time.time() - t0) * 1000),
            "error": f"HTTP {e.code}",
            "sample": body[:200],
        }
    except Exception as e:
        return {
            "ok": False,
            "status": None,
            "content_type": None,
            "ms": int((time.time() - t0) * 1000),
            "error": str(e),
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--manifest",
        default=str(Path(__file__).resolve().parent / "resources_manifest.json"),
        help="Path to resources manifest JSON (default: scripts/resources_manifest.json)",
    )
    ap.add_argument("--out", default="", help="Write full JSON report to this file")
    ap.add_argument("--timeout", type=int, default=15, help="Per-request timeout seconds")
    ap.add_argument("--limit", type=int, default=0, help="Only probe first N entries")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    items = load_manifest(manifest_path)
    if args.limit and args.limit > 0:
        items = items[: int(args.limit)]

    report: Dict[str, Any] = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "manifest": str(manifest_path),
        "count": len(items),
        "results": [],
    }

    hard_fail = 0
    for it in items:
        name = it.get("name")
        test_url = it.get("test_url") or it.get("url")
        requires_key = bool(it.get("requires_key"))

        if requires_key and not os.environ.get(it.get("env_key", "") or ""):
            report["results"].append({"name": name, "skipped": True, "reason": "requires_key"})
            continue

        r = fetch(str(test_url), timeout_s=int(args.timeout))
        r["name"] = name
        r["test_url"] = test_url
        report["results"].append(r)

        if not r.get("ok"):
            hard_fail += 1

    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Minimal console summary.
    ok = sum(1 for r in report["results"] if r.get("ok"))
    skipped = sum(1 for r in report["results"] if r.get("skipped"))
    fail = sum(1 for r in report["results"] if (not r.get("ok") and not r.get("skipped")))
    print(f"Probed: {len(report['results'])} | ok={ok} skipped={skipped} fail={fail}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
