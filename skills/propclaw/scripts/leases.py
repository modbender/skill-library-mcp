#!/usr/bin/env python3
"""propclaw leases domain module.

Lease lifecycle, rent schedules, late fees, and renewals for PropClaw.
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

REQUIRED_TABLES = ["company", "customer", "propclaw_property", "propclaw_unit", "propclaw_lease"]
SKILL = "propclaw-leases"

VALID_LEASE_TYPES = ("fixed", "month_to_month")
VALID_CHARGE_TYPES = ("base_rent", "pet_rent", "parking", "storage", "utility", "other")
VALID_FREQUENCIES = ("weekly", "biweekly", "monthly")
VALID_FEE_TYPES = ("flat", "percentage", "lower_of", "greater_of")


# ---------------------------------------------------------------------------
# add-lease
# ---------------------------------------------------------------------------
def add_lease(conn, args):
    if not args.company_id:
        err("--company-id is required")
    if not args.property_id:
        err("--property-id is required")
    if not args.unit_id:
        err("--unit-id is required")
    if not args.customer_id:
        err("--customer-id is required")
    if not args.start_date:
        err("--start-date is required")
    if not args.monthly_rent:
        err("--monthly-rent is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")
    if not conn.execute("SELECT id FROM propclaw_property WHERE id = ?", (args.property_id,)).fetchone():
        err(f"Property {args.property_id} not found")
    if not conn.execute("SELECT id FROM propclaw_unit WHERE id = ?", (args.unit_id,)).fetchone():
        err(f"Unit {args.unit_id} not found")
    if not conn.execute("SELECT id FROM customer WHERE id = ?", (args.customer_id,)).fetchone():
        err(f"Customer (tenant) {args.customer_id} not found")

    lease_type = args.lease_type or "fixed"
    if lease_type not in VALID_LEASE_TYPES:
        err(f"--lease-type must be one of: {', '.join(VALID_LEASE_TYPES)}")

    monthly_rent = str(round_currency(to_decimal(args.monthly_rent)))
    deposit_amt = str(round_currency(to_decimal(args.security_deposit_amount or "0")))

    lease_id = str(uuid.uuid4())
    conn.company_id = args.company_id
    lease_name = get_next_name(conn, "propclaw_lease")

    try:
        conn.execute(
            """INSERT INTO propclaw_lease
               (id, naming_series, company_id, property_id, unit_id, customer_id,
                lease_type, start_date, end_date, monthly_rent,
                security_deposit_amount, deposit_account_id, status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (lease_id, lease_name, args.company_id, args.property_id, args.unit_id,
             args.customer_id, lease_type, args.start_date, args.end_date,
             monthly_rent, deposit_amt, args.deposit_account_id, "draft"))
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[{SKILL}] {e}\n")
        err("Lease creation failed")

    audit(conn, SKILL, "add-lease", "propclaw_lease", lease_id,
          new_values={"naming_series": lease_name, "tenant": args.customer_id})
    conn.commit()
    ok({"lease_id": lease_id, "naming_series": lease_name, "status": "draft"})


# ---------------------------------------------------------------------------
# update-lease
# ---------------------------------------------------------------------------
def update_lease(conn, args):
    if not args.lease_id:
        err("--lease-id is required")
    if not conn.execute("SELECT id FROM propclaw_lease WHERE id = ?", (args.lease_id,)).fetchone():
        err(f"Lease {args.lease_id} not found")

    updates, params, changed = [], [], []

    if args.monthly_rent is not None:
        updates.append("monthly_rent = ?")
        params.append(str(round_currency(to_decimal(args.monthly_rent))))
        changed.append("monthly_rent")
    if args.end_date is not None:
        updates.append("end_date = ?"); params.append(args.end_date); changed.append("end_date")
    if args.lease_type is not None:
        if args.lease_type not in VALID_LEASE_TYPES:
            err(f"--lease-type must be one of: {', '.join(VALID_LEASE_TYPES)}")
        updates.append("lease_type = ?"); params.append(args.lease_type); changed.append("lease_type")
    if args.deposit_account_id is not None:
        updates.append("deposit_account_id = ?"); params.append(args.deposit_account_id)
        changed.append("deposit_account_id")
    if args.security_deposit_amount is not None:
        updates.append("security_deposit_amount = ?")
        params.append(str(round_currency(to_decimal(args.security_deposit_amount))))
        changed.append("security_deposit_amount")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(args.lease_id)
    conn.execute(f"UPDATE propclaw_lease SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-lease", "propclaw_lease", args.lease_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"lease_id": args.lease_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# get-lease
# ---------------------------------------------------------------------------
def get_lease(conn, args):
    if not args.lease_id:
        err("--lease-id is required")

    row = conn.execute(
        """SELECT l.*, p.name as property_name, u.unit_number, c.name as tenant_name
           FROM propclaw_lease l
           JOIN propclaw_property p ON l.property_id = p.id
           JOIN propclaw_unit u ON l.unit_id = u.id
           JOIN customer c ON l.customer_id = c.id
           WHERE l.id = ?""",
        (args.lease_id,)).fetchone()
    if not row:
        err(f"Lease {args.lease_id} not found")

    data = row_to_dict(row)
    schedules = conn.execute(
        "SELECT * FROM propclaw_rent_schedule WHERE lease_id = ? ORDER BY charge_type",
        (args.lease_id,)).fetchall()
    data["rent_schedules"] = [row_to_dict(s) for s in schedules]
    ok(data)


# ---------------------------------------------------------------------------
# list-leases
# ---------------------------------------------------------------------------
def list_leases(conn, args):
    params = []
    where = ["1=1"]
    if args.company_id:
        where.append("l.company_id = ?"); params.append(args.company_id)
    if args.property_id:
        where.append("l.property_id = ?"); params.append(args.property_id)
    if args.status:
        where.append("l.status = ?"); params.append(args.status)
    if args.customer_id:
        where.append("l.customer_id = ?"); params.append(args.customer_id)

    wc = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM propclaw_lease l WHERE {wc}", params).fetchone()[0]

    limit = int(args.limit); offset = int(args.offset)
    rows = conn.execute(
        f"""SELECT l.*, p.name as property_name, u.unit_number, c.name as tenant_name
            FROM propclaw_lease l
            JOIN propclaw_property p ON l.property_id = p.id
            JOIN propclaw_unit u ON l.unit_id = u.id
            JOIN customer c ON l.customer_id = c.id
            WHERE {wc} ORDER BY l.start_date DESC LIMIT ? OFFSET ?""",
        params + [limit, offset]).fetchall()

    ok({"leases": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": limit, "offset": offset, "has_more": offset + limit < total})


# ---------------------------------------------------------------------------
# activate-lease
# ---------------------------------------------------------------------------
def activate_lease(conn, args):
    if not args.lease_id:
        err("--lease-id is required")

    lease = conn.execute("SELECT * FROM propclaw_lease WHERE id = ?", (args.lease_id,)).fetchone()
    if not lease:
        err(f"Lease {args.lease_id} not found")
    if lease["status"] != "draft":
        err(f"Lease must be in 'draft' status to activate (current: {lease['status']})")

    conn.execute("UPDATE propclaw_unit SET status = 'occupied', updated_at = datetime('now') WHERE id = ?",
                 (lease["unit_id"],))

    move_in = args.move_in_date or lease["start_date"]
    conn.execute(
        "UPDATE propclaw_lease SET status = 'active', move_in_date = ?, updated_at = datetime('now') WHERE id = ?",
        (move_in, args.lease_id))

    # Auto-create base rent schedule if none exists
    if not conn.execute(
            "SELECT id FROM propclaw_rent_schedule WHERE lease_id = ? AND charge_type = 'base_rent'",
            (args.lease_id,)).fetchone():
        conn.execute(
            """INSERT INTO propclaw_rent_schedule
               (id, lease_id, charge_type, description, amount, frequency, start_date, end_date)
               VALUES (?,?,?,?,?,?,?,?)""",
            (str(uuid.uuid4()), args.lease_id, "base_rent", "Monthly Rent",
             lease["monthly_rent"], "monthly", lease["start_date"], lease["end_date"]))

    audit(conn, SKILL, "activate-lease", "propclaw_lease", args.lease_id,
          new_values={"status": "active", "move_in_date": move_in})
    conn.commit()
    ok({"lease_id": args.lease_id, "status": "active", "move_in_date": move_in})


# ---------------------------------------------------------------------------
# terminate-lease
# ---------------------------------------------------------------------------
def terminate_lease(conn, args):
    if not args.lease_id:
        err("--lease-id is required")
    if not args.move_out_date:
        err("--move-out-date is required")

    lease = conn.execute("SELECT * FROM propclaw_lease WHERE id = ?", (args.lease_id,)).fetchone()
    if not lease:
        err(f"Lease {args.lease_id} not found")
    if lease["status"] not in ("active", "expired"):
        err(f"Lease must be active or expired to terminate (current: {lease['status']})")

    conn.execute(
        "UPDATE propclaw_lease SET status = 'terminated', move_out_date = ?, updated_at = datetime('now') WHERE id = ?",
        (args.move_out_date, args.lease_id))
    conn.execute("UPDATE propclaw_unit SET status = 'maintenance', updated_at = datetime('now') WHERE id = ?",
                 (lease["unit_id"],))

    audit(conn, SKILL, "terminate-lease", "propclaw_lease", args.lease_id,
          new_values={"status": "terminated", "move_out_date": args.move_out_date})
    conn.commit()
    ok({"lease_id": args.lease_id, "status": "terminated", "move_out_date": args.move_out_date})


# ---------------------------------------------------------------------------
# add-rent-schedule
# ---------------------------------------------------------------------------
def add_rent_schedule(conn, args):
    if not args.lease_id:
        err("--lease-id is required")
    if not args.charge_type:
        err("--charge-type is required")
    if not args.amount:
        err("--amount is required")
    if args.charge_type not in VALID_CHARGE_TYPES:
        err(f"--charge-type must be one of: {', '.join(VALID_CHARGE_TYPES)}")

    lease = conn.execute("SELECT id, start_date, end_date FROM propclaw_lease WHERE id = ?",
                         (args.lease_id,)).fetchone()
    if not lease:
        err(f"Lease {args.lease_id} not found")

    frequency = args.frequency or "monthly"
    if frequency not in VALID_FREQUENCIES:
        err(f"--frequency must be one of: {', '.join(VALID_FREQUENCIES)}")

    amount = str(round_currency(to_decimal(args.amount)))
    sched_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_rent_schedule
           (id, lease_id, charge_type, description, amount, frequency, start_date, end_date)
           VALUES (?,?,?,?,?,?,?,?)""",
        (sched_id, args.lease_id, args.charge_type,
         args.description or args.charge_type.replace("_", " ").title(),
         amount, frequency, args.start_date or lease["start_date"],
         args.end_date or lease["end_date"]))

    conn.commit()
    ok({"rent_schedule_id": sched_id, "charge_type": args.charge_type, "amount": amount})


# ---------------------------------------------------------------------------
# list-rent-schedules
# ---------------------------------------------------------------------------
def list_rent_schedules(conn, args):
    if args.lease_id:
        rows = conn.execute(
            "SELECT * FROM propclaw_rent_schedule WHERE lease_id = ? ORDER BY charge_type",
            (args.lease_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM propclaw_rent_schedule ORDER BY lease_id, charge_type").fetchall()
    total = sum(to_decimal(r["amount"]) for r in rows)
    ok({"rent_schedules": [row_to_dict(r) for r in rows],
        "count": len(rows), "total_monthly": str(round_currency(total))})


# ---------------------------------------------------------------------------
# delete-rent-schedule
# ---------------------------------------------------------------------------
def delete_rent_schedule(conn, args):
    if not args.rent_schedule_id:
        err("--rent-schedule-id is required")
    if not conn.execute("SELECT id FROM propclaw_rent_schedule WHERE id = ?",
                        (args.rent_schedule_id,)).fetchone():
        err(f"Rent schedule {args.rent_schedule_id} not found")
    conn.execute("DELETE FROM propclaw_rent_schedule WHERE id = ?", (args.rent_schedule_id,))
    conn.commit()
    ok({"deleted": args.rent_schedule_id})


# ---------------------------------------------------------------------------
# generate-charges
# ---------------------------------------------------------------------------
def generate_charges(conn, args):
    if not args.lease_id:
        err("--lease-id is required")
    if not args.charge_date:
        err("--charge-date is required")

    lease = conn.execute("SELECT * FROM propclaw_lease WHERE id = ?", (args.lease_id,)).fetchone()
    if not lease:
        err(f"Lease {args.lease_id} not found")
    if lease["status"] != "active":
        err(f"Lease must be active to generate charges (current: {lease['status']})")

    schedules = conn.execute(
        """SELECT * FROM propclaw_rent_schedule
           WHERE lease_id = ? AND start_date <= ? AND (end_date IS NULL OR end_date >= ?)""",
        (args.lease_id, args.charge_date, args.charge_date)).fetchall()

    created = []
    for sched in schedules:
        if conn.execute(
                "SELECT id FROM propclaw_lease_charge WHERE lease_id = ? AND charge_date = ? AND charge_type = ?",
                (args.lease_id, args.charge_date, sched["charge_type"])).fetchone():
            continue
        charge_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO propclaw_lease_charge
               (id, lease_id, charge_date, charge_type, description, amount, status)
               VALUES (?,?,?,?,?,?,?)""",
            (charge_id, args.lease_id, args.charge_date, sched["charge_type"],
             sched["description"], sched["amount"], "pending"))
        created.append({"charge_id": charge_id, "type": sched["charge_type"], "amount": sched["amount"]})

    conn.commit()
    ok({"lease_id": args.lease_id, "charge_date": args.charge_date,
        "charges_created": len(created), "charges": created})


# ---------------------------------------------------------------------------
# list-charges
# ---------------------------------------------------------------------------
def list_charges(conn, args):
    params = []; where = ["1=1"]
    if args.lease_id:
        where.append("lease_id = ?"); params.append(args.lease_id)
    if args.charge_status:
        where.append("status = ?"); params.append(args.charge_status)
    wc = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM propclaw_lease_charge WHERE {wc}", params).fetchone()[0]
    limit = int(args.limit); offset = int(args.offset)
    rows = conn.execute(
        f"SELECT * FROM propclaw_lease_charge WHERE {wc} ORDER BY charge_date DESC, charge_type LIMIT ? OFFSET ?",
        params + [limit, offset]).fetchall()
    ok({"charges": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": limit, "offset": offset, "has_more": offset + limit < total})


# ---------------------------------------------------------------------------
# add-late-fee-rule
# ---------------------------------------------------------------------------
def add_late_fee_rule(conn, args):
    if not args.company_id:
        err("--company-id is required")
    if not args.state:
        err("--state is required")
    if not args.fee_type:
        err("--fee-type is required")
    if args.fee_type not in VALID_FEE_TYPES:
        err(f"--fee-type must be one of: {', '.join(VALID_FEE_TYPES)}")
    if not conn.execute("SELECT id FROM company WHERE id = ?", (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    rule_id = str(uuid.uuid4())
    try:
        conn.execute(
            """INSERT INTO propclaw_late_fee_rule
               (id, company_id, state, fee_type, flat_amount, percentage_rate,
                grace_days, max_cap, is_default)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (rule_id, args.company_id, args.state.upper(), args.fee_type,
             str(round_currency(to_decimal(args.flat_amount or "0"))) if args.flat_amount else None,
             args.percentage_rate,
             int(args.grace_days) if args.grace_days else 0,
             str(round_currency(to_decimal(args.max_cap or "0"))) if args.max_cap else None,
             0))
    except sqlite3.IntegrityError:
        err(f"Late fee rule already exists for state {args.state.upper()}")
    conn.commit()
    ok({"late_fee_rule_id": rule_id, "state": args.state.upper(), "fee_type": args.fee_type})


# ---------------------------------------------------------------------------
# list-late-fee-rules
# ---------------------------------------------------------------------------
def list_late_fee_rules(conn, args):
    if args.company_id and args.state:
        rows = conn.execute(
            "SELECT * FROM propclaw_late_fee_rule WHERE company_id = ? AND state = ?",
            (args.company_id, args.state.upper())).fetchall()
    elif args.company_id:
        rows = conn.execute(
            "SELECT * FROM propclaw_late_fee_rule WHERE company_id = ? ORDER BY state",
            (args.company_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM propclaw_late_fee_rule ORDER BY state").fetchall()
    ok({"late_fee_rules": [row_to_dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# apply-late-fees
# ---------------------------------------------------------------------------
def apply_late_fees(conn, args):
    if not args.company_id:
        err("--company-id is required")
    if not args.as_of_date:
        err("--as-of-date is required")

    as_of = date.fromisoformat(args.as_of_date)
    leases = conn.execute(
        """SELECT l.*, p.state FROM propclaw_lease l
           JOIN propclaw_property p ON l.property_id = p.id
           WHERE l.company_id = ? AND l.status = 'active'""",
        (args.company_id,)).fetchall()

    applied = []
    for lease in leases:
        rule = conn.execute(
            "SELECT * FROM propclaw_late_fee_rule WHERE company_id = ? AND state = ?",
            (args.company_id, lease["state"])).fetchone()
        if not rule:
            continue

        grace_cutoff = (as_of - timedelta(days=rule["grace_days"])).isoformat()
        unpaid = conn.execute(
            """SELECT * FROM propclaw_lease_charge
               WHERE lease_id = ? AND status = 'pending' AND charge_date <= ? AND charge_type != 'late_fee'""",
            (lease["id"], grace_cutoff)).fetchall()

        for charge in unpaid:
            if conn.execute(
                    "SELECT id FROM propclaw_lease_charge WHERE lease_id = ? AND charge_date = ? AND charge_type = 'late_fee' AND description LIKE ?",
                    (lease["id"], args.as_of_date, f"%{charge['id'][:8]}%")).fetchone():
                continue

            charge_amt = to_decimal(charge["amount"])
            if rule["fee_type"] == "flat":
                fee = to_decimal(rule["flat_amount"] or "0")
            elif rule["fee_type"] == "percentage":
                fee = charge_amt * to_decimal(rule["percentage_rate"] or "0") / Decimal("100")
            elif rule["fee_type"] == "lower_of":
                fee = min(to_decimal(rule["flat_amount"] or "0"),
                          charge_amt * to_decimal(rule["percentage_rate"] or "0") / Decimal("100"))
            else:
                fee = max(to_decimal(rule["flat_amount"] or "0"),
                          charge_amt * to_decimal(rule["percentage_rate"] or "0") / Decimal("100"))

            if rule["max_cap"]:
                fee = min(fee, to_decimal(rule["max_cap"]))
            fee = round_currency(fee)
            if fee <= 0:
                continue

            fee_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO propclaw_lease_charge
                   (id, lease_id, charge_date, charge_type, description, amount, status)
                   VALUES (?,?,?,?,?,?,?)""",
                (fee_id, lease["id"], args.as_of_date, "late_fee",
                 f"Late fee for charge {charge['id'][:8]}", str(fee), "pending"))
            applied.append({"lease_id": lease["id"], "charge_id": fee_id, "amount": str(fee)})

    conn.commit()
    ok({"as_of_date": args.as_of_date, "late_fees_applied": len(applied), "details": applied})


# ---------------------------------------------------------------------------
# propose-renewal
# ---------------------------------------------------------------------------
def propose_renewal(conn, args):
    if not args.lease_id:
        err("--lease-id is required")
    if not args.new_start_date:
        err("--new-start-date is required")
    if not args.new_monthly_rent:
        err("--new-monthly-rent is required")

    lease = conn.execute("SELECT * FROM propclaw_lease WHERE id = ?", (args.lease_id,)).fetchone()
    if not lease:
        err(f"Lease {args.lease_id} not found")

    new_rent = str(round_currency(to_decimal(args.new_monthly_rent)))
    old_rent = to_decimal(lease["monthly_rent"])
    increase_pct = args.rent_increase_pct
    if not increase_pct and old_rent > 0:
        increase_pct = str(round_currency(
            (to_decimal(new_rent) - old_rent) / old_rent * Decimal("100")))

    renewal_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_lease_renewal
           (id, lease_id, previous_lease_id, new_start_date, new_end_date,
            new_monthly_rent, rent_increase_pct, status)
           VALUES (?,?,?,?,?,?,?,?)""",
        (renewal_id, args.lease_id, args.lease_id, args.new_start_date,
         args.new_end_date, new_rent, increase_pct, "proposed"))
    conn.commit()
    ok({"renewal_id": renewal_id, "new_monthly_rent": new_rent,
        "rent_increase_pct": increase_pct, "status": "proposed"})


# ---------------------------------------------------------------------------
# accept-renewal
# ---------------------------------------------------------------------------
def accept_renewal(conn, args):
    if not args.renewal_id:
        err("--renewal-id is required")

    renewal = conn.execute("SELECT * FROM propclaw_lease_renewal WHERE id = ?",
                           (args.renewal_id,)).fetchone()
    if not renewal:
        err(f"Renewal {args.renewal_id} not found")
    if renewal["status"] != "proposed":
        err(f"Renewal must be 'proposed' to accept (current: {renewal['status']})")

    old_lease = conn.execute("SELECT * FROM propclaw_lease WHERE id = ?",
                             (renewal["lease_id"],)).fetchone()
    if not old_lease:
        err("Original lease not found")

    new_lease_id = str(uuid.uuid4())
    conn.company_id = old_lease["company_id"]
    new_name = get_next_name(conn, "propclaw_lease")

    conn.execute(
        """INSERT INTO propclaw_lease
           (id, naming_series, company_id, property_id, unit_id, customer_id,
            lease_type, start_date, end_date, monthly_rent,
            security_deposit_amount, deposit_account_id, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (new_lease_id, new_name, old_lease["company_id"], old_lease["property_id"],
         old_lease["unit_id"], old_lease["customer_id"], old_lease["lease_type"],
         renewal["new_start_date"], renewal["new_end_date"],
         renewal["new_monthly_rent"], old_lease["security_deposit_amount"],
         old_lease["deposit_account_id"], "active"))

    conn.execute("UPDATE propclaw_lease SET status = 'renewed', updated_at = datetime('now') WHERE id = ?",
                 (old_lease["id"],))
    conn.execute("UPDATE propclaw_lease_renewal SET status = 'accepted', updated_at = datetime('now') WHERE id = ?",
                 (args.renewal_id,))

    conn.execute(
        """INSERT INTO propclaw_rent_schedule
           (id, lease_id, charge_type, description, amount, frequency, start_date, end_date)
           VALUES (?,?,?,?,?,?,?,?)""",
        (str(uuid.uuid4()), new_lease_id, "base_rent", "Monthly Rent",
         renewal["new_monthly_rent"], "monthly", renewal["new_start_date"], renewal["new_end_date"]))

    audit(conn, SKILL, "accept-renewal", "propclaw_lease", new_lease_id,
          new_values={"previous_lease": old_lease["id"], "new_rent": renewal["new_monthly_rent"]})
    conn.commit()
    ok({"new_lease_id": new_lease_id, "naming_series": new_name,
        "previous_lease_id": old_lease["id"], "status": "active"})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-lease": add_lease,
    "update-lease": update_lease,
    "get-lease": get_lease,
    "list-leases": list_leases,
    "activate-lease": activate_lease,
    "terminate-lease": terminate_lease,
    "add-rent-schedule": add_rent_schedule,
    "list-rent-schedules": list_rent_schedules,
    "delete-rent-schedule": delete_rent_schedule,
    "generate-charges": generate_charges,
    "list-charges": list_charges,
    "add-late-fee-rule": add_late_fee_rule,
    "list-late-fee-rules": list_late_fee_rules,
    "apply-late-fees": apply_late_fees,
    "propose-renewal": propose_renewal,
    "accept-renewal": accept_renewal,
}
