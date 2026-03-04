"""
GridTRX MCP Server — structured AI agent interface to the accounting engine.

Wraps models.py functions as MCP tools. Every tool takes db_path as its first
parameter. The GRIDTRX_WORKSPACE environment variable must be set to the
directory containing client books.db files — the server will refuse to start
without it, and rejects any db_path outside that directory.

Usage:
    pip install mcp
    GRIDTRX_WORKSPACE=~/clients python mcp_server.py
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
import models

mcp = FastMCP("GridTRX", instructions="Double-entry accounting engine")

_initialized_db = None
_workspace = None

def _get_workspace():
    """Return the resolved workspace path. Raises if GRIDTRX_WORKSPACE is not set."""
    global _workspace
    if _workspace is None:
        ws = os.environ.get("GRIDTRX_WORKSPACE", "")
        if not ws:
            raise RuntimeError(
                "GRIDTRX_WORKSPACE environment variable is not set. "
                "Set it to the directory containing client books.db files. "
                "Example: GRIDTRX_WORKSPACE=~/clients python mcp_server.py"
            )
        _workspace = os.path.realpath(os.path.expanduser(ws))
    return _workspace

def _check_path(file_path: str, label: str = "path"):
    """Enforce workspace boundary on any file path (imports, exports, etc.)."""
    resolved = os.path.realpath(os.path.expanduser(file_path))
    ws = _get_workspace()
    if not resolved.startswith(ws + os.sep) and resolved != ws:
        raise ValueError(
            f"Access denied: {label} '{file_path}' is outside the workspace ({ws})."
        )
    return resolved

def _init(db_path: str):
    """Initialize database connection, only re-init if path changes.
    Enforces workspace boundary — db_path must be inside GRIDTRX_WORKSPACE."""
    global _initialized_db
    resolved = os.path.realpath(os.path.expanduser(db_path))
    ws = _get_workspace()
    if not resolved.startswith(ws + os.sep) and resolved != ws:
        raise ValueError(
            f"Access denied: '{db_path}' is outside the workspace ({ws}). "
            f"Set GRIDTRX_WORKSPACE to change the allowed directory."
        )
    if _initialized_db != resolved:
        models.init_db(resolved)
        _initialized_db = resolved


def _row_to_dict(row):
    """Convert a sqlite3.Row to a plain dict."""
    if row is None:
        return None
    return dict(row)


def _rows_to_dicts(rows):
    """Convert a list of sqlite3.Row to a list of plain dicts."""
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════════
# READ-ONLY TOOLS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def list_accounts(db_path: str, query: str = "") -> list[dict]:
    """List all accounts in the chart of accounts. Optionally filter by name/description with query."""
    _init(db_path)
    if query:
        rows = models.search_accounts(query)
    else:
        rows = models.get_accounts()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "description": r["description"],
            "normal_balance": r["normal_balance"],
            "type": r["account_type"],
        }
        for r in rows
    ]


@mcp.tool()
def get_balance(
    db_path: str,
    account_name: str,
    date_from: str = "",
    date_to: str = "",
) -> dict:
    """Get the balance of a single account, optionally within a date range (YYYY-MM-DD)."""
    _init(db_path)
    acct = models.get_account_by_name(account_name)
    if not acct:
        raise ValueError(f"Account not found: {account_name}")
    raw = models.get_account_balance(
        acct["id"],
        date_from=date_from or None,
        date_to=date_to or None,
    )
    sign = 1 if acct["normal_balance"] == "D" else -1
    balance = raw * sign
    return {
        "account": acct["name"],
        "balance_cents": balance,
        "formatted": models.fmt_amount(balance),
    }


@mcp.tool()
def get_ledger(
    db_path: str,
    account_name: str,
    date_from: str = "",
    date_to: str = "",
) -> list[dict]:
    """Get the full ledger for an account with running balance. Optionally filter by date range."""
    _init(db_path)
    acct = models.get_account_by_name(account_name)
    if not acct:
        raise ValueError(f"Account not found: {account_name}")
    entries = models.get_ledger(
        acct["id"],
        date_from=date_from or None,
        date_to=date_to or None,
    )
    return [
        {
            "txn_id": e["txn_id"],
            "date": e["date"],
            "reference": e["reference"],
            "description": e["description"],
            "amount_cents": e["amount"],
            "amount_formatted": models.fmt_amount(e["amount"]),
            "running_balance_cents": e["running_balance"],
            "running_balance_formatted": models.fmt_amount(e["running_balance"]),
            "cross_accounts": e["cross_accounts"],
            "reconciled": bool(e["reconciled"]),
        }
        for e in entries
    ]


@mcp.tool()
def trial_balance(db_path: str, as_of_date: str = "") -> dict:
    """Get the trial balance — all posting accounts with non-zero balances, split into Dr/Cr columns."""
    _init(db_path)
    accounts, total_dr, total_cr = models.get_trial_balance(
        as_of_date=as_of_date or None,
    )
    return {
        "accounts": [
            {
                "name": a["name"],
                "description": a["description"],
                "normal_balance": a["normal_balance"],
                "debit_cents": a["debit"],
                "debit_formatted": models.fmt_amount(a["debit"]) if a["debit"] else "",
                "credit_cents": a["credit"],
                "credit_formatted": models.fmt_amount(a["credit"]) if a["credit"] else "",
            }
            for a in accounts
        ],
        "total_debit_cents": total_dr,
        "total_debit_formatted": models.fmt_amount(total_dr),
        "total_credit_cents": total_cr,
        "total_credit_formatted": models.fmt_amount(total_cr),
    }


@mcp.tool()
def generate_report(
    db_path: str,
    report_name: str,
    date_from: str = "",
    date_to: str = "",
) -> list[dict]:
    """Generate a financial report (BS, IS, AJE, etc.) with computed balances. Returns line items."""
    _init(db_path)
    report = models.find_report_by_name(report_name)
    if not report:
        raise ValueError(f"Report not found: {report_name}")
    items = models.compute_report_column(
        report["id"],
        date_from=date_from or None,
        date_to=date_to or None,
    )
    result = []
    for item_dict, amount in items:
        entry = {
            "description": item_dict.get("description") or item_dict.get("acct_name") or "",
            "item_type": item_dict.get("item_type", ""),
            "indent": item_dict.get("indent", 0),
            "amount_cents": amount,
            "amount_formatted": models.fmt_amount(amount),
        }
        if item_dict.get("acct_name"):
            entry["account_name"] = item_dict["acct_name"]
        if item_dict.get("sep_style"):
            entry["separator_style"] = item_dict["sep_style"]
        result.append(entry)
    return result


@mcp.tool()
def get_transaction(db_path: str, txn_id: int) -> dict:
    """Get a single transaction by ID, including all its journal lines."""
    _init(db_path)
    txn, lines = models.get_transaction(txn_id)
    if not txn:
        raise ValueError(f"Transaction not found: {txn_id}")
    return {
        "id": txn["id"],
        "date": txn["date"],
        "description": txn["description"],
        "reference": txn["reference"],
        "lines": [
            {
                "account_name": l["account_name"],
                "amount_cents": l["amount"],
                "amount_formatted": models.fmt_amount(l["amount"]),
                "description": l["description"],
                "reconciled": bool(l["reconciled"]),
            }
            for l in lines
        ],
    }


@mcp.tool()
def search_transactions(
    db_path: str, query: str, limit: int = 100
) -> list[dict]:
    """Search transactions by description, reference, or account name."""
    _init(db_path)
    rows = models.search_transactions(query, limit=limit)
    return [
        {
            "txn_id": r["txn_id"],
            "date": r["date"],
            "reference": r["reference"],
            "description": r["description"],
            "accounts": r["accounts"],
            "total_amount_cents": r["total_amount"] or 0,
            "total_amount_formatted": models.fmt_amount(r["total_amount"] or 0),
        }
        for r in rows
    ]


@mcp.tool()
def list_reports(db_path: str) -> list[dict]:
    """List all available reports (BS, IS, AJE, etc.)."""
    _init(db_path)
    rows = models.get_reports()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "description": r["description"],
        }
        for r in rows
    ]


@mcp.tool()
def update_report(db_path: str, report_name: str, description: str) -> dict:
    """Update a report's description."""
    _init(db_path)
    rpt = models.find_report_by_name(report_name)
    if not rpt:
        raise ValueError(f"Report not found: {report_name}")
    return models.update_report(rpt['id'], description=description)


@mcp.tool()
def list_rules(db_path: str) -> list[dict]:
    """List all import rules for CSV auto-categorization."""
    _init(db_path)
    rows = models.get_import_rules()
    return [
        {
            "id": r["id"],
            "keyword": r["keyword"],
            "account": r["account_name"],
            "tax_code": r["tax_code"],
            "priority": r["priority"],
        }
        for r in rows
    ]


@mcp.tool()
def get_info(db_path: str) -> dict:
    """Get company metadata: name, fiscal year end, lock date."""
    _init(db_path)
    return {
        "company_name": models.get_meta("company_name", ""),
        "fiscal_year_end": models.get_meta("fiscal_year_end", ""),
        "lock_date": models.get_meta("lock_date", ""),
    }


# ═══════════════════════════════════════════════════════════════════
# WRITE TOOLS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def post_transaction(
    db_path: str,
    date: str,
    description: str,
    amount: str,
    debit_account: str,
    credit_account: str,
) -> dict:
    """Post a simple 2-line transaction. Amount is in dollars (e.g. '1500.00'). Date is YYYY-MM-DD."""
    _init(db_path)
    dr_acct = models.get_account_by_name(debit_account)
    if not dr_acct:
        raise ValueError(f"Debit account not found: {debit_account}")
    cr_acct = models.get_account_by_name(credit_account)
    if not cr_acct:
        raise ValueError(f"Credit account not found: {credit_account}")
    amount_cents = models.parse_amount(amount)
    if amount_cents <= 0:
        raise ValueError(f"Amount must be positive: {amount}")
    ref = models.generate_ref()
    txn_id = models.add_simple_transaction(
        date, ref, description, dr_acct["id"], cr_acct["id"], amount_cents
    )
    return {"txn_id": txn_id, "reference": ref}


@mcp.tool()
def delete_transaction(db_path: str, txn_id: int) -> dict:
    """Delete a transaction by ID. Respects lock date."""
    _init(db_path)
    models.delete_transaction(txn_id)
    return {"deleted": True, "txn_id": txn_id}


@mcp.tool()
def add_account(
    db_path: str,
    name: str,
    normal_balance: str,
    description: str = "",
) -> dict:
    """Add a new posting account. normal_balance is 'D' (debit-normal) or 'C' (credit-normal)."""
    _init(db_path)
    if normal_balance not in ("D", "C"):
        raise ValueError("normal_balance must be 'D' or 'C'")
    account_id = models.add_account(name, normal_balance, description)
    return {"account_id": account_id, "name": name}


@mcp.tool()
def add_rule(
    db_path: str,
    keyword: str,
    account_name: str,
    tax_code: str = "",
    priority: int = 0,
) -> dict:
    """Add a CSV import rule. Transactions matching keyword are auto-posted to account_name."""
    _init(db_path)
    # Verify the target account exists
    acct = models.get_account_by_name(account_name)
    if not acct:
        raise ValueError(f"Account not found: {account_name}")
    models.save_import_rule(None, keyword, account_name, tax_code, priority)
    # Retrieve the newly created rule to get its ID
    rules = models.get_import_rules()
    rule_id = None
    for r in rules:
        if r["keyword"] == keyword and r["account_name"] == account_name:
            rule_id = r["id"]
            break
    return {"rule_id": rule_id}


@mcp.tool()
def delete_rule(db_path: str, rule_id: int) -> dict:
    """Delete an import rule by ID."""
    _init(db_path)
    models.delete_import_rule(rule_id)
    return {"deleted": True, "rule_id": rule_id}


@mcp.tool()
def import_csv(db_path: str, csv_path: str, bank_account: str) -> dict:
    """Import a bank CSV file into the books. Applies import rules to auto-categorize.

    CSV format: Date, Description, Amount (or Date, Description, Debit, Credit).
    Also handles multi-column bank exports (auto-detects columns).
    Positive amounts = deposits, negative = payments.
    Unmatched rows go to EX.SUSP (suspense). Review with get_ledger('EX.SUSP').
    """
    _init(db_path)

    csv_path = _check_path(csv_path, "csv_path")
    if not os.path.exists(csv_path):
        raise ValueError(f"File not found: {csv_path}")

    bank_acct = models.get_account_by_name(bank_account)
    if not bank_acct:
        raise ValueError(f"Bank account not found: {bank_account}")

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows_raw = list(reader)

    if not rows_raw:
        raise ValueError("Empty CSV file")

    has_header, data_rows, csv_repairs = _normalize_csv(rows_raw)

    if not data_rows:
        raise ValueError("No data rows in CSV (only a header)")

    # Build row dicts for import_rows: parse amounts from CSV columns
    import_data = []
    parse_errors = []
    for row_num, row in enumerate(data_rows, start=2 if has_header else 1):
        if len(row) < 3:
            parse_errors.append({"row": row_num, "reason": "Too few columns"})
            continue

        row_date = row[0].strip()
        row_desc = row[1].strip()

        if not row_desc:
            parse_errors.append({"row": row_num, "reason": "Missing description"})
            continue

        if len(row) >= 4 and (row[2].strip() or row[3].strip()):
            try:
                dr = models.parse_amount(row[2]) if row[2].strip() else 0
                cr = models.parse_amount(row[3]) if row[3].strip() else 0
                amount_cents = dr - cr
            except Exception:
                parse_errors.append({"row": row_num, "reason": f"Bad amount '{row[2].strip()}/{row[3].strip()}'"})
                continue
        else:
            try:
                amount_cents = models.parse_amount(row[2])
            except Exception:
                parse_errors.append({"row": row_num, "reason": f"Bad amount '{row[2].strip()}'"})
                continue

        import_data.append({
            'date': row_date,
            'description': row_desc,
            'amount_cents': amount_cents,
        })

    result = models.import_rows(bank_acct['id'], import_data)
    result['rows_processed'] = len(data_rows)
    result['skipped'] = result['skipped'] + len(parse_errors)
    if csv_repairs:
        result["rows_repaired"] = len(csv_repairs)
    if parse_errors:
        all_errors = parse_errors + result.get('errors', [])
        result['errors'] = all_errors[:20]
    return result


@mcp.tool()
def import_ofx(db_path: str, ofx_path: str, bank_account: str) -> dict:
    """Import a bank OFX/QBO file. Applies import rules to auto-categorize.

    OFX/QBO files are standard bank download formats. Supports both XML-based
    and SGML-based OFX files. Positive amounts = deposits, negative = payments.
    Unmatched rows go to EX.SUSP (suspense). Review with get_ledger('EX.SUSP').
    """
    _init(db_path)

    ofx_path = _check_path(ofx_path, "ofx_path")
    if not os.path.exists(ofx_path):
        raise ValueError(f"File not found: {ofx_path}")

    bank_acct = models.get_account_by_name(bank_account)
    if not bank_acct:
        raise ValueError(f"Bank account not found: {bank_account}")

    rows = models.parse_ofx(ofx_path)
    result = models.import_rows(bank_acct['id'], rows)
    return result


@mcp.tool()
def year_end(db_path: str, ye_date: str) -> dict:
    """Year-end rollover. Posts closing RE offset entry and sets lock date.

    Reads the Retained Earnings total from the BS report as of ye_date.
    Posts: Dr RE.OFS / Cr RE.OPEN for that amount (dated first day of new FY).
    Then sets the lock date to ye_date. This is a one-way operation.

    ye_date: fiscal year end date in YYYY-MM-DD format (e.g. '2025-12-31').
    """
    _init(db_path)

    ye_date = _normalize_date(ye_date)
    if not ye_date:
        raise ValueError("Invalid date. Use YYYY-MM-DD format.")

    ye_dt = datetime.strptime(ye_date, "%Y-%m-%d")
    new_fy_start = (ye_dt + timedelta(days=1)).strftime("%Y-%m-%d")

    bs_report = models.find_report_by_name("BS")
    if not bs_report:
        raise ValueError("No BS (Balance Sheet) report found. Year-end requires a BS report.")

    display_items = models.get_report_items(bs_report["id"])
    all_items = models.get_all_report_items()
    data = models.compute_report_column(
        bs_report["id"], date_to=ye_date,
        _display_items=display_items, _all_items=all_items,
    )

    re_balance = None
    for item, balance in data:
        if item.get("acct_name") == "RE":
            re_balance = balance
            break

    if re_balance is None:
        raise ValueError("RE (Retained Earnings) total not found in BS report.")

    if re_balance == 0:
        return {"message": "Retained Earnings balance is zero — nothing to roll over."}

    re_acct = models.get_account_by_name("RE")
    if re_acct:
        sign = 1 if re_acct["normal_balance"] == "D" else -1
        raw_re = re_balance * sign
    else:
        raw_re = -re_balance

    re_open = models.get_account_by_name("RE.OPEN")
    re_ofs_acct = models.get_account_by_name("RE.OFS")

    if not re_open:
        raise ValueError("RE.OPEN account not found in chart of accounts.")

    if not re_ofs_acct:
        re_ofs_id = models.add_account("RE.OFS", "D", "Annual Opening RE Offset", "posting")
        re_ofs_acct = models.get_account(re_ofs_id)
        ofs_report = models.find_report_by_name("RE.OFS")
        if ofs_report:
            models.add_report_item(
                ofs_report["id"], "account", "Annual Opening RE Offset",
                re_ofs_acct["id"], indent=1, total_to_1="RE",
            )

    fy_year = ye_dt.strftime("%Y")
    desc = f"{fy_year} Closing RE"

    ofs_raw = -raw_re
    open_raw = raw_re

    lines = [
        (re_ofs_acct["id"], ofs_raw, desc),
        (re_open["id"], open_raw, desc),
    ]
    txn_id = models.add_transaction(new_fy_start, "YE-OFS", desc, lines)

    models.set_meta("lock_date", ye_date)

    new_fy_year = (ye_dt + timedelta(days=1)).strftime("%Y")
    models.set_meta("fiscal_year", new_fy_year)

    return {
        "txn_id": txn_id,
        "ye_date": ye_date,
        "posting_date": new_fy_start,
        "description": desc,
        "retained_earnings_cents": re_balance,
        "retained_earnings_formatted": models.fmt_amount(re_balance),
        "lock_date_set": ye_date,
    }


@mcp.tool()
def set_lock_date(db_path: str, lock_date: str = "") -> dict:
    """Show or set the lock date. Transactions on or before the lock date cannot be posted, edited, or deleted.

    If lock_date is provided (YYYY-MM-DD), sets it. If omitted, returns the current lock date.
    """
    _init(db_path)

    if lock_date:
        normalized = _normalize_date(lock_date)
        if not normalized:
            raise ValueError(f"Invalid date: '{lock_date}'. Use YYYY-MM-DD format.")
        models.set_meta("lock_date", normalized)
        return {"lock_date": normalized, "message": f"Lock date set to {normalized}"}
    else:
        current = models.get_meta("lock_date", "")
        return {"lock_date": current or None}


@mcp.tool()
def setup_detailed_ar(db_path: str) -> dict:
    """Setup a Detailed Accounts Receivable subledger report.

    Creates an AR report on the home screen with 3 sample client accounts
    (Gretzky, Lemieux, Orr), a total account (ARDET), and links it to the
    Balance Sheet via AR.DET. The cross-report total chain flows:
    R. client accounts → ARDET → AR.DET (on BS) → AR.TOT → CA → TA.

    Run once per set of books. Returns an error if the AR report already exists.
    After setup, add real clients with add_account (e.g. R.SMIJOH, D, "Smith, John")
    and place them on the AR report with total_to_1 set to ARDET.
    """
    _init(db_path)
    result = models.setup_detailed_ar()
    return {"success": True, "message": result}


@mcp.tool()
def setup_detailed_ap(db_path: str) -> dict:
    """Setup a Detailed Accounts Payable subledger report.

    Creates an AP.SUB report on the home screen with 3 sample vendor accounts
    (Bauer, CCM, Warrior), a total account (APDET), and links it to the
    Balance Sheet via AP.DET → AP.TOT. Also restructures the BS to add an
    AP.TOT subtotal for all payable accounts. The cross-report total chain flows:
    P. vendor accounts → APDET → AP.DET (on BS) → AP.TOT → CL → TL.

    Run once per set of books. Returns an error if the AP.SUB report already exists.
    After setup, add real vendors with add_account (e.g. P.SMISUP, C, "Smith, Supply")
    and place them on the AP.SUB report with total_to_1 set to APDET.
    """
    _init(db_path)
    result = models.setup_detailed_ap()
    return {"success": True, "message": result}


@mcp.tool()
def bulk_report_layout(
    db_path: str,
    report_name: str,
    items: list[dict],
    after_account: str = "",
    mode: str = "append",
) -> dict:
    """Place a batch of items on a report in one call, with correct ordering guaranteed.

    Use this after importing a trial balance to lay out 20-60 accounts on the BS/IS
    in the correct sections with proper positioning, indentation, and total_to wiring.

    Args:
        report_name: Target report (BS, IS, etc.)
        items: Ordered list of items. Each dict can have:
            - account_name (required for account/total items)
            - item_type: "account" (default), "total", "label", "separator"
            - indent: indentation level (default 2)
            - total_to: account name this item rolls up into (sets total_to_1)
            - description: override display text
            - sep_style: for separators — "single", "double", "blank"
        after_account: Anchor — insert the batch after this account on the report.
            If empty, appends to end (or starts at 10 for replace mode).
        mode: "append" (default) adds to existing items;
            "replace" clears all existing items first then inserts.
    """
    _init(db_path)
    if mode not in ("append", "replace"):
        raise ValueError(f"Invalid mode: '{mode}'. Must be 'append' or 'replace'.")

    report = models.find_report_by_name(report_name)
    if not report:
        raise ValueError(f"Report not found: {report_name}")
    report_id = report["id"]

    # Replace mode: wipe existing items
    if mode == "replace":
        models.clear_report_items(report_id)

    # Determine starting position
    if after_account:
        existing = models.get_report_items(report_id)
        anchor_pos = None
        for item in existing:
            if item["acct_name"] == after_account:
                anchor_pos = item["position"]
                break
        if anchor_pos is None:
            raise ValueError(
                f"after_account '{after_account}' not found on report {report_name}")
        position = anchor_pos + 5
    elif mode == "replace":
        position = 10
    else:
        # Append: start after current max
        existing = models.get_report_items(report_id)
        max_pos = max((item["position"] for item in existing), default=0)
        position = max_pos + 10

    placed = 0
    skipped = 0
    errors = []

    with models.get_db() as db:
        for idx, spec in enumerate(items):
            item_type = spec.get("item_type", "account")
            indent = spec.get("indent", 2)
            total_to_1 = spec.get("total_to", "")
            description = spec.get("description", "")
            sep_style = spec.get("sep_style", "")
            account_name = spec.get("account_name", "")

            # Validate item_type
            if item_type not in ("account", "total", "label", "separator"):
                errors.append({"index": idx, "reason": f"Invalid item_type: '{item_type}'"})
                skipped += 1
                continue

            # Labels and separators don't need an account
            if item_type in ("label", "separator"):
                db.execute(
                    "INSERT INTO report_items(report_id, position, item_type, description, "
                    "account_id, indent, total_to_1, sep_style) VALUES(?,?,?,?,?,?,?,?)",
                    (report_id, position, item_type, description, None, indent,
                     total_to_1, sep_style))
                position += 10
                placed += 1
                continue

            # Account and total types require account_name
            if not account_name:
                errors.append({"index": idx, "reason": f"Missing account_name for {item_type} item"})
                skipped += 1
                continue

            acct = models.get_account_by_name(account_name)
            if not acct:
                errors.append({"index": idx, "reason": f"Account not found: {account_name}"})
                skipped += 1
                continue

            db.execute(
                "INSERT INTO report_items(report_id, position, item_type, description, "
                "account_id, indent, total_to_1, sep_style) VALUES(?,?,?,?,?,?,?,?)",
                (report_id, position, item_type, description, acct["id"], indent,
                 total_to_1, sep_style))
            position += 10
            placed += 1

        # Resequence once at the end
        models._resequence(db, report_id)

    return {
        "report": report_name,
        "placed": placed,
        "skipped": skipped,
        "errors": errors,
        "mode": mode,
    }


# ═══════════════════════════════════════════════════════════════════
# HELPERS (CSV import)
# ═══════════════════════════════════════════════════════════════════

def _normalize_date(s):
    """Try to normalize a date string to YYYY-MM-DD."""
    return models.normalize_date(s)


def _normalize_csv(rows_raw):
    """Pre-process CSV: detect format, repair rows with extra fields, normalize.

    Handles:
      1. Standard Grid format (3-4 columns) — repairs rows with extra commas
      2. Multi-column bank CSVs (5+ columns) — auto-detects date/desc/amount
      3. Rows with extra fields from unquoted commas in descriptions

    Returns (has_header, data_rows, repairs).
    """
    if not rows_raw:
        return False, [], []

    first_row = rows_raw[0]
    header = [h.strip().lower() for h in first_row]
    has_header = any(kw in " ".join(header) for kw in
                     ["date", "description", "amount", "debit", "credit"])
    start = 1 if has_header else 0
    data_rows = [list(r) for r in rows_raw[start:]]
    expected = len(first_row)
    repairs = []

    if has_header and expected > 4:
        date_col = None
        amt_cols = []
        desc_cols = []

        for i, h in enumerate(header):
            if "date" in h and date_col is None:
                date_col = i
            elif "$" in h or h in ("amount", "debit", "credit"):
                amt_cols.append(i)
            elif any(kw in h for kw in ["description", "desc", "memo",
                                        "payee", "detail", "narrative"]):
                desc_cols.append(i)

        if date_col is None or not amt_cols:
            return has_header, data_rows, repairs

        normalized = []
        for idx, row in enumerate(data_rows):
            n = len(row)
            row_num = idx + start + 1
            date_val = row[date_col].strip() if date_col < n else ""

            if n > expected:
                amt_start = n - len(amt_cols)
                desc_parts = [row[i].strip() for i in range(date_col + 1, amt_start) if row[i].strip()]
                amt_val = ""
                for v in row[amt_start:]:
                    v = v.strip()
                    if v:
                        amt_val = v
                        break
                extra = n - expected
                desc_joined = ": ".join(desc_parts)
                repairs.append((row_num, extra, desc_joined[:50]))
            else:
                desc_parts = [row[c].strip() for c in desc_cols if c < n and row[c].strip()]
                amt_val = ""
                for c in amt_cols:
                    if c < n and row[c].strip():
                        amt_val = row[c].strip()
                        break
                desc_joined = ": ".join(desc_parts)

            normalized.append([date_val, desc_joined, amt_val])

        return has_header, normalized, repairs

    for i, row in enumerate(data_rows):
        if len(row) > expected:
            row_num = i + start + 1
            extra = len(row) - expected
            amt_count = expected - 2

            date_val = row[0]
            desc_fields = row[1 : len(row) - amt_count]
            amt_fields = row[len(row) - amt_count:]

            merged = ", ".join(f.strip() for f in desc_fields)
            data_rows[i] = [date_val, merged] + amt_fields
            repairs.append((row_num, extra, merged[:50]))

    return has_header, data_rows, repairs


if __name__ == "__main__":
    mcp.run()
