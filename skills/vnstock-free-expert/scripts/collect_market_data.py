#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None

from common import RateLimiter, configure_vnstock_api_key, ensure_outdir, pct_return, safe_float, timestamp, write_json


def load_symbols(universe_file: str):
    p = Path(universe_file)
    if not p.exists():
        raise FileNotFoundError(f"Universe file not found: {universe_file}")
    df = pd.read_csv(p)
    if "symbol" not in df.columns:
        raise RuntimeError("Universe file must include symbol column.")
    return [s.strip().upper() for s in df["symbol"].astype(str).tolist() if s.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect historical market data and momentum metrics")
    parser.add_argument("--source", default="kbs", choices=["kbs", "vci"], help="Data source")
    parser.add_argument("--universe-file", required=True, help="CSV with symbol column")
    parser.add_argument("--outdir", default="./outputs", help="Output directory")
    parser.add_argument("--interval", default="1D", help="Price interval")
    parser.add_argument("--lookback-days", type=int, default=260, help="Bars target")
    parser.add_argument("--min-interval-sec", type=float, default=3.2, help="Rate-limit pacing")
    parser.add_argument("--api-key", default="", help="Optional VNStock API key override")
    args = parser.parse_args()

    if pd is None:
        raise ModuleNotFoundError("Missing dependency: pandas. Install with `pip install pandas`.")

    from vnstock import Quote

    outdir = ensure_outdir(args.outdir)
    configure_vnstock_api_key(args.api_key or None)
    symbols = load_symbols(args.universe_file)
    limiter = RateLimiter(min_interval_sec=args.min_interval_sec)

    end = datetime.now().date()
    start = end - timedelta(days=max(args.lookback_days * 2, 400))

    rows = []
    errors = []

    for symbol in symbols:
        try:
            limiter.wait()
            quote = Quote(source=args.source, symbol=symbol)
            hist = quote.history(start=str(start), end=str(end), interval=args.interval)

            row = {"symbol": symbol, "source": args.source}
            if hist is not None and not hist.empty and "close" in hist.columns:
                last = hist.sort_values("time").iloc[-1]
                row["last_close"] = safe_float(last.get("close"))
                row["ret_3m_pct"] = pct_return(hist, 63)
                row["ret_6m_pct"] = pct_return(hist, 126)
                row["ret_12m_pct"] = pct_return(hist, 252)
                row["bars"] = len(hist)
            rows.append(row)
        except Exception as e:
            errors.append({"symbol": symbol, "error": str(e)})

    df = pd.DataFrame(rows)
    ts = timestamp()
    csv_path = outdir / f"market_data_{ts}.csv"
    json_path = outdir / f"market_data_{ts}.json"

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

    (outdir / "market_data_latest.csv").write_text(str(csv_path), encoding="utf-8")
    (outdir / "market_data_latest.json").write_text(str(json_path), encoding="utf-8")

    print(f"Saved: {csv_path}")
    print(f"Saved: {json_path}")


if __name__ == "__main__":
    main()
