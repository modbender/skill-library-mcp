#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None

from common import RateLimiter, configure_vnstock_api_key, ensure_outdir, find_metric, timestamp, write_json


def load_symbols(universe_file: str):
    p = Path(universe_file)
    if not p.exists():
        raise FileNotFoundError(f"Universe file not found: {universe_file}")
    df = pd.read_csv(p)
    if "symbol" not in df.columns:
        raise RuntimeError("Universe file must include symbol column.")
    return [s.strip().upper() for s in df["symbol"].astype(str).tolist() if s.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect valuation and quality fundamentals")
    parser.add_argument("--source", default="kbs", choices=["kbs", "vci"], help="Data source")
    parser.add_argument("--universe-file", required=True, help="CSV with symbol column")
    parser.add_argument("--outdir", default="./outputs", help="Output directory")
    parser.add_argument("--min-interval-sec", type=float, default=3.2, help="Rate-limit pacing")
    parser.add_argument("--api-key", default="", help="Optional VNStock API key override")
    args = parser.parse_args()

    if pd is None:
        raise ModuleNotFoundError("Missing dependency: pandas. Install with `pip install pandas`.")

    from vnstock import Company, Finance

    outdir = ensure_outdir(args.outdir)
    configure_vnstock_api_key(args.api_key or None)
    symbols = load_symbols(args.universe_file)
    limiter = RateLimiter(min_interval_sec=args.min_interval_sec)

    rows = []
    errors = []

    for symbol in symbols:
        row = {"symbol": symbol, "source": args.source}
        try:
            limiter.wait()
            finance = Finance(source=args.source, symbol=symbol)
            ratios = finance.ratio(period="year")

            row["pe"] = find_metric(ratios, ["p/e", "pe", "price to earnings"])
            row["pb"] = find_metric(ratios, ["p/b", "pb", "price to book"])
            row["roe"] = find_metric(ratios, ["roe", "return on equity"])
            row["debt_equity"] = find_metric(ratios, ["debt/equity", "debt to equity", "d/e"])

            limiter.wait()
            company = Company(source=args.source, symbol=symbol)
            overview = company.overview()
            if overview is not None and isinstance(overview, pd.DataFrame) and not overview.empty:
                local = overview.iloc[0].to_dict()
                row["exchange"] = local.get("exchange")
                row["industry"] = local.get("icb_name3") or local.get("icb_name2")

            rows.append(row)
        except Exception as e:
            errors.append({"symbol": symbol, "error": str(e)})

    df = pd.DataFrame(rows)
    ts = timestamp()
    csv_path = outdir / f"fundamentals_{ts}.csv"
    json_path = outdir / f"fundamentals_{ts}.json"

    df.to_csv(csv_path, index=False)
    write_json(
        json_path,
        {
            "generated_at": ts,
            "source": args.source,
            "rows": df.to_dict(orient="records"),
            "errors": errors,
        },
    )

    (outdir / "fundamentals_latest.csv").write_text(str(csv_path), encoding="utf-8")
    (outdir / "fundamentals_latest.json").write_text(str(json_path), encoding="utf-8")

    print(f"Saved: {csv_path}")
    print(f"Saved: {json_path}")


if __name__ == "__main__":
    main()
