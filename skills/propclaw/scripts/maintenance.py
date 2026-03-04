#!/usr/bin/env python3
"""propclaw maintenance domain module.

Work orders, vendor assignment, and property inspections.
Imported by the unified propclaw db_query.py router.
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
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

REQUIRED_TABLES = ["company", "propclaw_property", "propclaw_work_order", "propclaw_inspection"]
SKILL = "propclaw-maintenance"

VALID_CATEGORIES = ("plumbing", "electrical", "hvac", "appliance", "structural",
                    "general", "landscaping", "pest", "safety")
VALID_PRIORITIES = ("emergency", "urgent", "routine")
VALID_WO_STATUSES = ("open", "assigned", "in_progress", "completed", "cancelled")
VALID_ITEM_TYPES = ("labor", "material", "other")
VALID_INSPECTION_TYPES = ("move_in", "move_out", "routine", "pre_listing")
VALID_INSPECTION_STATUSES = ("scheduled", "completed", "reviewed")
VALID_CONDITIONS = ("excellent", "good", "fair", "poor")
VALID_ITEM_CONDITIONS = ("good", "fair", "poor", "damaged", "missing")
VALID_AREAS = ("kitchen", "bathroom", "bedroom", "living_room", "dining_room",
               "exterior", "garage", "other")
VALID_ITEMS = ("walls", "floors", "ceiling", "windows", "doors",
               "fixtures", "appliances", "cabinets", "other")
VALID_VA_STATUSES = ("assigned", "accepted", "declined", "en_route", "on_site", "completed")


# ---------------------------------------------------------------------------
# add-work-order
# ---------------------------------------------------------------------------
def add_work_order(conn, args):
    if not args.company_id:
        err("--company-id is required")
    if not args.property_id:
        err("--property-id is required")
    if not args.description:
        err("--description is required")
    if not args.reported_date:
        err("--reported-date is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")
    if not conn.execute("SELECT id FROM propclaw_property WHERE id = ?", (args.property_id,)).fetchone():
        err(f"Property {args.property_id} not found")

    category = args.category or "general"
    if category not in VALID_CATEGORIES:
        err(f"--category must be one of: {', '.join(VALID_CATEGORIES)}")
    priority = args.priority or "routine"
    if priority not in VALID_PRIORITIES:
        err(f"--priority must be one of: {', '.join(VALID_PRIORITIES)}")

    pte = 1 if args.permission_to_enter and args.permission_to_enter.lower() in ("1", "true", "yes") else 0

    wo_id = str(uuid.uuid4())
    conn.company_id = args.company_id
    wo_name = get_next_name(conn, "propclaw_work_order")

    conn.execute(
        """INSERT INTO propclaw_work_order
           (id, naming_series, company_id, property_id, unit_id, lease_id,
            customer_id, category, priority, description, reported_date,
            scheduled_date, estimated_cost, permission_to_enter, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (wo_id, wo_name, args.company_id, args.property_id, args.unit_id,
         args.lease_id, args.customer_id, category, priority,
         args.description, args.reported_date, args.scheduled_date,
         str(round_currency(to_decimal(args.estimated_cost or "0"))) if args.estimated_cost else None,
         pte, "open"))

    audit(conn, SKILL, "add-work-order", "propclaw_work_order", wo_id,
          new_values={"naming_series": wo_name, "priority": priority})
    conn.commit()
    ok({"work_order_id": wo_id, "naming_series": wo_name, "priority": priority, "status": "open"})


# ---------------------------------------------------------------------------
# update-work-order
# ---------------------------------------------------------------------------
def update_work_order(conn, args):
    if not args.work_order_id:
        err("--work-order-id is required")
    if not conn.execute("SELECT id FROM propclaw_work_order WHERE id = ?",
                        (args.work_order_id,)).fetchone():
        err(f"Work order {args.work_order_id} not found")

    updates, params, changed = [], [], []

    if args.status is not None:
        if args.status not in VALID_WO_STATUSES:
            err(f"--status must be one of: {', '.join(VALID_WO_STATUSES)}")
        updates.append("status = ?"); params.append(args.status); changed.append("status")
    if args.category is not None:
        if args.category not in VALID_CATEGORIES:
            err(f"--category must be one of: {', '.join(VALID_CATEGORIES)}")
        updates.append("category = ?"); params.append(args.category); changed.append("category")
    if args.priority is not None:
        if args.priority not in VALID_PRIORITIES:
            err(f"--priority must be one of: {', '.join(VALID_PRIORITIES)}")
        updates.append("priority = ?"); params.append(args.priority); changed.append("priority")
    if args.scheduled_date is not None:
        updates.append("scheduled_date = ?"); params.append(args.scheduled_date); changed.append("scheduled_date")
    if args.estimated_cost is not None:
        updates.append("estimated_cost = ?")
        params.append(str(round_currency(to_decimal(args.estimated_cost))))
        changed.append("estimated_cost")
    if args.actual_cost is not None:
        updates.append("actual_cost = ?")
        params.append(str(round_currency(to_decimal(args.actual_cost))))
        changed.append("actual_cost")
    if args.description is not None:
        updates.append("description = ?"); params.append(args.description); changed.append("description")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(args.work_order_id)
    conn.execute(f"UPDATE propclaw_work_order SET {', '.join(updates)} WHERE id = ?", params)
    audit(conn, SKILL, "update-work-order", "propclaw_work_order", args.work_order_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"work_order_id": args.work_order_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# get-work-order
# ---------------------------------------------------------------------------
def get_work_order(conn, args):
    if not args.work_order_id:
        err("--work-order-id is required")

    row = conn.execute(
        """SELECT w.*, p.name as property_name, u.unit_number, c.name as tenant_name,
                  s.name as vendor_name
           FROM propclaw_work_order w
           JOIN propclaw_property p ON w.property_id = p.id
           LEFT JOIN propclaw_unit u ON w.unit_id = u.id
           LEFT JOIN customer c ON w.customer_id = c.id
           LEFT JOIN supplier s ON w.supplier_id = s.id
           WHERE w.id = ?""",
        (args.work_order_id,)).fetchone()
    if not row:
        err(f"Work order {args.work_order_id} not found")

    data = row_to_dict(row)

    items = conn.execute(
        "SELECT * FROM propclaw_work_order_item WHERE work_order_id = ?",
        (args.work_order_id,)).fetchall()
    data["items"] = [row_to_dict(i) for i in items]

    assignments = conn.execute(
        """SELECT va.*, s.name as vendor_name FROM propclaw_vendor_assignment va
           JOIN supplier s ON va.supplier_id = s.id
           WHERE va.work_order_id = ?""",
        (args.work_order_id,)).fetchall()
    data["vendor_assignments"] = [row_to_dict(a) for a in assignments]

    ok(data)


# ---------------------------------------------------------------------------
# list-work-orders
# ---------------------------------------------------------------------------
def list_work_orders(conn, args):
    params = []; where = ["1=1"]
    if args.company_id:
        where.append("w.company_id = ?"); params.append(args.company_id)
    if args.property_id:
        where.append("w.property_id = ?"); params.append(args.property_id)
    if args.status:
        where.append("w.status = ?"); params.append(args.status)
    if args.priority:
        where.append("w.priority = ?"); params.append(args.priority)

    wc = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM propclaw_work_order w WHERE {wc}", params).fetchone()[0]

    limit = int(args.limit); offset = int(args.offset)
    rows = conn.execute(
        f"""SELECT w.*, p.name as property_name, u.unit_number
            FROM propclaw_work_order w
            JOIN propclaw_property p ON w.property_id = p.id
            LEFT JOIN propclaw_unit u ON w.unit_id = u.id
            WHERE {wc}
            ORDER BY CASE w.priority WHEN 'emergency' THEN 1 WHEN 'urgent' THEN 2 ELSE 3 END,
                     w.reported_date DESC
            LIMIT ? OFFSET ?""",
        params + [limit, offset]).fetchall()

    ok({"work_orders": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": limit, "offset": offset, "has_more": offset + limit < total})


# ---------------------------------------------------------------------------
# assign-vendor
# ---------------------------------------------------------------------------
def assign_vendor(conn, args):
    if not args.work_order_id:
        err("--work-order-id is required")
    if not args.supplier_id:
        err("--supplier-id is required")

    wo = conn.execute("SELECT id, status FROM propclaw_work_order WHERE id = ?",
                      (args.work_order_id,)).fetchone()
    if not wo:
        err(f"Work order {args.work_order_id} not found")
    if not conn.execute("SELECT id FROM supplier WHERE id = ?", (args.supplier_id,)).fetchone():
        err(f"Supplier {args.supplier_id} not found")

    assignment_id = str(uuid.uuid4())
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn.execute(
        """INSERT INTO propclaw_vendor_assignment
           (id, work_order_id, supplier_id, assigned_date, estimated_arrival, status)
           VALUES (?,?,?,?,?,?)""",
        (assignment_id, args.work_order_id, args.supplier_id, today,
         args.estimated_arrival, "assigned"))

    # Update work order status and supplier
    conn.execute(
        "UPDATE propclaw_work_order SET status = 'assigned', supplier_id = ?, updated_at = datetime('now') WHERE id = ?",
        (args.supplier_id, args.work_order_id))

    conn.commit()
    ok({"assignment_id": assignment_id, "work_order_id": args.work_order_id,
        "supplier_id": args.supplier_id, "status": "assigned"})


# ---------------------------------------------------------------------------
# update-vendor-assignment
# ---------------------------------------------------------------------------
def update_vendor_assignment(conn, args):
    if not args.assignment_id:
        err("--assignment-id is required")

    row = conn.execute("SELECT * FROM propclaw_vendor_assignment WHERE id = ?",
                       (args.assignment_id,)).fetchone()
    if not row:
        err(f"Assignment {args.assignment_id} not found")

    updates, params, changed = [], [], []

    if args.status is not None:
        if args.status not in VALID_VA_STATUSES:
            err(f"--status must be one of: {', '.join(VALID_VA_STATUSES)}")
        updates.append("status = ?"); params.append(args.status); changed.append("status")
    if args.actual_arrival is not None:
        updates.append("actual_arrival = ?"); params.append(args.actual_arrival); changed.append("actual_arrival")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(args.assignment_id)
    conn.execute(f"UPDATE propclaw_vendor_assignment SET {', '.join(updates)} WHERE id = ?", params)

    # If vendor is on_site, update work order to in_progress
    if args.status == "on_site":
        conn.execute(
            "UPDATE propclaw_work_order SET status = 'in_progress', updated_at = datetime('now') WHERE id = ?",
            (row["work_order_id"],))

    conn.commit()
    ok({"assignment_id": args.assignment_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# complete-work-order
# ---------------------------------------------------------------------------
def complete_work_order(conn, args):
    if not args.work_order_id:
        err("--work-order-id is required")
    if not args.actual_cost:
        err("--actual-cost is required")

    wo = conn.execute("SELECT * FROM propclaw_work_order WHERE id = ?",
                      (args.work_order_id,)).fetchone()
    if not wo:
        err(f"Work order {args.work_order_id} not found")
    if wo["status"] in ("completed", "cancelled"):
        err(f"Work order is already {wo['status']}")

    actual_cost = str(round_currency(to_decimal(args.actual_cost)))
    billable = 1 if args.billable_to_tenant and args.billable_to_tenant.lower() in ("1", "true", "yes") else 0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    conn.execute(
        """UPDATE propclaw_work_order
           SET status = 'completed', actual_cost = ?, completed_date = ?,
               purchase_invoice_id = ?, billable_to_tenant = ?,
               updated_at = datetime('now')
           WHERE id = ?""",
        (actual_cost, today, args.purchase_invoice_id, billable, args.work_order_id))

    # Complete any open vendor assignments
    conn.execute(
        """UPDATE propclaw_vendor_assignment
           SET status = 'completed', updated_at = datetime('now')
           WHERE work_order_id = ? AND status NOT IN ('completed', 'declined')""",
        (args.work_order_id,))

    audit(conn, SKILL, "complete-work-order", "propclaw_work_order", args.work_order_id,
          new_values={"actual_cost": actual_cost, "status": "completed"})
    conn.commit()
    ok({"work_order_id": args.work_order_id, "status": "completed",
        "actual_cost": actual_cost})


# ---------------------------------------------------------------------------
# add-work-order-item
# ---------------------------------------------------------------------------
def add_work_order_item(conn, args):
    if not args.work_order_id:
        err("--work-order-id is required")
    if not args.item_description:
        err("--item-description is required")
    if not args.item_type:
        err("--item-type is required")
    if not args.rate:
        err("--rate is required")
    if args.item_type not in VALID_ITEM_TYPES:
        err(f"--item-type must be one of: {', '.join(VALID_ITEM_TYPES)}")

    if not conn.execute("SELECT id FROM propclaw_work_order WHERE id = ?",
                        (args.work_order_id,)).fetchone():
        err(f"Work order {args.work_order_id} not found")

    qty = to_decimal(args.quantity or "1")
    rate = to_decimal(args.rate)
    amount = round_currency(qty * rate)

    item_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_work_order_item
           (id, work_order_id, description, item_type, quantity, rate, amount)
           VALUES (?,?,?,?,?,?,?)""",
        (item_id, args.work_order_id, args.item_description, args.item_type,
         str(qty), str(round_currency(rate)), str(amount)))

    conn.commit()
    ok({"item_id": item_id, "amount": str(amount)})


# ---------------------------------------------------------------------------
# list-work-order-items
# ---------------------------------------------------------------------------
def list_work_order_items(conn, args):
    if args.work_order_id:
        rows = conn.execute(
            "SELECT * FROM propclaw_work_order_item WHERE work_order_id = ?",
            (args.work_order_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM propclaw_work_order_item ORDER BY created_at DESC").fetchall()
    total = sum(to_decimal(r["amount"]) for r in rows)
    ok({"items": [row_to_dict(r) for r in rows], "count": len(rows),
        "total_amount": str(round_currency(total))})


# ---------------------------------------------------------------------------
# add-inspection
# ---------------------------------------------------------------------------
def add_inspection(conn, args):
    if not args.company_id:
        err("--company-id is required")
    if not args.property_id:
        err("--property-id is required")
    if not args.inspection_type:
        err("--inspection-type is required")
    if not args.inspection_date:
        err("--inspection-date is required")
    if args.inspection_type not in VALID_INSPECTION_TYPES:
        err(f"--inspection-type must be one of: {', '.join(VALID_INSPECTION_TYPES)}")

    if not conn.execute("SELECT id FROM propclaw_property WHERE id = ?", (args.property_id,)).fetchone():
        err(f"Property {args.property_id} not found")

    insp_id = str(uuid.uuid4())
    conn.company_id = args.company_id
    insp_name = get_next_name(conn, "propclaw_inspection")

    conn.execute(
        """INSERT INTO propclaw_inspection
           (id, naming_series, company_id, property_id, unit_id, lease_id,
            inspection_type, inspection_date, inspector_name, status)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (insp_id, insp_name, args.company_id, args.property_id, args.unit_id,
         args.lease_id, args.inspection_type, args.inspection_date,
         args.inspector_name, "scheduled"))

    audit(conn, SKILL, "add-inspection", "propclaw_inspection", insp_id,
          new_values={"naming_series": insp_name, "type": args.inspection_type})
    conn.commit()
    ok({"inspection_id": insp_id, "naming_series": insp_name, "status": "scheduled"})


# ---------------------------------------------------------------------------
# get-inspection
# ---------------------------------------------------------------------------
def get_inspection(conn, args):
    if not args.inspection_id:
        err("--inspection-id is required")

    row = conn.execute(
        """SELECT i.*, p.name as property_name, u.unit_number
           FROM propclaw_inspection i
           JOIN propclaw_property p ON i.property_id = p.id
           LEFT JOIN propclaw_unit u ON i.unit_id = u.id
           WHERE i.id = ?""",
        (args.inspection_id,)).fetchone()
    if not row:
        err(f"Inspection {args.inspection_id} not found")

    data = row_to_dict(row)
    items = conn.execute(
        "SELECT * FROM propclaw_inspection_item WHERE inspection_id = ?",
        (args.inspection_id,)).fetchall()
    data["items"] = [row_to_dict(i) for i in items]
    ok(data)


# ---------------------------------------------------------------------------
# list-inspections
# ---------------------------------------------------------------------------
def list_inspections(conn, args):
    params = []; where = ["1=1"]
    if args.company_id:
        where.append("i.company_id = ?"); params.append(args.company_id)
    if args.property_id:
        where.append("i.property_id = ?"); params.append(args.property_id)
    if args.inspection_type:
        where.append("i.inspection_type = ?"); params.append(args.inspection_type)

    wc = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM propclaw_inspection i WHERE {wc}", params).fetchone()[0]

    limit = int(args.limit); offset = int(args.offset)
    rows = conn.execute(
        f"""SELECT i.*, p.name as property_name, u.unit_number
            FROM propclaw_inspection i
            JOIN propclaw_property p ON i.property_id = p.id
            LEFT JOIN propclaw_unit u ON i.unit_id = u.id
            WHERE {wc} ORDER BY i.inspection_date DESC LIMIT ? OFFSET ?""",
        params + [limit, offset]).fetchall()

    ok({"inspections": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": limit, "offset": offset, "has_more": offset + limit < total})


# ---------------------------------------------------------------------------
# add-inspection-item
# ---------------------------------------------------------------------------
def add_inspection_item(conn, args):
    if not args.inspection_id:
        err("--inspection-id is required")
    if not args.area:
        err("--area is required")
    if not args.item:
        err("--item is required")
    if not args.condition:
        err("--condition is required")
    if args.area not in VALID_AREAS:
        err(f"--area must be one of: {', '.join(VALID_AREAS)}")
    if args.item not in VALID_ITEMS:
        err(f"--item must be one of: {', '.join(VALID_ITEMS)}")
    if args.condition not in VALID_ITEM_CONDITIONS:
        err(f"--condition must be one of: {', '.join(VALID_ITEM_CONDITIONS)}")

    if not conn.execute("SELECT id FROM propclaw_inspection WHERE id = ?",
                        (args.inspection_id,)).fetchone():
        err(f"Inspection {args.inspection_id} not found")

    repair_cost = str(round_currency(to_decimal(args.estimated_repair_cost or "0"))) if args.estimated_repair_cost else None

    item_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_inspection_item
           (id, inspection_id, area, item, condition, description, photo_url, estimated_repair_cost)
           VALUES (?,?,?,?,?,?,?,?)""",
        (item_id, args.inspection_id, args.area, args.item, args.condition,
         args.description, args.photo_url, repair_cost))

    conn.commit()
    ok({"item_id": item_id, "area": args.area, "item": args.item, "condition": args.condition})


# ---------------------------------------------------------------------------
# list-inspection-items
# ---------------------------------------------------------------------------
def list_inspection_items(conn, args):
    if args.inspection_id:
        rows = conn.execute(
            "SELECT * FROM propclaw_inspection_item WHERE inspection_id = ? ORDER BY area, item",
            (args.inspection_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM propclaw_inspection_item ORDER BY area, item").fetchall()
    ok({"items": [row_to_dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-work-order": add_work_order,
    "update-work-order": update_work_order,
    "get-work-order": get_work_order,
    "list-work-orders": list_work_orders,
    "assign-vendor": assign_vendor,
    "update-vendor-assignment": update_vendor_assignment,
    "complete-work-order": complete_work_order,
    "add-work-order-item": add_work_order_item,
    "list-work-order-items": list_work_order_items,
    "add-inspection": add_inspection,
    "get-inspection": get_inspection,
    "list-inspections": list_inspections,
    "add-inspection-item": add_inspection_item,
    "list-inspection-items": list_inspection_items,
}
