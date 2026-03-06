#!/usr/bin/env python3
"""propclaw properties domain module.

Property and unit management for PropClaw. Manages properties, units,
amenities, and photos. Imported by the unified propclaw db_query.py router.
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

# Add shared lib to path
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.naming import get_next_name
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
    from erpclaw_lib.query import Q, P, Table, Field, fn, Order, Criterion
except ImportError:
    import json as _json
    print(_json.dumps({
        "status": "error",
        "error": "ERPClaw foundation not installed. Install erpclaw-setup first: clawhub install erpclaw-setup",
        "suggestion": "clawhub install erpclaw-setup"
    }))
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants & Table References
# ---------------------------------------------------------------------------
REQUIRED_TABLES = ["company", "propclaw_property"]
SKILL = "propclaw-properties"

_t_company = Table("company")
_t_property = Table("propclaw_property")
_t_unit = Table("propclaw_unit")
_t_amenity = Table("propclaw_amenity")
_t_photo = Table("propclaw_property_photo")

VALID_PROPERTY_TYPES = ("residential", "commercial", "mixed")
VALID_PROPERTY_STATUSES = ("active", "inactive", "archived")
VALID_UNIT_TYPES = ("apartment", "house", "condo", "townhouse", "commercial", "storage", "parking")
VALID_UNIT_STATUSES = ("available", "occupied", "maintenance", "reserved")
VALID_AMENITY_SCOPES = ("property", "unit")
VALID_PHOTO_SCOPES = ("property", "unit", "inspection")


# ---------------------------------------------------------------------------
# add-property
# ---------------------------------------------------------------------------
def add_property(conn, args):
    if not args.name:
        err("--name is required")
    if not args.company_id:
        err("--company-id is required")
    if not args.address_line1:
        err("--address-line1 is required")
    if not args.city:
        err("--city is required")
    if not args.state:
        err("--state is required")
    if not args.zip_code:
        err("--zip-code is required")

    if not conn.execute(Q.from_(_t_company).select(_t_company.id).where(
            _t_company.id == P()).get_sql(), (args.company_id,)).fetchone():
        err(f"Company {args.company_id} not found")

    property_type = args.property_type or "residential"
    if property_type not in VALID_PROPERTY_TYPES:
        err(f"--property-type must be one of: {', '.join(VALID_PROPERTY_TYPES)}")

    total_units = int(args.total_units) if args.total_units else 1
    year_built = int(args.year_built) if args.year_built else None
    mgmt_fee = str(round_currency(to_decimal(args.management_fee_pct or "0"))) if args.management_fee_pct else None

    prop_id = str(uuid.uuid4())
    conn.company_id = args.company_id
    prop_name = get_next_name(conn, "propclaw_property")

    try:
        conn.execute(
            """INSERT INTO propclaw_property
               (id, naming_series, company_id, name, property_type, address_line1,
                address_line2, city, state, zip_code, county, year_built,
                total_units, owner_name, owner_contact, management_fee_pct, status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (prop_id, prop_name, args.company_id, args.name, property_type,
             args.address_line1, args.address_line2, args.city, args.state,
             args.zip_code, args.county, year_built, total_units,
             args.owner_name, args.owner_contact, mgmt_fee, "active"))
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[{SKILL}] {e}\n")
        err("Property creation failed — check for duplicates or invalid data")

    audit(conn, SKILL, "add-property", "propclaw_property", prop_id,
          new_values={"name": args.name, "naming_series": prop_name})
    conn.commit()
    ok({"property_id": prop_id, "naming_series": prop_name, "name": args.name})


# ---------------------------------------------------------------------------
# update-property
# ---------------------------------------------------------------------------
def update_property(conn, args):
    if not args.property_id:
        err("--property-id is required")

    row = conn.execute("SELECT * FROM propclaw_property WHERE id = ?",
                       (args.property_id,)).fetchone()
    if not row:
        err(f"Property {args.property_id} not found")

    updates, params, changed = [], [], []

    if args.name is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if args.property_type is not None:
        if args.property_type not in VALID_PROPERTY_TYPES:
            err(f"--property-type must be one of: {', '.join(VALID_PROPERTY_TYPES)}")
        updates.append("property_type = ?"); params.append(args.property_type); changed.append("property_type")
    if args.address_line1 is not None:
        updates.append("address_line1 = ?"); params.append(args.address_line1); changed.append("address_line1")
    if args.address_line2 is not None:
        updates.append("address_line2 = ?"); params.append(args.address_line2); changed.append("address_line2")
    if args.city is not None:
        updates.append("city = ?"); params.append(args.city); changed.append("city")
    if args.state is not None:
        updates.append("state = ?"); params.append(args.state); changed.append("state")
    if args.zip_code is not None:
        updates.append("zip_code = ?"); params.append(args.zip_code); changed.append("zip_code")
    if args.county is not None:
        updates.append("county = ?"); params.append(args.county); changed.append("county")
    if args.year_built is not None:
        updates.append("year_built = ?"); params.append(int(args.year_built)); changed.append("year_built")
    if args.total_units is not None:
        updates.append("total_units = ?"); params.append(int(args.total_units)); changed.append("total_units")
    if args.owner_name is not None:
        updates.append("owner_name = ?"); params.append(args.owner_name); changed.append("owner_name")
    if args.owner_contact is not None:
        updates.append("owner_contact = ?"); params.append(args.owner_contact); changed.append("owner_contact")
    if args.management_fee_pct is not None:
        updates.append("management_fee_pct = ?")
        params.append(str(round_currency(to_decimal(args.management_fee_pct))))
        changed.append("management_fee_pct")
    if args.status is not None:
        if args.status not in VALID_PROPERTY_STATUSES:
            err(f"--status must be one of: {', '.join(VALID_PROPERTY_STATUSES)}")
        updates.append("status = ?"); params.append(args.status); changed.append("status")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(args.property_id)
    conn.execute(f"UPDATE propclaw_property SET {', '.join(updates)} WHERE id = ?", params)

    audit(conn, SKILL, "update-property", "propclaw_property", args.property_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"property_id": args.property_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# get-property
# ---------------------------------------------------------------------------
def get_property(conn, args):
    if not args.property_id:
        err("--property-id is required")

    row = conn.execute("SELECT * FROM propclaw_property WHERE id = ?",
                       (args.property_id,)).fetchone()
    if not row:
        err(f"Property {args.property_id} not found")

    data = row_to_dict(row)

    # Add unit count and occupancy
    unit_stats = conn.execute(
        """SELECT COUNT(*) as total, SUM(CASE WHEN status='occupied' THEN 1 ELSE 0 END) as occupied
           FROM propclaw_unit WHERE property_id = ?""",
        (args.property_id,)).fetchone()
    data["unit_count"] = unit_stats["total"]
    data["occupied_units"] = unit_stats["occupied"] or 0

    ok(data)


# ---------------------------------------------------------------------------
# list-properties
# ---------------------------------------------------------------------------
def list_properties(conn, args):
    params = []
    where = ["1=1"]

    if args.company_id:
        where.append("p.company_id = ?"); params.append(args.company_id)

    if args.status:
        where.append("p.status = ?"); params.append(args.status)
    if args.state:
        where.append("p.state = ?"); params.append(args.state)
    if args.search:
        where.append("(p.name LIKE ? OR p.city LIKE ? OR p.address_line1 LIKE ?)")
        params.extend([f"%{args.search}%"] * 3)

    where_clause = " AND ".join(where)

    total = conn.execute(
        f"SELECT COUNT(*) FROM propclaw_property p WHERE {where_clause}",
        params).fetchone()[0]

    limit = int(args.limit)
    offset = int(args.offset)
    rows = conn.execute(
        f"""SELECT p.*, (SELECT COUNT(*) FROM propclaw_unit u WHERE u.property_id = p.id) as unit_count
            FROM propclaw_property p WHERE {where_clause}
            ORDER BY p.name LIMIT ? OFFSET ?""",
        params + [limit, offset]).fetchall()

    ok({"properties": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": limit, "offset": offset,
        "has_more": offset + limit < total})


# ---------------------------------------------------------------------------
# add-unit
# ---------------------------------------------------------------------------
def add_unit(conn, args):
    if not args.property_id:
        err("--property-id is required")
    if not args.unit_number:
        err("--unit-number is required")

    prop = conn.execute("SELECT id, company_id FROM propclaw_property WHERE id = ?",
                        (args.property_id,)).fetchone()
    if not prop:
        err(f"Property {args.property_id} not found")

    unit_type = args.unit_type or "apartment"
    if unit_type not in VALID_UNIT_TYPES:
        err(f"--unit-type must be one of: {', '.join(VALID_UNIT_TYPES)}")

    bedrooms = int(args.bedrooms) if args.bedrooms else None
    sq_ft = int(args.sq_ft) if args.sq_ft else None
    floor_num = int(args.floor) if args.floor else None
    market_rent = str(round_currency(to_decimal(args.market_rent or "0")))

    unit_id = str(uuid.uuid4())
    conn.company_id = prop["company_id"]
    unit_name = get_next_name(conn, "propclaw_unit")

    try:
        conn.execute(
            """INSERT INTO propclaw_unit
               (id, naming_series, property_id, unit_number, unit_type, bedrooms,
                bathrooms, sq_ft, floor, market_rent, status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (unit_id, unit_name, args.property_id, args.unit_number, unit_type,
             bedrooms, args.bathrooms, sq_ft, floor_num, market_rent, "available"))
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e):
            err(f"Unit {args.unit_number} already exists in this property")
        sys.stderr.write(f"[{SKILL}] {e}\n")
        err("Unit creation failed")

    audit(conn, SKILL, "add-unit", "propclaw_unit", unit_id,
          new_values={"unit_number": args.unit_number, "naming_series": unit_name})
    conn.commit()
    ok({"unit_id": unit_id, "naming_series": unit_name, "unit_number": args.unit_number})


# ---------------------------------------------------------------------------
# update-unit
# ---------------------------------------------------------------------------
def update_unit(conn, args):
    if not args.unit_id:
        err("--unit-id is required")

    row = conn.execute("SELECT * FROM propclaw_unit WHERE id = ?",
                       (args.unit_id,)).fetchone()
    if not row:
        err(f"Unit {args.unit_id} not found")

    updates, params, changed = [], [], []

    if args.unit_number is not None:
        updates.append("unit_number = ?"); params.append(args.unit_number); changed.append("unit_number")
    if args.unit_type is not None:
        if args.unit_type not in VALID_UNIT_TYPES:
            err(f"--unit-type must be one of: {', '.join(VALID_UNIT_TYPES)}")
        updates.append("unit_type = ?"); params.append(args.unit_type); changed.append("unit_type")
    if args.bedrooms is not None:
        updates.append("bedrooms = ?"); params.append(int(args.bedrooms)); changed.append("bedrooms")
    if args.bathrooms is not None:
        updates.append("bathrooms = ?"); params.append(args.bathrooms); changed.append("bathrooms")
    if args.sq_ft is not None:
        updates.append("sq_ft = ?"); params.append(int(args.sq_ft)); changed.append("sq_ft")
    if args.floor is not None:
        updates.append("floor = ?"); params.append(int(args.floor)); changed.append("floor")
    if args.market_rent is not None:
        updates.append("market_rent = ?")
        params.append(str(round_currency(to_decimal(args.market_rent))))
        changed.append("market_rent")
    if args.status is not None:
        if args.status not in VALID_UNIT_STATUSES:
            err(f"--status must be one of: {', '.join(VALID_UNIT_STATUSES)}")
        updates.append("status = ?"); params.append(args.status); changed.append("status")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(args.unit_id)
    conn.execute(f"UPDATE propclaw_unit SET {', '.join(updates)} WHERE id = ?", params)

    audit(conn, SKILL, "update-unit", "propclaw_unit", args.unit_id,
          new_values={"updated_fields": changed})
    conn.commit()
    ok({"unit_id": args.unit_id, "updated_fields": changed})


# ---------------------------------------------------------------------------
# get-unit
# ---------------------------------------------------------------------------
def get_unit(conn, args):
    if not args.unit_id:
        err("--unit-id is required")

    row = conn.execute(
        """SELECT u.*, p.name as property_name, p.address_line1, p.city, p.state
           FROM propclaw_unit u
           JOIN propclaw_property p ON u.property_id = p.id
           WHERE u.id = ?""",
        (args.unit_id,)).fetchone()
    if not row:
        err(f"Unit {args.unit_id} not found")

    ok(row_to_dict(row))


# ---------------------------------------------------------------------------
# list-units
# ---------------------------------------------------------------------------
def list_units(conn, args):
    params = []
    where = ["1=1"]

    if args.property_id:
        where.append("u.property_id = ?"); params.append(args.property_id)

    if args.status:
        where.append("u.status = ?"); params.append(args.status)
    if args.search:
        where.append("u.unit_number LIKE ?"); params.append(f"%{args.search}%")

    where_clause = " AND ".join(where)

    total = conn.execute(
        f"SELECT COUNT(*) FROM propclaw_unit u WHERE {where_clause}",
        params).fetchone()[0]

    limit = int(args.limit)
    offset = int(args.offset)
    rows = conn.execute(
        f"""SELECT u.* FROM propclaw_unit u WHERE {where_clause}
            ORDER BY u.unit_number LIMIT ? OFFSET ?""",
        params + [limit, offset]).fetchall()

    ok({"units": [row_to_dict(r) for r in rows],
        "total_count": total, "limit": limit, "offset": offset,
        "has_more": offset + limit < total})


# ---------------------------------------------------------------------------
# add-amenity
# ---------------------------------------------------------------------------
def add_amenity(conn, args):
    if not args.amenity_name:
        err("--amenity-name is required")
    if not args.property_id and not args.unit_id:
        err("--property-id or --unit-id is required")

    scope = "unit" if args.unit_id else "property"

    if scope == "property":
        if not conn.execute("SELECT id FROM propclaw_property WHERE id = ?",
                            (args.property_id,)).fetchone():
            err(f"Property {args.property_id} not found")
    else:
        if not conn.execute("SELECT id FROM propclaw_unit WHERE id = ?",
                            (args.unit_id,)).fetchone():
            err(f"Unit {args.unit_id} not found")

    amenity_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_amenity (id, property_id, unit_id, amenity_scope, name, description)
           VALUES (?,?,?,?,?,?)""",
        (amenity_id, args.property_id, args.unit_id, scope,
         args.amenity_name, args.description))

    conn.commit()
    ok({"amenity_id": amenity_id, "name": args.amenity_name, "scope": scope})


# ---------------------------------------------------------------------------
# list-amenities
# ---------------------------------------------------------------------------
def list_amenities(conn, args):
    if args.unit_id:
        rows = conn.execute(
            "SELECT * FROM propclaw_amenity WHERE unit_id = ? ORDER BY name",
            (args.unit_id,)).fetchall()
    elif args.property_id:
        rows = conn.execute(
            "SELECT * FROM propclaw_amenity WHERE property_id = ? ORDER BY name",
            (args.property_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM propclaw_amenity ORDER BY name").fetchall()

    ok({"amenities": [row_to_dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# delete-amenity
# ---------------------------------------------------------------------------
def delete_amenity(conn, args):
    if not args.amenity_id:
        err("--amenity-id is required")

    row = conn.execute("SELECT id FROM propclaw_amenity WHERE id = ?",
                       (args.amenity_id,)).fetchone()
    if not row:
        err(f"Amenity {args.amenity_id} not found")

    conn.execute("DELETE FROM propclaw_amenity WHERE id = ?", (args.amenity_id,))
    conn.commit()
    ok({"deleted": args.amenity_id})


# ---------------------------------------------------------------------------
# add-photo
# ---------------------------------------------------------------------------
def add_photo(conn, args):
    if not args.file_url:
        err("--file-url is required")
    if not args.property_id and not args.unit_id:
        err("--property-id or --unit-id is required")

    scope = args.photo_scope or ("unit" if args.unit_id else "property")
    if scope not in VALID_PHOTO_SCOPES:
        err(f"--photo-scope must be one of: {', '.join(VALID_PHOTO_SCOPES)}")

    photo_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO propclaw_property_photo
           (id, property_id, unit_id, photo_scope, file_url, description)
           VALUES (?,?,?,?,?,?)""",
        (photo_id, args.property_id, args.unit_id, scope,
         args.file_url, args.description))

    conn.commit()
    ok({"photo_id": photo_id, "scope": scope})


# ---------------------------------------------------------------------------
# list-photos
# ---------------------------------------------------------------------------
def list_photos(conn, args):
    if args.unit_id:
        rows = conn.execute(
            "SELECT * FROM propclaw_property_photo WHERE unit_id = ? ORDER BY uploaded_at DESC",
            (args.unit_id,)).fetchall()
    elif args.property_id:
        rows = conn.execute(
            "SELECT * FROM propclaw_property_photo WHERE property_id = ? ORDER BY uploaded_at DESC",
            (args.property_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM propclaw_property_photo ORDER BY uploaded_at DESC").fetchall()

    ok({"photos": [row_to_dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# delete-photo
# ---------------------------------------------------------------------------
def delete_photo(conn, args):
    if not args.photo_id:
        err("--photo-id is required")

    row = conn.execute("SELECT id FROM propclaw_property_photo WHERE id = ?",
                       (args.photo_id,)).fetchone()
    if not row:
        err(f"Photo {args.photo_id} not found")

    conn.execute("DELETE FROM propclaw_property_photo WHERE id = ?", (args.photo_id,))
    conn.commit()
    ok({"deleted": args.photo_id})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------
ACTIONS = {
    "add-property": add_property,
    "update-property": update_property,
    "get-property": get_property,
    "list-properties": list_properties,
    "add-unit": add_unit,
    "update-unit": update_unit,
    "get-unit": get_unit,
    "list-units": list_units,
    "add-amenity": add_amenity,
    "list-amenities": list_amenities,
    "delete-amenity": delete_amenity,
    "add-photo": add_photo,
    "list-photos": list_photos,
    "delete-photo": delete_photo,
}
