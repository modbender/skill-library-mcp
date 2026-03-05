#!/usr/bin/env python3
"""
Export LP position events from RangePositionUpdate table to CSV.

This script exports raw LP add/remove events, which are stored as they happen
(unlike Executors which require shutdown or buffer threshold to persist).

Auto-detects the database with the most LP position data in data/.

Usage:
    python controllers/generic/lp_rebalancer/scripts/export_lp_positions.py [--db <database_path>] [--output <output_path>]

Examples:
    python controllers/generic/lp_rebalancer/scripts/export_lp_positions.py
    python controllers/generic/lp_rebalancer/scripts/export_lp_positions.py --summary
    python controllers/generic/lp_rebalancer/scripts/export_lp_positions.py --db data/conf_v2_with_controllers_1.sqlite
    python controllers/generic/lp_rebalancer/scripts/export_lp_positions.py --pair SOL-USDC
"""

import argparse
import csv
import os
from datetime import datetime
from pathlib import Path


def find_db_with_lp_positions(data_dir: str = "data") -> str:
    """Find database with RangePositionUpdate data, prioritizing by row count."""
    import sqlite3

    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    # Find all sqlite files and check for RangePositionUpdate data
    candidates = []
    for db_file in data_path.glob("*.sqlite"):
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='RangePositionUpdate'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM RangePositionUpdate")
                count = cursor.fetchone()[0]
                if count > 0:
                    candidates.append((str(db_file), count))
            conn.close()
        except Exception:
            continue

    if not candidates:
        raise FileNotFoundError(f"No database with RangePositionUpdate data found in {data_dir}")

    # Return the database with the most rows
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]


def get_table_columns(cursor) -> set:
    """Get column names from RangePositionUpdate table."""
    cursor.execute("PRAGMA table_info(RangePositionUpdate)")
    return {row[1] for row in cursor.fetchall()}


def export_positions(db_path: str, output_path: str, trading_pair: str = None) -> int:
    """Export LP position events to CSV. Returns number of rows exported."""
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if RangePositionUpdate table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='RangePositionUpdate'")
    if not cursor.fetchone():
        print("RangePositionUpdate table not found in database")
        conn.close()
        return 0

    # Get available columns (schema may vary)
    available_cols = get_table_columns(cursor)

    # All columns to export
    all_cols = ["id", "hb_id", "timestamp", "tx_hash", "token_id", "trade_fee",
                "config_file_path", "market", "order_action", "trading_pair", "position_address",
                "lower_price", "upper_price", "mid_price", "base_amount", "quote_amount",
                "base_fee", "quote_fee", "position_rent", "position_rent_refunded", "trade_fee_in_quote"]

    # Build SELECT with available columns
    select_cols = [c for c in all_cols if c in available_cols]

    # Build query
    query = f"SELECT {', '.join(select_cols)} FROM RangePositionUpdate WHERE 1=1"
    params = []

    if trading_pair:
        query += " AND trading_pair = ?"
        params.append(trading_pair)

    query += " ORDER BY timestamp DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        filter_str = f" with pair={trading_pair}" if trading_pair else ""
        print(f"No LP position events found{filter_str}")
        return 0

    # Create output directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header (add datetime column after timestamp)
        header = select_cols.copy()
        ts_idx = header.index("timestamp") if "timestamp" in header else -1
        if ts_idx >= 0:
            header.insert(ts_idx + 1, "datetime")
        writer.writerow(header)

        # Write data rows
        for row in rows:
            row_dict = dict(zip(select_cols, row))
            out_row = list(row)

            # Insert formatted datetime after timestamp
            if ts_idx >= 0:
                timestamp = row_dict.get("timestamp")
                dt_str = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S") if timestamp else ""
                out_row.insert(ts_idx + 1, dt_str)

            writer.writerow(out_row)

    return len(rows)


def show_summary(db_path: str):
    """Show summary of LP positions in database."""
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='RangePositionUpdate'")
    if not cursor.fetchone():
        print("RangePositionUpdate table not found")
        conn.close()
        return

    # Get counts by action (and trading_pair since market may not exist)
    cursor.execute("""
        SELECT trading_pair, order_action, COUNT(*) as count
        FROM RangePositionUpdate
        GROUP BY trading_pair, order_action
        ORDER BY trading_pair, order_action
    """)
    rows = cursor.fetchall()

    if not rows:
        print("No LP position events found")
        conn.close()
        return

    print("\nLP Position Events Summary:")
    print("-" * 50)
    current_pair = None
    for pair, action, count in rows:
        if pair != current_pair:
            if current_pair is not None:
                print()
            print(f"\n{pair or 'unknown'}:")
            current_pair = pair
        print(f"  {action or 'unknown'}: {count}")

    # Get unique position addresses
    cursor.execute("SELECT COUNT(DISTINCT position_address) FROM RangePositionUpdate WHERE position_address IS NOT NULL")
    unique_positions = cursor.fetchone()[0]
    print(f"\nUnique positions: {unique_positions}")

    # Get date range
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM RangePositionUpdate")
    min_ts, max_ts = cursor.fetchone()
    if min_ts and max_ts:
        min_dt = datetime.fromtimestamp(min_ts / 1000).strftime("%Y-%m-%d %H:%M")
        max_dt = datetime.fromtimestamp(max_ts / 1000).strftime("%Y-%m-%d %H:%M")
        print(f"Date range: {min_dt} to {max_dt}")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Export LP position events to CSV")
    parser.add_argument("--db", help="Path to SQLite database (default: data/hummingbot_trades.sqlite)")
    parser.add_argument("--output", "-o", help="Output CSV path (default: data/lp_positions_<timestamp>.csv)")
    parser.add_argument("--pair", "-p", help="Filter by trading pair (e.g., SOL-USDC)")
    parser.add_argument("--summary", "-s", action="store_true", help="Show summary only, don't export")

    args = parser.parse_args()

    # Determine database path
    if args.db:
        db_path = args.db
    else:
        db_path = find_db_with_lp_positions()
        print(f"Using database: {db_path}")

    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        return 1

    # Show summary if requested
    if args.summary:
        show_summary(db_path)
        return 0

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/lp_positions_{timestamp}.csv"

    # Export
    count = export_positions(db_path, output_path, args.pair)

    if count > 0:
        print(f"Exported {count} LP position events to: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
