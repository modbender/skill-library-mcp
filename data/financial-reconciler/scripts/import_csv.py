#!/usr/bin/env python3
"""CSV import for bank transactions. Supports Chase, BofA, Wells Fargo, and generic auto-detect."""

import argparse
import json
import os
import sys

import pandas as pd

from db import ensure_db_ready, get_connection, insert_transaction
from utils import clean_merchant_name, parse_amount, parse_date


def load_csv_formats():
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    with open(os.path.join(assets_dir, "csv_formats.json")) as f:
        return json.load(f)


def detect_format(df, formats_config):
    """Auto-detect bank format from CSV headers."""
    headers = [h.strip().lower() for h in df.columns.tolist()]

    # Check Chase
    chase_headers = [h.lower() for h in formats_config["formats"]["chase"]["detection_headers"]]
    if all(h in headers for h in chase_headers):
        return "chase"

    # Check BofA
    bofa_headers = [h.lower() for h in formats_config["formats"]["bofa"]["detection_headers"]]
    if all(h in headers for h in bofa_headers):
        return "bofa"

    # Check Wells Fargo (no header, 5 columns)
    if len(df.columns) == 5 and all(isinstance(c, int) or c.startswith("Unnamed") or str(c).isdigit() for c in df.columns):
        return "wells_fargo"

    return "generic"


def parse_chase(df, source_file):
    """Parse Chase bank CSV format."""
    transactions = []
    for _, row in df.iterrows():
        date = parse_date(row.get("Transaction Date", ""))
        description = str(row.get("Description", "")).strip()
        amount = parse_amount(row.get("Amount"))

        if not date or amount is None:
            continue

        transactions.append({
            "date": date,
            "description": clean_merchant_name(description),
            "original_description": description,
            "amount": amount,
            "transaction_type": str(row.get("Type", "")).strip() or None,
            "memo": str(row.get("Memo", "")).strip() or None,
            "account": "chase",
            "source_file": source_file,
        })
    return transactions


def parse_bofa(df, source_file):
    """Parse Bank of America CSV format."""
    transactions = []
    for _, row in df.iterrows():
        date = parse_date(row.get("Date", ""))
        description = str(row.get("Payee", row.get("Description", ""))).strip()
        amount = parse_amount(row.get("Amount"))

        if not date or amount is None:
            continue

        transactions.append({
            "date": date,
            "description": clean_merchant_name(description),
            "original_description": description,
            "amount": amount,
            "transaction_type": str(row.get("Transaction Type", "")).strip() or None,
            "memo": None,
            "account": "bofa",
            "source_file": source_file,
        })
    return transactions


def parse_wells_fargo(df, source_file):
    """Parse Wells Fargo CSV format (no headers, 5 columns)."""
    transactions = []
    for _, row in df.iterrows():
        values = row.tolist()
        if len(values) < 5:
            continue

        date = parse_date(values[0])
        amount = parse_amount(values[1])
        description = str(values[4]).strip() if values[4] else ""

        if not date or amount is None:
            continue

        transactions.append({
            "date": date,
            "description": clean_merchant_name(description),
            "original_description": description,
            "amount": amount,
            "transaction_type": None,
            "memo": None,
            "account": "wells_fargo",
            "source_file": source_file,
        })
    return transactions


def parse_generic(df, source_file, formats_config):
    """Parse a generic CSV by matching column names heuristically."""
    generic_cols = formats_config["formats"]["generic"]["columns"]
    headers_lower = {h.strip().lower(): h for h in df.columns.tolist()}

    def find_column(candidates):
        if isinstance(candidates, str):
            candidates = [candidates]
        for c in candidates:
            if c in headers_lower:
                return headers_lower[c]
        return None

    date_col = find_column(generic_cols["date"])
    desc_col = find_column(generic_cols["description"])
    amount_col = find_column(generic_cols["amount"])
    debit_col = find_column(generic_cols.get("debit", []))
    credit_col = find_column(generic_cols.get("credit", []))

    if not date_col or not desc_col:
        return []

    transactions = []
    for _, row in df.iterrows():
        date = parse_date(row.get(date_col, ""))
        description = str(row.get(desc_col, "")).strip()

        if amount_col:
            amount = parse_amount(row.get(amount_col))
        elif debit_col and credit_col:
            debit = parse_amount(row.get(debit_col))
            credit = parse_amount(row.get(credit_col))
            if debit and debit != 0:
                amount = -abs(debit)
            elif credit and credit != 0:
                amount = abs(credit)
            else:
                amount = 0.0
        else:
            continue

        if not date or amount is None:
            continue

        transactions.append({
            "date": date,
            "description": clean_merchant_name(description),
            "original_description": description,
            "amount": amount,
            "transaction_type": None,
            "memo": None,
            "account": "unknown",
            "source_file": source_file,
        })
    return transactions


def import_csv(file_path, bank_format=None, account_name=None, db_path=None):
    """Import transactions from a CSV file."""
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}"}

    formats_config = load_csv_formats()
    source_file = os.path.basename(file_path)

    # Read CSV
    try:
        # Try with headers first
        df = pd.read_csv(file_path, dtype=str, keep_default_na=False)

        # Auto-detect format if not specified
        if not bank_format:
            bank_format = detect_format(df, formats_config)

        # For Wells Fargo, re-read without headers
        if bank_format == "wells_fargo":
            wf_config = formats_config["formats"]["wells_fargo"]
            if wf_config.get("has_header") is False:
                df = pd.read_csv(file_path, header=None, dtype=str, keep_default_na=False)

    except Exception as e:
        return {"success": False, "error": f"Failed to read CSV: {str(e)}"}

    # Parse based on format
    parsers = {
        "chase": lambda: parse_chase(df, source_file),
        "bofa": lambda: parse_bofa(df, source_file),
        "wells_fargo": lambda: parse_wells_fargo(df, source_file),
        "generic": lambda: parse_generic(df, source_file, formats_config),
    }

    parser = parsers.get(bank_format)
    if not parser:
        return {"success": False, "error": f"Unknown bank format: {bank_format}"}

    transactions = parser()

    if not transactions:
        return {"success": False, "error": "No valid transactions found in file"}

    # Insert into database
    ensure_db_ready(db_path)
    conn = get_connection(db_path)

    imported = 0
    duplicates = 0
    errors = 0

    for tx in transactions:
        if account_name:
            tx["account"] = account_name
        try:
            was_inserted = insert_transaction(
                conn,
                date_str=tx["date"],
                description=tx["description"],
                amount=tx["amount"],
                account=tx["account"],
                source_file=tx["source_file"],
                transaction_type=tx["transaction_type"],
                memo=tx["memo"],
                original_description=tx["original_description"],
            )
            if was_inserted:
                imported += 1
            else:
                duplicates += 1
        except Exception:
            errors += 1

    conn.commit()

    # Get date range
    dates = [tx["date"] for tx in transactions]
    date_range = {"start": min(dates), "end": max(dates)} if dates else None

    result = {
        "success": True,
        "imported": imported,
        "duplicates": duplicates,
        "errors": errors,
        "total_in_file": len(transactions),
        "date_range": date_range,
        "account": account_name or transactions[0]["account"] if transactions else None,
        "format_detected": bank_format,
        "source_file": source_file,
    }

    conn.close()
    return result


def main():
    parser = argparse.ArgumentParser(description="Import bank transactions from CSV")
    parser.add_argument("file", help="Path to CSV file")
    parser.add_argument("--format", choices=["chase", "bofa", "wells_fargo", "generic"],
                        help="Bank format (auto-detected if not specified)")
    parser.add_argument("--account", help="Account name override")
    parser.add_argument("--db", help="Database path override")
    args = parser.parse_args()

    result = import_csv(args.file, bank_format=args.format,
                        account_name=args.account, db_path=args.db)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
