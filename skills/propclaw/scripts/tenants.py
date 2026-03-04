#!/usr/bin/env python3
"""propclaw tenants domain module.

Tenant applications, FCRA-compliant screening, and document management.
Imported by the unified propclaw db_query.py router.
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

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

REQUIRED_TABLES = ["company", "customer", "propclaw_property", "propclaw_application"]
SKILL = "propclaw-tenants"

VALID_APP_STATUSES = ("received", "screening", "approved", "denied", "withdrawn")
VALID_SCREENING_TYPES = ("credit", "criminal", "eviction", "income")
VALID_SCREENING_RESULTS = ("pending", "pass", "fail", "review")
VALID_DOC_TYPES = ("lease", "lead_paint_disclosure", "move_in_inspection",
                   "move_out_inspection", "application", "id_copy", "insurance", "w9", "other")
VALID_DELIVERY_METHODS = ("mail", "email", "hand")


# ---------------------------------------------------------------------------
# add-application
# ---------------------------------------------------------------------------
def add_application(conn, args):
    if not args.company_id:
        err("--company-id is required")
    if not args.property_id:
        err("--property-id is required")
    if not args.applicant_name:
        err("--applicant-name is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")
    if not conn.execute("SELECT id FROM propclaw_property WHERE id = ?", (args.property_id,)).fetchone():
        err(f"Property {args.property_id} not found")
    if args.unit_id:
        if not conn.execute("SELECT id FROM propclaw_unit WHERE id = ?", (args.unit_id,)).fetchone():
            err(f"Unit {args.unit_id} not found")

    app_id = str(uuid.uuid4())
    conn.company_id = args.company_id
    app_name = get_next_name(conn, "propclaw_application")

    income = str(round_currency(to_decimal(args.monthly_income or "0"))) if args.monthly_income else None

    conn.execute(
        """INSERT INTO propclaw_application
           (id, naming_series, company_id, property_id, unit_id, applicant_name,
            applicant_email, applicant_phone, desired_move_in, monthly_income,
            employer, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (app_id, app_name, args.company_id, args.property_id, args.unit_id,
         args.applicant_name, args.applicant_email, args.applicant_phone,
         args.desired_move_in, income, args.employer, "received"))

    audit(conn, SKILL, "add-application", "propclaw_application", app_id,
          new_values={"applicant": args.applicant_name, "naming_series": app_name})
    conn.commit()
    ok({"application_id": app_id, "naming_series": app_name, "status": "received"})


# ---------------------------------------------------------------------------
# update-application
# ---------------------------------------------------------------------------
def update_application(conn, args):
    if not args.application_id:
        err("--application-id is required")
    if not conn.execute("SELECT id FROM propclaw_application WHERE id = ?",
                        (args.application_id,)).fetchone():
        err(f"Application {args.application_id} not found")

    updates, params, changed = [], [], []

    if args.applicant_name is not None:
        updates.append("applicant_name = ?"); params.append(args.applicant_name); changed.append("applicant_name")
    if args.applicant_email is not None:
        updates.append("applicant_email = ?"); params.append(args.applicant_email); changed.append("applicant_email")
    if args.applicant_phone is not None:
        updates.append("applicant_phone = ?"); params.append(args.applicant_phone); changed.append("applicant_phone")
    if args.monthly_income is not None:
        updates.append("monthly_income = ?")
        params.append(str(round_currency(to_decimal(args.monthly_income))))
        changed.append("monthly_income")
    if args.employer is not None:
        updates.append("employer = ?"); params.append(args.employer); changed.append("employer")
    if args.desired_move_in is not None:
        updates.append("desired_move_in = ?"); params.append(args.desired_move_in); changed.append("desired_move_in")
    if args.unit_id is not None:
        updates.append("unit_id = ?"); params.append(args.unit_id); changed.append("unit_id")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(args.application_id)
    conn.execute(f"UPDATE propclaw_application SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    ok({"application_id": args.application_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# get-application
# ---------------------------------------------------------------------------
def get_application(conn, args):
    if not args.application_id:
        err("--application-id is required")

    row = conn.execute(
        """SELECT a.*, p.name as property_name, u.unit_number
           FROM propclaw_application a
           JOIN propclaw_property p ON a.property_id = p.id
           LEFT JOIN propclaw_unit u ON a.unit_id = u.id
           WHERE a.id = ?""",
        (args.application_id,)).fetchone()
    if not row:
        err(f"Application {args.application_id} not found")

    data = row_to_dict(row)

    # Include screenings
    screenings = conn.execute(
        "SELECT * FROM propclaw_screening_request WHERE application_id = ?",
        (args.application_id,)).fetchall()
    data["screenings"] = [row_to_dict(s) for s in screenings]

    ok(data)


# ---------------------------------------------------------------------------
# list-applications
# ---------------------------------------------------------------------------
def list_applications(conn, args):
    params = []; where = ["1=1"]
    if args.company_id:
        where.append("a.company_id = ?"); params.append(args.company_id)
    if args.property_id:
        where.append("a.property_id = ?"); params.append(args.property_id)
    if args.status:
        where.append("a.status = ?"); params.append(args.status)

    wc = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM propclaw_application a WHERE {wc}", params).fetchone()[0]

    limit = int(args.limit); offset = int(args.offset)
    rows = conn.execute(
        f"""SELECT a.*, p.name as property_name
            FROM propclaw_application a
            JOIN propclaw_property p ON a.property_id = p.id
            WHERE {wc} ORDER BY a.created_at DESC LIMIT ? OFFSET ?""",
        params + [limit, offset]).fetchall()

    ok({"applications": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": limit, "offset": offset, "has_more": offset + limit < total})


# ---------------------------------------------------------------------------
# approve-application
# ---------------------------------------------------------------------------
def approve_application(conn, args):
    if not args.application_id:
        err("--application-id is required")

    app = conn.execute("SELECT * FROM propclaw_application WHERE id = ?",
                       (args.application_id,)).fetchone()
    if not app:
        err(f"Application {args.application_id} not found")
    if app["status"] not in ("received", "screening"):
        err(f"Application must be in 'received' or 'screening' status (current: {app['status']})")

    # Check all screenings passed (if any)
    failed = conn.execute(
        "SELECT id FROM propclaw_screening_request WHERE application_id = ? AND result = 'fail'",
        (args.application_id,)).fetchone()
    if failed:
        err("Cannot approve — one or more screenings failed")

    # Create customer (tenant) record
    customer_id = str(uuid.uuid4())
    conn.company_id = app["company_id"]
    conn.execute(
        """INSERT INTO customer
           (id, name, email, phone, customer_type, company_id, status)
           VALUES (?,?,?,?,?,?,?)""",
        (customer_id, app["applicant_name"], app["applicant_email"],
         app["applicant_phone"], "individual", app["company_id"], "active"))

    # Update application
    conn.execute(
        "UPDATE propclaw_application SET status = 'approved', customer_id = ?, updated_at = datetime('now') WHERE id = ?",
        (customer_id, args.application_id))

    audit(conn, SKILL, "approve-application", "propclaw_application", args.application_id,
          new_values={"customer_id": customer_id, "status": "approved"})
    conn.commit()
    ok({"application_id": args.application_id, "customer_id": customer_id,
        "tenant_name": app["applicant_name"], "status": "approved"})


# ---------------------------------------------------------------------------
# deny-application
# ---------------------------------------------------------------------------
def deny_application(conn, args):
    if not args.application_id:
        err("--application-id is required")
    if not args.denial_reason:
        err("--denial-reason is required")
    if not args.cra_name:
        err("--cra-name is required (FCRA requirement)")

    app = conn.execute("SELECT * FROM propclaw_application WHERE id = ?",
                       (args.application_id,)).fetchone()
    if not app:
        err(f"Application {args.application_id} not found")
    if app["status"] not in ("received", "screening"):
        err(f"Application must be in 'received' or 'screening' status (current: {app['status']})")

    conn.execute(
        "UPDATE propclaw_application SET status = 'denied', denial_reason = ?, updated_at = datetime('now') WHERE id = ?",
        (args.denial_reason, args.application_id))

    # Create adverse action notice (FCRA requirement)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    notice_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_adverse_action
           (id, application_id, screening_request_id, notice_date, cra_name,
            cra_address, cra_phone, reason, delivery_method)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (notice_id, args.application_id, args.screening_request_id, today,
         args.cra_name, args.cra_address, args.cra_phone, args.denial_reason,
         args.delivery_method))

    audit(conn, SKILL, "deny-application", "propclaw_application", args.application_id,
          new_values={"status": "denied", "adverse_action_id": notice_id})
    conn.commit()
    ok({"application_id": args.application_id, "status": "denied",
        "adverse_action_id": notice_id})


# ---------------------------------------------------------------------------
# add-screening
# ---------------------------------------------------------------------------
def add_screening(conn, args):
    if not args.application_id:
        err("--application-id is required")
    if not args.screening_type:
        err("--screening-type is required")
    if args.screening_type not in VALID_SCREENING_TYPES:
        err(f"--screening-type must be one of: {', '.join(VALID_SCREENING_TYPES)}")

    app = conn.execute("SELECT id, status FROM propclaw_application WHERE id = ?",
                       (args.application_id,)).fetchone()
    if not app:
        err(f"Application {args.application_id} not found")

    consent = 1 if args.consent_obtained and args.consent_obtained.lower() in ("1", "true", "yes") else 0

    screening_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_screening_request
           (id, application_id, screening_type, consent_obtained, consent_date,
            request_date, result, notes)
           VALUES (?,?,?,?,?,?,?,?)""",
        (screening_id, args.application_id, args.screening_type, consent,
         args.consent_date, datetime.now(timezone.utc).strftime("%Y-%m-%d"),
         "pending", args.notes))

    # Update application status to screening
    if app["status"] == "received":
        conn.execute("UPDATE propclaw_application SET status = 'screening', updated_at = datetime('now') WHERE id = ?",
                     (args.application_id,))

    conn.commit()
    ok({"screening_id": screening_id, "screening_type": args.screening_type,
        "consent_obtained": bool(consent), "result": "pending"})


# ---------------------------------------------------------------------------
# get-screening
# ---------------------------------------------------------------------------
def get_screening(conn, args):
    if not args.screening_id:
        err("--screening-id is required")

    row = conn.execute("SELECT * FROM propclaw_screening_request WHERE id = ?",
                       (args.screening_id,)).fetchone()
    if not row:
        err(f"Screening {args.screening_id} not found")
    ok(row_to_dict(row))


# ---------------------------------------------------------------------------
# list-screenings
# ---------------------------------------------------------------------------
def list_screenings(conn, args):
    if args.application_id:
        rows = conn.execute(
            "SELECT * FROM propclaw_screening_request WHERE application_id = ? ORDER BY screening_type",
            (args.application_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM propclaw_screening_request ORDER BY created_at DESC").fetchall()
    ok({"screenings": [row_to_dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# add-document
# ---------------------------------------------------------------------------
def add_document(conn, args):
    if not args.customer_id:
        err("--customer-id is required")
    if not args.document_type:
        err("--document-type is required")
    if not args.file_url:
        err("--file-url is required")
    if args.document_type not in VALID_DOC_TYPES:
        err(f"--document-type must be one of: {', '.join(VALID_DOC_TYPES)}")

    if not conn.execute("SELECT id FROM customer WHERE id = ?", (args.customer_id,)).fetchone():
        err(f"Customer {args.customer_id} not found")

    doc_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_tenant_document
           (id, customer_id, lease_id, document_type, file_url, description, expiry_date)
           VALUES (?,?,?,?,?,?,?)""",
        (doc_id, args.customer_id, args.lease_id, args.document_type,
         args.file_url, args.description, args.expiry_date))

    conn.commit()
    ok({"document_id": doc_id, "document_type": args.document_type})


# ---------------------------------------------------------------------------
# list-documents
# ---------------------------------------------------------------------------
def list_documents(conn, args):
    params = []; where = ["1=1"]
    if args.customer_id:
        where.append("customer_id = ?"); params.append(args.customer_id)
    if args.lease_id:
        where.append("lease_id = ?"); params.append(args.lease_id)
    if args.document_type:
        where.append("document_type = ?"); params.append(args.document_type)

    wc = " AND ".join(where)
    limit = int(args.limit); offset = int(args.offset)
    total = conn.execute(f"SELECT COUNT(*) FROM propclaw_tenant_document WHERE {wc}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT * FROM propclaw_tenant_document WHERE {wc} ORDER BY uploaded_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset]).fetchall()

    ok({"documents": [row_to_dict(r) for r in rows], "total_count": total,
        "limit": limit, "offset": offset, "has_more": offset + limit < total})


# ---------------------------------------------------------------------------
# delete-document
# ---------------------------------------------------------------------------
def delete_document(conn, args):
    if not args.document_id:
        err("--document-id is required")
    if not conn.execute("SELECT id FROM propclaw_tenant_document WHERE id = ?",
                        (args.document_id,)).fetchone():
        err(f"Document {args.document_id} not found")

    conn.execute("DELETE FROM propclaw_tenant_document WHERE id = ?", (args.document_id,))
    conn.commit()
    ok({"deleted": args.document_id})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-application": add_application,
    "update-application": update_application,
    "get-application": get_application,
    "list-applications": list_applications,
    "approve-application": approve_application,
    "deny-application": deny_application,
    "add-screening": add_screening,
    "get-screening": get_screening,
    "list-screenings": list_screenings,
    "add-document": add_document,
    "list-documents": list_documents,
    "delete-document": delete_document,
}
