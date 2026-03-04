#!/usr/bin/env bash
# Check permit statuses and flag aging permits
set -euo pipefail

DATA_DIR="${DATA_DIR:-${OPENCLAW_WORKSPACE:-.}/construction-pm-data}"
DB="$DATA_DIR/jobs.json"

if [ ! -f "$DB" ]; then
    echo "Error: Database not found. Run init.sh first." >&2
    exit 1
fi

THRESHOLD="${1:-30}"

python3 << PYEOF
import json, datetime

with open("$DB") as f:
    data = json.load(f)

jobs = data.get("jobs", [])
today = datetime.date.today()
threshold = int("$THRESHOLD")

pending_statuses = {"pending", "submitted", "applied", "review", "in-review"}
approved_statuses = {"approved", "issued", "granted"}

pending = []
approved = []
missing = []

for j in jobs:
    ps = j.get("permit_status", "").lower()
    status = j.get("status", "").lower()
    
    # Skip cancelled/paid/lead jobs
    if status in ("cancelled", "paid", "lead"):
        continue
    
    if ps in pending_statuses:
        days = (today - datetime.date.fromisoformat(j.get("updated", today.isoformat()))).days
        pending.append((j, days))
    elif ps in approved_statuses:
        approved.append(j)
    elif status in ("sold", "estimate") and not ps:
        missing.append(j)

print("# Permit Status Report")
print()

if pending:
    pending.sort(key=lambda x: -x[1])  # Oldest first
    print(f"## Pending ({len(pending)})")
    for j, days in pending:
        flag = " ⚠️ OVERDUE" if days > threshold else ""
        print(f"  #{j['number']:>6} | {j.get('customer', '?'):20} | {j.get('permit_status', '?'):10} | {days}d{flag}")
    print()

overdue = [p for p in pending if p[1] > threshold]
if overdue:
    print(f"## ⚠️ Overdue ({len(overdue)} permits pending > {threshold} days)")
    for j, days in overdue:
        print(f"  - **#{j['number']}** {j.get('customer', '?')} - {days} days pending")
    print()

if missing:
    print(f"## Missing Permit Info ({len(missing)})")
    for j in missing:
        print(f"  #{j['number']:>6} | {j.get('customer', '?'):20} | Status: {j.get('status', '?')} | No permit data")
    print()

if approved:
    print(f"## Approved ({len(approved)})")
    for j in approved:
        pn = f" #{j.get('permit_number', '')}" if j.get("permit_number") else ""
        print(f"  #{j['number']:>6} | {j.get('customer', '?'):20} | Approved{pn}")
    print()

if not pending and not missing:
    print("All permits accounted for. No action needed.")
PYEOF
