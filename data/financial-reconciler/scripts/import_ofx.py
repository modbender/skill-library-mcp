#!/usr/bin/env python3
"""OFX/QFX import for bank transactions."""

import argparse
import json
import os
import sys

from ofxparse import OfxParser

from db import ensure_db_ready, get_connection, insert_transaction
from utils import clean_merchant_name


def import_ofx(file_path, account_name=None, db_path=None):
    """Import transactions from an OFX/QFX file."""
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}"}

    source_file = os.path.basename(file_path)

    try:
        with open(file_path, "rb") as f:
            ofx = OfxParser.parse(f)
    except Exception as e:
        return {"success": False, "error": f"Failed to parse OFX file: {str(e)}"}

    if not ofx.account or not ofx.account.statement:
        return {"success": False, "error": "No account/statement data found in OFX file"}

    account = ofx.account
    statement = account.statement

    # Extract account info
    acct_id = account.account_id or ""
    acct_type = account.account_type or ""
    institution = getattr(account, "institution", None)
    bank_name = institution.organization if institution else "unknown"

    effective_account = account_name or f"{bank_name}_{acct_id[-4:]}" if acct_id else bank_name

    transactions = []
    for tx in statement.transactions:
        date_str = tx.date.strftime("%Y-%m-%d") if tx.date else None
        if not date_str:
            continue

        description = ""
        if hasattr(tx, "payee") and tx.payee:
            description = str(tx.payee)
        elif hasattr(tx, "memo") and tx.memo:
            description = str(tx.memo)
        elif hasattr(tx, "name") and tx.name:
            description = str(tx.name)

        description = description.strip()
        if not description:
            continue

        amount = float(tx.amount) if tx.amount else 0.0

        tx_type = str(tx.type) if hasattr(tx, "type") and tx.type else None
        memo = str(tx.memo).strip() if hasattr(tx, "memo") and tx.memo else None

        transactions.append({
            "date": date_str,
            "description": clean_merchant_name(description),
            "original_description": description,
            "amount": round(amount, 2),
            "transaction_type": tx_type,
            "memo": memo,
            "account": effective_account,
            "source_file": source_file,
        })

    if not transactions:
        return {"success": False, "error": "No valid transactions found in OFX file"}

    # Insert into database
    ensure_db_ready(db_path)
    conn = get_connection(db_path)

    imported = 0
    duplicates = 0
    errors = 0

    for tx in transactions:
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

    dates = [tx["date"] for tx in transactions]
    date_range = {"start": min(dates), "end": max(dates)} if dates else None

    # Account info for output
    account_info = {
        "account_id": acct_id[-4:] if acct_id else None,
        "account_type": acct_type,
        "institution": bank_name,
        "balance": float(statement.balance) if hasattr(statement, "balance") and statement.balance else None,
        "balance_date": statement.balance_date.strftime("%Y-%m-%d") if hasattr(statement, "balance_date") and statement.balance_date else None,
    }

    result = {
        "success": True,
        "imported": imported,
        "duplicates": duplicates,
        "errors": errors,
        "total_in_file": len(transactions),
        "date_range": date_range,
        "account": effective_account,
        "account_info": account_info,
        "source_file": source_file,
    }

    conn.close()
    return result


def main():
    parser = argparse.ArgumentParser(description="Import bank transactions from OFX/QFX")
    parser.add_argument("file", help="Path to OFX/QFX file")
    parser.add_argument("--account", help="Account name override")
    parser.add_argument("--db", help="Database path override")
    args = parser.parse_args()

    result = import_ofx(args.file, account_name=args.account, db_path=args.db)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
