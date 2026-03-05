#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None

from common import configure_vnstock_api_key, ensure_outdir, timestamp, write_json, write_latest_alias


def from_group(source: str, group: str):
    from vnstock import Listing

    listing = Listing(source=source)
    data = listing.symbols_by_group(group=group)
    if isinstance(data, list):
        return pd.DataFrame({"symbol": [x.upper() for x in data]})
    if isinstance(data, pd.Series):
        return pd.DataFrame({"symbol": data.astype(str).str.upper().tolist()})
    if "symbol" in data.columns:
        data["symbol"] = data["symbol"].astype(str).str.upper()
    return data


def from_exchange(source: str, exchange: str):
    from vnstock import Listing

    listing = Listing(source=source)
    data = listing.symbols_by_exchange()
    if "exchange" in data.columns:
        data = data[data["exchange"].astype(str).str.upper().eq(exchange.upper())]
    if "symbol" in data.columns:
        data["symbol"] = data["symbol"].astype(str).str.upper()
    return data


def from_symbols(symbols: str):
    rows = [x.strip().upper() for x in symbols.split(",") if x.strip()]
    return pd.DataFrame({"symbol": rows})


def main() -> None:
    parser = argparse.ArgumentParser(description="Build stock universe for vnstock valuation pipeline")
    parser.add_argument("--source", default="kbs", choices=["kbs", "vci"], help="Data source")
    parser.add_argument("--mode", required=True, choices=["group", "exchange", "symbols"], help="Universe mode")
    parser.add_argument("--group", default="VN30", help="Group name for mode=group")
    parser.add_argument("--exchange", default="HOSE", help="Exchange name for mode=exchange")
    parser.add_argument("--symbols", default="", help="Comma-separated symbols for mode=symbols")
    parser.add_argument("--outdir", default="./outputs", help="Output directory")
    parser.add_argument("--api-key", default="", help="Optional VNStock API key override")
    args = parser.parse_args()

    if pd is None:
        raise ModuleNotFoundError("Missing dependency: pandas. Install with `pip install pandas`.")

    outdir = ensure_outdir(args.outdir)
    configure_vnstock_api_key(args.api_key or None)

    if args.mode == "group":
        df = from_group(args.source, args.group)
    elif args.mode == "exchange":
        df = from_exchange(args.source, args.exchange)
    else:
        df = from_symbols(args.symbols)

    if df.empty or "symbol" not in df.columns:
        raise RuntimeError("Failed to build universe with non-empty symbol column.")

    df = df.dropna(subset=["symbol"]).drop_duplicates(subset=["symbol"]).reset_index(drop=True)
    ts = timestamp()
    csv_path = outdir / f"universe_{ts}.csv"
    json_path = outdir / f"universe_{ts}.json"

    df.to_csv(csv_path, index=False)
    write_json(
        json_path,
        {
            "generated_at": ts,
            "source": args.source,
            "mode": args.mode,
            "count": len(df),
            "symbols": df["symbol"].tolist(),
        },
    )

    # Latest pointers for easier pipeline chaining.
    (outdir / "universe_latest.csv").write_text(str(csv_path), encoding="utf-8")
    (outdir / "universe_latest.json").write_text(str(json_path), encoding="utf-8")

    print(f"Saved: {csv_path}")
    print(f"Saved: {json_path}")


if __name__ == "__main__":
    main()
