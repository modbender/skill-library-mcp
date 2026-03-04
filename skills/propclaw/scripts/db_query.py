#!/usr/bin/env python3
"""propclaw — db_query.py (unified router)

AI-native property management for US landlords. Routes all 66 actions
across 5 domain modules: properties, leases, tenants, maintenance, accounting.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sys

# Add shared lib to path
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
    from erpclaw_lib.validation import check_input_lengths
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.dependencies import check_required_tables
except ImportError:
    import json as _json
    print(_json.dumps({
        "status": "error",
        "error": "ERPClaw foundation not installed. Install erpclaw-setup first: clawhub install erpclaw-setup",
        "suggestion": "clawhub install erpclaw-setup"
    }))
    sys.exit(1)

# Add this script's directory so domain modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from properties import ACTIONS as PROP_ACTIONS
from leases import ACTIONS as LEASE_ACTIONS
from tenants import ACTIONS as TENANT_ACTIONS
from maintenance import ACTIONS as MAINT_ACTIONS
from accounting import ACTIONS as ACCT_ACTIONS

# ---------------------------------------------------------------------------
# Merge all domain actions into one router
# ---------------------------------------------------------------------------
SKILL = "propclaw"
REQUIRED_TABLES = ["company", "propclaw_property"]

ACTIONS = {}
ACTIONS.update(PROP_ACTIONS)
ACTIONS.update(LEASE_ACTIONS)
ACTIONS.update(TENANT_ACTIONS)
ACTIONS.update(MAINT_ACTIONS)
ACTIONS.update(ACCT_ACTIONS)
ACTIONS["status"] = lambda conn, args: ok({
    "skill": SKILL,
    "version": "1.0.0",
    "actions_available": len([k for k in ACTIONS if k != "status"]),
    "domains": ["properties", "leases", "tenants", "maintenance", "accounting"],
    "database": DEFAULT_DB_PATH,
})


def main():
    parser = argparse.ArgumentParser(description="propclaw")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)

    # -- Properties --
    parser.add_argument("--property-id")
    parser.add_argument("--company-id")
    parser.add_argument("--name")
    parser.add_argument("--property-type")
    parser.add_argument("--address-line1")
    parser.add_argument("--address-line2")
    parser.add_argument("--city")
    parser.add_argument("--state")
    parser.add_argument("--zip-code")
    parser.add_argument("--county")
    parser.add_argument("--year-built")
    parser.add_argument("--total-units")
    parser.add_argument("--owner-name")
    parser.add_argument("--owner-contact")
    parser.add_argument("--management-fee-pct")
    parser.add_argument("--status")
    parser.add_argument("--unit-id")
    parser.add_argument("--unit-number")
    parser.add_argument("--unit-type")
    parser.add_argument("--bedrooms")
    parser.add_argument("--bathrooms")
    parser.add_argument("--sq-ft")
    parser.add_argument("--area")
    parser.add_argument("--floor")
    parser.add_argument("--market-rent")
    parser.add_argument("--amenity-id")
    parser.add_argument("--amenity-name")
    parser.add_argument("--category")
    parser.add_argument("--description")
    parser.add_argument("--photo-id")
    parser.add_argument("--file-url")
    parser.add_argument("--photo-scope")

    # -- Leases --
    parser.add_argument("--lease-id")
    parser.add_argument("--customer-id")
    parser.add_argument("--lease-type")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--monthly-rent")
    parser.add_argument("--security-deposit-amount")
    parser.add_argument("--deposit-account-id")
    parser.add_argument("--move-in-date")
    parser.add_argument("--move-out-date")
    parser.add_argument("--charge-status")
    parser.add_argument("--charge-type")
    parser.add_argument("--charge-date")
    parser.add_argument("--rent-schedule-id")
    parser.add_argument("--scheduled-date")
    parser.add_argument("--fee-type")
    parser.add_argument("--flat-amount")
    parser.add_argument("--percentage-rate")
    parser.add_argument("--grace-days")
    parser.add_argument("--max-cap")
    parser.add_argument("--frequency")
    parser.add_argument("--as-of-date")
    parser.add_argument("--new-end-date")
    parser.add_argument("--new-start-date")
    parser.add_argument("--new-monthly-rent")
    parser.add_argument("--rent-increase-pct")
    parser.add_argument("--renewal-id")

    # -- Tenants --
    parser.add_argument("--application-id")
    parser.add_argument("--applicant-name")
    parser.add_argument("--applicant-phone")
    parser.add_argument("--applicant-email")
    parser.add_argument("--monthly-income")
    parser.add_argument("--desired-move-in")
    parser.add_argument("--employer")
    parser.add_argument("--screening-id")
    parser.add_argument("--screening-request-id")
    parser.add_argument("--screening-type")
    parser.add_argument("--consent-obtained")
    parser.add_argument("--consent-date")
    parser.add_argument("--cra-name")
    parser.add_argument("--cra-phone")
    parser.add_argument("--cra-address")
    parser.add_argument("--denial-reason")
    parser.add_argument("--delivery-method")
    parser.add_argument("--document-id")
    parser.add_argument("--document-type")
    parser.add_argument("--expiry-date")

    # -- Maintenance --
    parser.add_argument("--work-order-id")
    parser.add_argument("--priority")
    parser.add_argument("--reported-date")
    parser.add_argument("--estimated-cost")
    parser.add_argument("--actual-cost")
    parser.add_argument("--supplier-id")
    parser.add_argument("--purchase-invoice-id")
    parser.add_argument("--permission-to-enter")
    parser.add_argument("--assignment-id")
    parser.add_argument("--estimated-arrival")
    parser.add_argument("--actual-arrival")
    parser.add_argument("--item-type")
    parser.add_argument("--item-description")
    parser.add_argument("--quantity")
    parser.add_argument("--rate")
    parser.add_argument("--billable-to-tenant")
    parser.add_argument("--inspection-id")
    parser.add_argument("--inspection-type")
    parser.add_argument("--inspection-date")
    parser.add_argument("--inspector-name")
    parser.add_argument("--item")
    parser.add_argument("--condition")
    parser.add_argument("--overall-condition")
    parser.add_argument("--photo-url")
    parser.add_argument("--estimated-repair-cost")

    # -- Accounting --
    parser.add_argument("--account-id")
    parser.add_argument("--trust-account-id")
    parser.add_argument("--bank-name")
    parser.add_argument("--period-start")
    parser.add_argument("--period-end")
    parser.add_argument("--security-deposit-id")
    parser.add_argument("--amount")
    parser.add_argument("--deposit-date")
    parser.add_argument("--trust-account-id-ref", dest="trust_account_id_for_deposit")
    parser.add_argument("--return-amount")
    parser.add_argument("--deduction-type")
    parser.add_argument("--deduction-description")
    parser.add_argument("--invoice-url")
    parser.add_argument("--receipt-url")
    parser.add_argument("--tax-year")
    parser.add_argument("--interest-rate")
    parser.add_argument("--notes")

    # -- Shared --
    parser.add_argument("--search")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)

    args, _unknown = parser.parse_known_args()
    check_input_lengths(args)

    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = "clawhub install erpclaw-setup && clawhub install propclaw"
        print(json.dumps(_dep, indent=2))
        conn.close()
        sys.exit(1)

    try:
        ACTIONS[args.action](conn, args)
    except Exception as e:
        conn.rollback()
        sys.stderr.write(f"[{SKILL}] {e}\n")
        err(str(e))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
