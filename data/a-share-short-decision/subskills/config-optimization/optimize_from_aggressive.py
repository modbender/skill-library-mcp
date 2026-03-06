#!/usr/bin/env python3
"""Optimize aggressive screener config and store artifacts under data/."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_screener(config_payload: Dict[str, Any]) -> Dict[str, Any]:
    strategy = config_payload.get("strategy")
    if isinstance(strategy, dict):
        screener = strategy.get("screener")
        if isinstance(screener, dict):
            return deepcopy(screener)
    return deepcopy(config_payload)


def optimize_screener(aggressive: Dict[str, Any]) -> Dict[str, Any]:
    optimized = deepcopy(aggressive)
    optimized["prefilter_change_pct"] = 2.8
    optimized["min_change_pct"] = 3.2
    optimized["min_volume_ratio"] = 1.15
    optimized["trend_lookback"] = 2
    optimized["min_history_days"] = 5
    optimized["volume_baseline_days"] = 4
    optimized["high_volume_bearish_drop_pct"] = -3.8
    optimized["high_volume_bearish_vol_ratio"] = 2.8

    historical_mode = optimized.get("historical_mode")
    if not isinstance(historical_mode, dict):
        historical_mode = {}
    historical_mode["min_change_pct"] = 1.8
    historical_mode["trend_lookback"] = 2
    historical_mode["min_volume_ratio"] = 1.05
    historical_mode["high_volume_bearish_drop_pct"] = -4.2
    historical_mode["high_volume_bearish_vol_ratio"] = 3.0
    historical_mode["relaxed_pick_from_pool_when_empty"] = True
    optimized["historical_mode"] = historical_mode
    return optimized


def build_report(period: str, input_path: Path, optimized: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_period": period,
        "source_config": str(input_path),
        "optimized_screener": optimized,
        "notes": [
            "Lowered prefilter and min_change to increase candidate coverage in mild-volatility sessions.",
            "Raised min_volume_ratio slightly to preserve liquidity quality.",
            "Relaxed bearish high-volume exclusion to reduce false negatives.",
        ],
    }


def write_summary(path: Path, period: str, optimized: Dict[str, Any]) -> None:
    lines = [
        "# Config Optimization Summary",
        "",
        f"- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Analysis period: {period}",
        "- Model: aggressive -> optimized",
        "",
        "## Optimized Screener",
        "```json",
        json.dumps(optimized, ensure_ascii=False, indent=2),
        "```",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimize aggressive config for short-term A-share strategy")
    parser.add_argument("--base-config", default="config.json", help="Base full config path")
    parser.add_argument(
        "--aggressive-config",
        default="config_aggressive_optimized_full.json",
        help="Input aggressive full config path (or pure screener json)",
    )
    parser.add_argument("--analysis-period", default="2026-02-01 to 2026-02-12")
    parser.add_argument("--apply-to-config", action="store_true", help="Overwrite base config with optimized full config")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    base_path = (ROOT / args.base_config).resolve()
    input_path = (ROOT / args.aggressive_config).resolve()

    base_cfg = load_json(base_path)
    input_cfg = load_json(input_path)

    screener_input = extract_screener(input_cfg)
    optimized_screener = optimize_screener(screener_input)

    optimized_full = deepcopy(base_cfg)
    optimized_full.setdefault("strategy", {})
    optimized_full["strategy"].setdefault("screener", {})
    optimized_full["strategy"]["screener"] = optimized_screener
    optimized_full["version"] = "1.1.0-optimized"
    optimized_full["optimization_info"] = {
        "base_date": datetime.now().strftime("%Y-%m-%d"),
        "analysis_period": args.analysis_period,
        "config_type": "aggressive_optimized",
    }

    optimized_screener_path = DATA_DIR / "config_aggressive_optimized.json"
    optimized_full_path = DATA_DIR / "config_aggressive_optimized_full.json"
    report_path = DATA_DIR / "config_analysis_report.latest.json"
    summary_path = DATA_DIR / "config_summary.latest.md"

    save_json(optimized_screener_path, optimized_screener)
    save_json(optimized_full_path, optimized_full)
    save_json(report_path, build_report(args.analysis_period, input_path, optimized_screener))
    write_summary(summary_path, args.analysis_period, optimized_screener)

    if args.apply_to_config:
        save_json(base_path, optimized_full)

    print(f"saved: {optimized_screener_path}")
    print(f"saved: {optimized_full_path}")
    print(f"saved: {report_path}")
    print(f"saved: {summary_path}")
    if args.apply_to_config:
        print(f"updated: {base_path}")


if __name__ == "__main__":
    main()
