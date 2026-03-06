#!/usr/bin/env python3
"""
ByBit Order Book Data Processor

Reads raw ob500 ZIP files, parses JSONL snapshots, filters to depth 50,
optionally downsamples, and outputs Parquet files for backtesting.

Usage:
    python process_orderbook.py --input ./data/raw --output ./data/processed --depth 50
    python process_orderbook.py --input ./data/raw --output ./data/processed --depth 50 --sample-interval 1s
"""

import argparse
import json
import os
import sys
import zipfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("ERROR: Missing dependencies. Install with:")
    print("  pip install pandas numpy pyarrow --break-system-packages")
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Process ByBit order book snapshots")
    parser.add_argument("--input", type=str, default="./data/raw", help="Directory with raw ZIP files")
    parser.add_argument("--output", type=str, default="./data/processed", help="Output directory for Parquet files")
    parser.add_argument("--depth", type=int, default=50, help="Order book depth to retain (default: 50)")
    parser.add_argument("--sample-interval", type=str, default=None,
                        help="Downsample interval (e.g., '1s', '5s', '1min'). None = keep all ~100ms snapshots")
    parser.add_argument("--symbol", type=str, default=None,
                        help="Filter to specific symbol (default: process all)")
    return parser.parse_args()


def parse_snapshot(line: bytes, depth: int = 50) -> dict:
    """Parse a single JSONL line into a flat dict for the top N depth levels."""
    snap = json.loads(line.decode("utf-8"))
    data = snap["data"]
    ts_ms = snap["ts"]
    cts_ms = snap.get("cts", ts_ms)
    symbol = data["s"]

    bids = data["b"][:depth]
    asks = data["a"][:depth]

    record = {
        "timestamp": pd.Timestamp(ts_ms, unit="ms"),
        "cts": pd.Timestamp(cts_ms, unit="ms"),
        "symbol": symbol,
    }

    # Flatten bid/ask levels into columns: bid_price_0, bid_size_0, ..., ask_price_49, ask_size_49
    for i, (price, size) in enumerate(bids):
        record[f"bid_price_{i}"] = float(price)
        record[f"bid_size_{i}"] = float(size)

    for i, (price, size) in enumerate(asks):
        record[f"ask_price_{i}"] = float(price)
        record[f"ask_size_{i}"] = float(size)

    # Pad missing levels with NaN
    for i in range(len(bids), depth):
        record[f"bid_price_{i}"] = np.nan
        record[f"bid_size_{i}"] = np.nan
    for i in range(len(asks), depth):
        record[f"ask_price_{i}"] = np.nan
        record[f"ask_size_{i}"] = np.nan

    # Derived features useful for strategies
    if bids and asks:
        record["best_bid"] = float(bids[0][0])
        record["best_ask"] = float(asks[0][0])
        record["mid_price"] = (record["best_bid"] + record["best_ask"]) / 2
        record["spread"] = record["best_ask"] - record["best_bid"]
        record["spread_bps"] = (record["spread"] / record["mid_price"]) * 10000

        # Total volume at top N levels
        record["total_bid_volume"] = sum(float(b[1]) for b in bids)
        record["total_ask_volume"] = sum(float(a[1]) for a in asks)
        record["volume_imbalance"] = (
            (record["total_bid_volume"] - record["total_ask_volume"])
            / (record["total_bid_volume"] + record["total_ask_volume"])
            if (record["total_bid_volume"] + record["total_ask_volume"]) > 0
            else 0.0
        )

        # Weighted mid price (microprice)
        best_bid_size = float(bids[0][1])
        best_ask_size = float(asks[0][1])
        if best_bid_size + best_ask_size > 0:
            record["microprice"] = (
                record["best_bid"] * best_ask_size + record["best_ask"] * best_bid_size
            ) / (best_bid_size + best_ask_size)
        else:
            record["microprice"] = record["mid_price"]

    return record


def process_zip_file(zip_path: str, depth: int = 50, symbol_filter: str = None) -> pd.DataFrame:
    """Process a single ZIP file and return a DataFrame."""
    records = []
    print(f"  Processing: {os.path.basename(zip_path)}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        for filename in zf.namelist():
            if not filename.endswith(".data"):
                continue
            print(f"    Reading: {filename}")
            with zf.open(filename) as f:
                line_count = 0
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = parse_snapshot(line, depth=depth)
                        if symbol_filter and record["symbol"] != symbol_filter:
                            continue
                        records.append(record)
                        line_count += 1
                        if line_count % 100000 == 0:
                            print(f"      {line_count:,} snapshots parsed...")
                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        continue  # Skip malformed lines

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = df.sort_values("timestamp").reset_index(drop=True)
    print(f"    Total snapshots: {len(df):,}")
    return df


def downsample(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    """Downsample by keeping the last snapshot in each interval."""
    if df.empty:
        return df
    df = df.set_index("timestamp")
    df = df.groupby(pd.Grouper(freq=interval)).last().dropna(subset=["symbol"])
    df = df.reset_index()
    return df


def main():
    args = parse_args()
    input_dir = args.input
    output_dir = args.output
    depth = args.depth

    os.makedirs(output_dir, exist_ok=True)

    # Find all ZIP files
    zip_files = sorted(Path(input_dir).glob("*ob500*.zip"))
    if not zip_files:
        # Also try all ZIPs in case naming differs
        zip_files = sorted(Path(input_dir).glob("*.zip"))

    if not zip_files:
        print(f"ERROR: No ZIP files found in {input_dir}")
        sys.exit(1)

    print(f"ByBit Order Book Processor")
    print(f"  Input:     {input_dir}")
    print(f"  Output:    {output_dir}")
    print(f"  Depth:     {depth}")
    print(f"  Downsample: {args.sample_interval or 'None (keep all)'}")
    print(f"  Files:     {len(zip_files)}")
    print()

    all_dfs = []
    for zip_path in zip_files:
        df = process_zip_file(str(zip_path), depth=depth, symbol_filter=args.symbol)
        if not df.empty:
            all_dfs.append(df)

    if not all_dfs:
        print("ERROR: No data parsed from ZIP files")
        sys.exit(1)

    combined = pd.concat(all_dfs, ignore_index=True)
    combined = combined.sort_values("timestamp").reset_index(drop=True)
    print(f"\nTotal combined snapshots: {len(combined):,}")

    # Downsample if requested
    if args.sample_interval:
        original_count = len(combined)
        combined = downsample(combined, args.sample_interval)
        print(f"Downsampled from {original_count:,} to {len(combined):,} snapshots ({args.sample_interval})")

    # Save per-symbol Parquet files
    for symbol in combined["symbol"].unique():
        sym_df = combined[combined["symbol"] == symbol]
        out_path = os.path.join(output_dir, f"{symbol}_ob{depth}.parquet")
        sym_df.to_parquet(out_path, index=False, engine="pyarrow")
        size_mb = os.path.getsize(out_path) / (1024 * 1024)
        print(f"  Saved: {out_path} ({len(sym_df):,} rows, {size_mb:.1f} MB)")

    print("\nProcessing complete!")


if __name__ == "__main__":
    main()
