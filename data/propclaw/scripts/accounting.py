#!/usr/bin/env python3
"""propclaw accounting domain module.

Trust accounting, owner statements, security deposits, and 1099 reporting.
Imported by the unified propclaw db_query.py router.
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal, InvalidOperation

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
except ImportError:
    import json as _json
    print(_json.dumps({
        "status": "error",
        "error": "ERPClaw foundation not installed. Install erpclaw-setup first: clawhub install erpclaw-setup",
        "suggestion": "clawhub install erpclaw-setup"
    }))
    sys.exit(1)

REQUIRED_TABLES = ["company", "account", "propclaw_property", "propclaw_lease",
                   "propclaw_trust_account", "propclaw_security_deposit"]
SKILL = "propclaw-accounting"


# ---------------------------------------------------------------------------
# setup-trust-account
# ---------------------------------------------------------------------------
def setup_trust_account(conn, args):
    if not args.company_id:
        err("--company-id is required")
    if not args.property_id:
        err("--property-id is required")
    if not args.account_id:
        err("--account-id is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")
    if not conn.execute("SELECT id FROM propclaw_property WHERE id = ?", (args.property_id,)).fetchone():
        err(f"Property {args.property_id} not found")

    acct = conn.execute("SELECT id, account_type FROM account WHERE id = ?", (args.account_id,)).fetchone()
    if not acct:
        err(f"Account {args.account_id} not found")
    if acct["account_type"] != "trust":
        err(f"Account must be of type 'trust' (current: {acct['account_type']})")

    trust_id = str(uuid.uuid4())
    try:
        conn.execute(
            """INSERT INTO propclaw_trust_account
               (id, company_id, property_id, account_id, bank_name, status)
               VALUES (?,?,?,?,?,?)""",
            (trust_id, args.company_id, args.property_id, args.account_id,
             args.bank_name, "active"))
    except sqlite3.IntegrityError:
        err(f"Trust account already exists for this property")

    audit(conn, SKILL, "setup-trust-account", "propclaw_trust_account", trust_id,
          new_values={"property_id": args.property_id, "account_id": args.account_id})
    conn.commit()
    ok({"trust_account_id": trust_id, "property_id": args.property_id,
        "account_id": args.account_id, "status": "active"})


# ---------------------------------------------------------------------------
# get-trust-account
# ---------------------------------------------------------------------------
def get_trust_account(conn, args):
    if not args.trust_account_id:
        err("--trust-account-id is required")

    row = conn.execute(
        """SELECT t.*, p.name as property_name, a.name as account_name
           FROM propclaw_trust_account t
           JOIN propclaw_property p ON t.property_id = p.id
           JOIN account a ON t.account_id = a.id
           WHERE t.id = ?""",
        (args.trust_account_id,)).fetchone()
    if not row:
        err(f"Trust account {args.trust_account_id} not found")

    data = row_to_dict(row)

    # Calculate trust balance from deposits held
    balance = conn.execute(
        """SELECT COALESCE(SUM(CAST(amount AS REAL) - CAST(deduction_amount AS REAL)), 0) as balance
           FROM propclaw_security_deposit
           WHERE trust_account_id = ? AND status = 'held'""",
        (args.trust_account_id,)).fetchone()
    data["deposits_held_balance"] = str(round_currency(to_decimal(str(balance["balance"]))))

    ok(data)


# ---------------------------------------------------------------------------
# list-trust-accounts
# ---------------------------------------------------------------------------
def list_trust_accounts(conn, args):
    params = []; where = ["1=1"]
    if args.company_id:
        where.append("t.company_id = ?"); params.append(args.company_id)
    if args.property_id:
        where.append("t.property_id = ?"); params.append(args.property_id)

    wc = " AND ".join(where)
    rows = conn.execute(
        f"""SELECT t.*, p.name as property_name, a.name as account_name
            FROM propclaw_trust_account t
            JOIN propclaw_property p ON t.property_id = p.id
            JOIN account a ON t.account_id = a.id
            WHERE {wc} ORDER BY p.name""",
        params).fetchall()

    ok({"trust_accounts": [row_to_dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# generate-owner-statement
# ---------------------------------------------------------------------------
def generate_owner_statement(conn, args):
    if not args.company_id:
        err("--company-id is required")
    if not args.property_id:
        err("--property-id is required")
    if not args.period_start:
        err("--period-start is required")
    if not args.period_end:
        err("--period-end is required")

    prop = conn.execute("SELECT * FROM propclaw_property WHERE id = ?",
                        (args.property_id,)).fetchone()
    if not prop:
        err(f"Property {args.property_id} not found")

    # Calculate income from lease charges in period
    rent_income = conn.execute(
        """SELECT COALESCE(SUM(CAST(lc.amount AS REAL)), 0) as total
           FROM propclaw_lease_charge lc
           JOIN propclaw_lease l ON lc.lease_id = l.id
           WHERE l.property_id = ? AND lc.charge_date >= ? AND lc.charge_date <= ?
                 AND lc.charge_type = 'base_rent'""",
        (args.property_id, args.period_start, args.period_end)).fetchone()

    other_income = conn.execute(
        """SELECT COALESCE(SUM(CAST(lc.amount AS REAL)), 0) as total
           FROM propclaw_lease_charge lc
           JOIN propclaw_lease l ON lc.lease_id = l.id
           WHERE l.property_id = ? AND lc.charge_date >= ? AND lc.charge_date <= ?
                 AND lc.charge_type != 'base_rent'""",
        (args.property_id, args.period_start, args.period_end)).fetchone()

    # Calculate maintenance expenses in period
    maint_expense = conn.execute(
        """SELECT COALESCE(SUM(CAST(actual_cost AS REAL)), 0) as total
           FROM propclaw_work_order
           WHERE property_id = ? AND status = 'completed'
                 AND completed_date >= ? AND completed_date <= ?""",
        (args.property_id, args.period_start, args.period_end)).fetchone()

    gross = round_currency(to_decimal(str(rent_income["total"])))
    other = round_currency(to_decimal(str(other_income["total"])))
    maint = round_currency(to_decimal(str(maint_expense["total"])))

    mgmt_fee_pct = to_decimal(prop["management_fee_pct"] or "0")
    mgmt_fee = round_currency(gross * mgmt_fee_pct / Decimal("100"))

    net = round_currency(gross + other - mgmt_fee - maint)

    stmt_id = str(uuid.uuid4())
    conn.company_id = args.company_id
    stmt_name = get_next_name(conn, "propclaw_owner_statement")

    conn.execute(
        """INSERT INTO propclaw_owner_statement
           (id, naming_series, company_id, property_id, owner_name,
            period_start, period_end, gross_rent, other_income,
            management_fee, maintenance_expense, other_expense,
            net_distribution, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (stmt_id, stmt_name, args.company_id, args.property_id,
         prop["owner_name"] or "Owner", args.period_start, args.period_end,
         str(gross), str(other), str(mgmt_fee), str(maint), "0",
         str(net), "draft"))

    audit(conn, SKILL, "generate-owner-statement", "propclaw_owner_statement", stmt_id,
          new_values={"naming_series": stmt_name, "net": str(net)})
    conn.commit()
    ok({"statement_id": stmt_id, "naming_series": stmt_name,
        "gross_rent": str(gross), "other_income": str(other),
        "management_fee": str(mgmt_fee), "maintenance_expense": str(maint),
        "net_distribution": str(net), "status": "draft"})


# ---------------------------------------------------------------------------
# list-owner-statements
# ---------------------------------------------------------------------------
def list_owner_statements(conn, args):
    params = []; where = ["1=1"]
    if args.company_id:
        where.append("s.company_id = ?"); params.append(args.company_id)
    if args.property_id:
        where.append("s.property_id = ?"); params.append(args.property_id)

    wc = " AND ".join(where)
    total = conn.execute(
        f"SELECT COUNT(*) FROM propclaw_owner_statement s WHERE {wc}", params).fetchone()[0]

    limit = int(args.limit); offset = int(args.offset)
    rows = conn.execute(
        f"""SELECT s.*, p.name as property_name
            FROM propclaw_owner_statement s
            JOIN propclaw_property p ON s.property_id = p.id
            WHERE {wc} ORDER BY s.period_start DESC LIMIT ? OFFSET ?""",
        params + [limit, offset]).fetchall()

    ok({"statements": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": limit, "offset": offset, "has_more": offset + limit < total})


# ---------------------------------------------------------------------------
# record-security-deposit
# ---------------------------------------------------------------------------
def record_security_deposit(conn, args):
    if not args.lease_id:
        err("--lease-id is required")
    if not args.amount:
        err("--amount is required")
    if not args.deposit_date:
        err("--deposit-date is required")

    lease = conn.execute("SELECT * FROM propclaw_lease WHERE id = ?", (args.lease_id,)).fetchone()
    if not lease:
        err(f"Lease {args.lease_id} not found")

    amount = str(round_currency(to_decimal(args.amount)))

    # Find trust account for property
    trust_account_id = args.trust_account_id
    if not trust_account_id:
        trust = conn.execute(
            "SELECT id FROM propclaw_trust_account WHERE property_id = ? AND status = 'active'",
            (lease["property_id"],)).fetchone()
        if trust:
            trust_account_id = trust["id"]

    # Get state for return deadline calculation
    prop = conn.execute("SELECT state FROM propclaw_property WHERE id = ?",
                        (lease["property_id"],)).fetchone()
    state = prop["state"] if prop else None

    # State-specific return deadlines (days after move-out)
    state_deadlines = {
        "CA": 21, "NY": 14, "TX": 30, "FL": 15, "IL": 30,
        "PA": 30, "OH": 30, "GA": 30, "NC": 30, "MI": 30,
    }
    deadline_days = state_deadlines.get(state, 30)

    deposit_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_security_deposit
           (id, lease_id, customer_id, amount, deposit_date, trust_account_id,
            interest_rate, interest_accrued, return_deadline, status)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (deposit_id, args.lease_id, lease["customer_id"], amount,
         args.deposit_date, trust_account_id, args.interest_rate, "0",
         None, "held"))

    audit(conn, SKILL, "record-security-deposit", "propclaw_security_deposit", deposit_id,
          new_values={"amount": amount, "lease_id": args.lease_id})
    conn.commit()
    ok({"security_deposit_id": deposit_id, "amount": amount,
        "trust_account_id": trust_account_id, "return_deadline_days": deadline_days,
        "status": "held"})


# ---------------------------------------------------------------------------
# return-security-deposit
# ---------------------------------------------------------------------------
def return_security_deposit(conn, args):
    if not args.security_deposit_id:
        err("--security-deposit-id is required")
    if not args.return_amount:
        err("--return-amount is required")

    deposit = conn.execute("SELECT * FROM propclaw_security_deposit WHERE id = ?",
                           (args.security_deposit_id,)).fetchone()
    if not deposit:
        err(f"Security deposit {args.security_deposit_id} not found")
    if deposit["status"] not in ("held", "partially_returned"):
        err(f"Deposit must be 'held' or 'partially_returned' (current: {deposit['status']})")

    return_amount = round_currency(to_decimal(args.return_amount))
    deposit_amount = to_decimal(deposit["amount"])
    deduction_total = to_decimal(deposit["deduction_amount"])

    if return_amount > deposit_amount - deduction_total:
        err(f"Return amount ({return_amount}) exceeds available balance ({deposit_amount - deduction_total})")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_status = "returned" if return_amount + deduction_total >= deposit_amount else "partially_returned"

    conn.execute(
        """UPDATE propclaw_security_deposit
           SET return_amount = ?, return_date = ?, status = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (str(return_amount), today, new_status, args.security_deposit_id))

    audit(conn, SKILL, "return-security-deposit", "propclaw_security_deposit",
          args.security_deposit_id,
          new_values={"return_amount": str(return_amount), "status": new_status})
    conn.commit()
    ok({"security_deposit_id": args.security_deposit_id,
        "return_amount": str(return_amount), "return_date": today,
        "status": new_status})


# ---------------------------------------------------------------------------
# add-deposit-deduction
# ---------------------------------------------------------------------------
def add_deposit_deduction(conn, args):
    if not args.security_deposit_id:
        err("--security-deposit-id is required")
    if not args.deduction_type:
        err("--deduction-type is required")
    if not args.deduction_description:
        err("--deduction-description is required")
    if not args.amount:
        err("--amount is required")

    valid_types = ("damages", "unpaid_rent", "cleaning", "other")
    if args.deduction_type not in valid_types:
        err(f"--deduction-type must be one of: {', '.join(valid_types)}")

    deposit = conn.execute("SELECT * FROM propclaw_security_deposit WHERE id = ?",
                           (args.security_deposit_id,)).fetchone()
    if not deposit:
        err(f"Security deposit {args.security_deposit_id} not found")

    amount = round_currency(to_decimal(args.amount))
    current_deductions = to_decimal(deposit["deduction_amount"])
    deposit_amount = to_decimal(deposit["amount"])

    if current_deductions + amount > deposit_amount:
        err(f"Total deductions ({current_deductions + amount}) would exceed deposit ({deposit_amount})")

    deduction_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_deposit_deduction
           (id, security_deposit_id, deduction_type, description, amount,
            invoice_url, receipt_url)
           VALUES (?,?,?,?,?,?,?)""",
        (deduction_id, args.security_deposit_id, args.deduction_type,
         args.deduction_description, str(amount), args.invoice_url, args.receipt_url))

    # Update total deductions on deposit
    new_total = str(round_currency(current_deductions + amount))
    conn.execute(
        "UPDATE propclaw_security_deposit SET deduction_amount = ?, updated_at = datetime('now') WHERE id = ?",
        (new_total, args.security_deposit_id))

    conn.commit()
    ok({"deduction_id": deduction_id, "amount": str(amount),
        "total_deductions": new_total})


# ---------------------------------------------------------------------------
# list-deposit-deductions
# ---------------------------------------------------------------------------
def list_deposit_deductions(conn, args):
    if args.security_deposit_id:
        rows = conn.execute(
            "SELECT * FROM propclaw_deposit_deduction WHERE security_deposit_id = ? ORDER BY created_at",
            (args.security_deposit_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM propclaw_deposit_deduction ORDER BY created_at DESC").fetchall()

    total = sum(to_decimal(r["amount"]) for r in rows)
    ok({"deductions": [row_to_dict(r) for r in rows], "count": len(rows),
        "total_deductions": str(round_currency(total))})


# ---------------------------------------------------------------------------
# generate-1099-report
# ---------------------------------------------------------------------------
def generate_1099_report(conn, args):
    if not args.company_id:
        err("--company-id is required")
    if not args.tax_year:
        err("--tax-year is required")

    tax_year = int(args.tax_year)

    # Calculate vendor payments from completed work orders
    query = """
        SELECT s.id as supplier_id, s.name as vendor_name, s.tax_id,
               COALESCE(SUM(CAST(w.actual_cost AS REAL)), 0) as total_paid
        FROM supplier s
        JOIN propclaw_work_order w ON w.supplier_id = s.id
        WHERE w.company_id = ? AND w.status = 'completed'
              AND w.completed_date >= ? AND w.completed_date < ?
    """
    params = [args.company_id, f"{tax_year}-01-01", f"{tax_year + 1}-01-01"]

    if args.supplier_id:
        query += " AND s.id = ?"
        params.append(args.supplier_id)

    query += " GROUP BY s.id, s.name, s.tax_id HAVING total_paid > 0"
    vendors = conn.execute(query, params).fetchall()

    results = []
    for v in vendors:
        total = round_currency(to_decimal(str(v["total_paid"])))
        needs_1099 = total >= Decimal("600")

        # Upsert 1099 tracking record
        existing = conn.execute(
            "SELECT id FROM propclaw_tax_1099 WHERE company_id = ? AND supplier_id = ? AND tax_year = ?",
            (args.company_id, v["supplier_id"], tax_year)).fetchone()

        if existing:
            conn.execute(
                "UPDATE propclaw_tax_1099 SET total_payments = ?, updated_at = datetime('now') WHERE id = ?",
                (str(total), existing["id"]))
            record_id = existing["id"]
        else:
            record_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO propclaw_tax_1099
                   (id, company_id, supplier_id, tax_year, total_payments,
                    form_type, filing_status, w9_on_file)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (record_id, args.company_id, v["supplier_id"], tax_year,
                 str(total), "1099_nec", "pending", 0))

        results.append({
            "supplier_id": v["supplier_id"],
            "vendor_name": v["vendor_name"],
            "total_payments": str(total),
            "needs_1099": needs_1099,
            "tracking_id": record_id,
        })

    conn.commit()
    ok({"tax_year": tax_year, "vendors": results, "count": len(results),
        "vendors_needing_1099": sum(1 for r in results if r["needs_1099"])})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "setup-trust-account": setup_trust_account,
    "get-trust-account": get_trust_account,
    "list-trust-accounts": list_trust_accounts,
    "generate-owner-statement": generate_owner_statement,
    "list-owner-statements": list_owner_statements,
    "record-security-deposit": record_security_deposit,
    "return-security-deposit": return_security_deposit,
    "add-deposit-deduction": add_deposit_deduction,
    "list-deposit-deductions": list_deposit_deductions,
    "generate-1099-report": generate_1099_report,
}
