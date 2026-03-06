#!/usr/bin/env python3
"""Scrapling smoke test / mini-extractor.

Usage:
  python scrapling_smoke_test.py URL [URL ...] --fetcher fetcher|stealthy|dynamic [--extract next_data]

Notes:
- Dynamic fetcher requires Playwright browsers: `playwright install chromium`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Iterable


def _pick_fetcher(kind: str):
    kind = kind.lower().strip()
    if kind == "fetcher":
        from scrapling.fetchers import Fetcher

        return ("Fetcher", lambda url, **kw: Fetcher.get(url, **kw))
    if kind == "stealthy":
        from scrapling.fetchers import StealthyFetcher

        return (
            "StealthyFetcher",
            lambda url, **kw: StealthyFetcher.fetch(url, **kw),
        )
    if kind == "dynamic":
        from scrapling.fetchers import DynamicFetcher

        return (
            "DynamicFetcher",
            lambda url, **kw: DynamicFetcher.fetch(url, **kw),
        )
    raise SystemExit(f"Unknown --fetcher kind: {kind}")


def _extract_next_data(html: str) -> dict[str, Any] | None:
    m = re.search(
        r'__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def _find_strings(obj: Any, needles: Iterable[str]) -> list[tuple[str, str]]:
    needles = list(needles)
    out: list[tuple[str, str]] = []

    def walk(x: Any, path: str):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, f"{path}/{k}")
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")
        else:
            if isinstance(x, str) and any(n in x for n in needles):
                out.append((path, x))

    walk(obj, "")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+", help="One or more URLs")
    ap.add_argument(
        "--fetcher",
        default="fetcher",
        choices=["fetcher", "stealthy", "dynamic"],
        help="Which Scrapling fetcher to use",
    )
    ap.add_argument(
        "--extract",
        default="none",
        choices=["none", "next_data"],
        help="Optional specialized extraction",
    )
    ap.add_argument("--timeout", type=int, default=60, help="Timeout seconds")
    ap.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="(Dynamic/Stealthy) headless browser",
    )

    args = ap.parse_args()

    fetcher_name, fetch = _pick_fetcher(args.fetcher)

    for url in args.urls:
        print(f"\n=== {url}")
        print(f"fetcher: {fetcher_name}")

        kw = {}
        if args.fetcher in ("stealthy", "dynamic"):
            kw.update(
                {
                    "headless": bool(args.headless),
                    "network_idle": True,
                }
            )
        if args.fetcher == "fetcher":
            kw.update({"timeout": args.timeout})
        else:
            # milliseconds for Playwright-based fetchers
            kw.update({"timeout": args.timeout * 1000})

        try:
            resp = fetch(url, **kw)
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            continue

        status = getattr(resp, "status", None)
        html = getattr(resp, "html_content", None) or ""

        print("status:", status)
        print("html_len:", len(html))

        # quick indicators
        low = html.lower()
        for needle in [
            "something went wrong",
            "enable javascript",
            "turnstile",
            "captcha",
            "access denied",
        ]:
            if needle in low:
                print("indicator:", needle)

        # meta/title
        try:
            title = resp.css("title::text").get()
        except Exception:
            title = None
        if title:
            print("title:", title[:240])

        if args.extract == "next_data":
            nd = _extract_next_data(html)
            if not nd:
                print("next_data: not found")
            else:
                hits = _find_strings(nd, ["Yapay", "Üretken", "Atölye", "Atolye"])
                print("next_data: found, hits:", len(hits))
                for p, s in hits[:25]:
                    s1 = s.replace("\n", " ").strip()
                    print(" ", p, "=>", s1[:240])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
