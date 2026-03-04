#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full vnstock free-tier valuation pipeline")
    parser.add_argument("--source", default="kbs", choices=["kbs", "vci"], help="Data source")
    parser.add_argument("--outdir", default="./outputs", help="Output directory")
    parser.add_argument("--mode", default="group", choices=["group", "exchange", "symbols"], help="Universe mode")
    parser.add_argument("--group", default="VN30", help="Group for mode=group")
    parser.add_argument("--exchange", default="HOSE", help="Exchange for mode=exchange")
    parser.add_argument("--symbols", default="", help="Comma-separated symbols for mode=symbols")
    parser.add_argument("--api-key", default="", help="Optional VNStock API key override")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent

    run([
        sys.executable,
        str(base / "build_universe.py"),
        "--source", args.source,
        "--mode", args.mode,
        "--group", args.group,
        "--exchange", args.exchange,
        "--symbols", args.symbols,
        "--outdir", args.outdir,
        "--api-key", args.api_key,
    ])

    universe_latest = str(Path(args.outdir) / "universe_latest.csv")
    universe_path = Path(universe_latest).read_text(encoding="utf-8").strip()

    run([
        sys.executable,
        str(base / "collect_market_data.py"),
        "--source", args.source,
        "--universe-file", universe_path,
        "--outdir", args.outdir,
        "--api-key", args.api_key,
    ])

    run([
        sys.executable,
        str(base / "collect_fundamentals.py"),
        "--source", args.source,
        "--universe-file", universe_path,
        "--outdir", args.outdir,
        "--api-key", args.api_key,
    ])

    market_path = Path(args.outdir, "market_data_latest.csv").read_text(encoding="utf-8").strip()
    fundamentals_path = Path(args.outdir, "fundamentals_latest.csv").read_text(encoding="utf-8").strip()

    run([
        sys.executable,
        str(base / "score_stocks.py"),
        "--market-file", market_path,
        "--fundamentals-file", fundamentals_path,
        "--outdir", args.outdir,
    ])

    ranking_path = Path(args.outdir, "ranking_latest.csv").read_text(encoding="utf-8").strip()

    run([
        sys.executable,
        str(base / "generate_report.py"),
        "--ranking-file", ranking_path,
        "--outdir", args.outdir,
    ])


if __name__ == "__main__":
    main()
