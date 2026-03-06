#!/usr/bin/env python3
"""Generate daily recommendation artifact under data/."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
sys.path.insert(0, str(ROOT))

from tools.fusion_engine import short_term_signal_engine  # noqa: E402


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate A-share short-term recommendation")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="analysis date YYYY-MM-DD")
    parser.add_argument("--top-n", type=int, default=5)
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    signal = short_term_signal_engine(analysis_date=args.date)
    candidates = signal.get("candidates", [])[: max(args.top_n, 0)]

    report = {
        "title": f"A-share recommendation for {args.date}",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_date": args.date,
        "signal": signal.get("signal"),
        "score": signal.get("score"),
        "confidence": signal.get("confidence"),
        "holding_days": signal.get("holding_days"),
        "has_recommendation": signal.get("has_recommendation", False),
        "no_recommendation_message": signal.get("no_recommendation_message"),
        "factor_breakdown": signal.get("factor_breakdown", {}),
        "top_sectors": signal.get("top_sectors", []),
        "candidates": candidates,
    }

    dated_path = DATA_DIR / f"today_recommendation_{args.date}.json"
    latest_path = DATA_DIR / "today_recommendation.latest.json"
    save_json(dated_path, report)
    save_json(latest_path, report)

    print(f"saved: {dated_path}")
    print(f"saved: {latest_path}")


if __name__ == "__main__":
    main()
