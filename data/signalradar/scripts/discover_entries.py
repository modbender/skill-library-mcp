#!/usr/bin/env python3
"""Semi-automatic topic discovery for Polymarket entries."""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from typing import Any


def _parse_outcome_price(raw: Any) -> str:
    """Parse outcomePrices (JSON string or list) to first price string."""
    if isinstance(raw, str) and raw.startswith("["):
        try:
            parsed = json.loads(raw)
            return str(parsed[0]) if parsed else ""
        except (json.JSONDecodeError, ValueError, IndexError):
            return ""
    if isinstance(raw, list) and raw:
        return str(raw[0])
    return ""


def fetch_markets(limit: int, timeout: int) -> list[dict[str, Any]]:
    url = f"https://gamma-api.polymarket.com/markets?active=true&closed=false&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "signalradar/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    return []


def tokenize(text: str) -> set[str]:
    cleaned = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return {t for t in cleaned.split() if len(t) >= 3}


def score(topic_tokens: set[str], question: str, description: str) -> float:
    cand_tokens = tokenize(question + " " + description)
    if not topic_tokens or not cand_tokens:
        return 0.0
    inter = len(topic_tokens & cand_tokens)
    union = len(topic_tokens | cand_tokens)
    if union == 0:
        return 0.0
    jaccard = inter / union
    contain_bonus = 0.0
    combined = (question + " " + description).lower()
    for token in topic_tokens:
        if token in combined:
            contain_bonus += 0.04
    return min(1.0, jaccard + contain_bonus)


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover candidate entries from a natural-language topic")
    parser.add_argument("--topic", required=True, help="Natural-language topic")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--min-score", type=float, default=0.03)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args()

    topic_tokens = tokenize(args.topic)
    markets = fetch_markets(args.limit, args.timeout)
    ranked: list[dict[str, Any]] = []
    for m in markets:
        q = str(m.get("question", "") or m.get("title", "")).strip()
        if not q:
            continue
        desc = str(m.get("description", ""))
        rel = score(topic_tokens, q, desc)
        if rel < args.min_score:
            continue
        ranked.append(
            {
                "question": q,
                "slug": str(m.get("slug", "")),
                "end_date": str(m.get("endDate", "") or "")[:10],
                "probability": _parse_outcome_price(m.get("outcomePrices")),
                "relevance_score": round(rel, 4),
            }
        )
    ranked.sort(key=lambda x: x["relevance_score"], reverse=True)
    ranked = ranked[: args.top_k]

    output = {
        "topic": args.topic,
        "candidate_count": len(ranked),
        "candidates": ranked,
        "next_step": "请人工确认后将条目写入 SignalRadar_Manual_Entries",
    }
    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
