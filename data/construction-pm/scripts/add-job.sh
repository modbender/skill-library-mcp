#!/usr/bin/env bash
# Add or update a job in the construction PM database
set -euo pipefail

DATA_DIR="${DATA_DIR:-${OPENCLAW_WORKSPACE:-.}/construction-pm-data}"
DB="$DATA_DIR/jobs.json"

if [ ! -f "$DB" ]; then
    echo "Error: Database not found. Run init.sh first." >&2
    exit 1
fi

# Parse arguments
NUMBER="" CUSTOMER="" ADDRESS="" PM="" VALUE="" STATUS="" PERMIT_STATUS="" PERMIT_NUMBER="" NOTES="" TRADE=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --number) NUMBER="$2"; shift 2;;
        --customer) CUSTOMER="$2"; shift 2;;
        --address) ADDRESS="$2"; shift 2;;
        --pm) PM="$2"; shift 2;;
        --value) VALUE="$2"; shift 2;;
        --status) STATUS="$2"; shift 2;;
        --permit-status) PERMIT_STATUS="$2"; shift 2;;
        --permit-number) PERMIT_NUMBER="$2"; shift 2;;
        --notes) NOTES="$2"; shift 2;;
        --trade) TRADE="$2"; shift 2;;
        *) echo "Unknown option: $1" >&2; exit 1;;
    esac
done

if [ -z "$NUMBER" ]; then
    echo "Error: --number is required" >&2
    exit 1
fi

python3 << PYEOF
import json, datetime, sys

db_path = "$DB"
with open(db_path) as f:
    data = json.load(f)

jobs = data.get("jobs", [])
today = datetime.date.today().isoformat()

# Find existing job
existing = None
for i, j in enumerate(jobs):
    if j.get("number") == "$NUMBER":
        existing = i
        break

if existing is not None:
    job = jobs[existing]
    old_status = job.get("status", "")
    
    # Update only provided fields
    if "$CUSTOMER": job["customer"] = "$CUSTOMER"
    if "$ADDRESS": job["address"] = "$ADDRESS"
    if "$PM": job["pm"] = "$PM"
    if "$VALUE": job["value"] = float("$VALUE") if "$VALUE" else job.get("value", 0)
    if "$STATUS": job["status"] = "$STATUS"
    if "$PERMIT_STATUS": job["permit_status"] = "$PERMIT_STATUS"
    if "$PERMIT_NUMBER": job["permit_number"] = "$PERMIT_NUMBER"
    if "$NOTES": job["notes"] = "$NOTES"
    if "$TRADE": job["trade"] = "$TRADE"
    job["updated"] = today
    
    # Log status change
    new_status = job.get("status", "")
    if "$STATUS" and new_status != old_status:
        job.setdefault("history", []).append({
            "date": today,
            "from": old_status,
            "to": new_status,
            "note": "$NOTES" or f"Status changed to {new_status}"
        })
    
    jobs[existing] = job
    print(f"Updated job #{job['number']} - {job.get('customer', 'Unknown')} [{job.get('status', '?')}]")
else:
    job = {
        "number": "$NUMBER",
        "customer": "$CUSTOMER" or "Unknown",
        "address": "$ADDRESS" or "",
        "pm": "$PM" or "",
        "value": float("$VALUE") if "$VALUE" else 0,
        "status": "$STATUS" or "lead",
        "permit_status": "$PERMIT_STATUS" or "",
        "permit_number": "$PERMIT_NUMBER" or "",
        "trade": "$TRADE" or "",
        "notes": "$NOTES" or "",
        "created": today,
        "updated": today,
        "history": [{"date": today, "from": "", "to": "$STATUS" or "lead", "note": "Initial entry"}]
    }
    jobs.append(job)
    print(f"Added job #{job['number']} - {job['customer']} [{job['status']}] \${job['value']:,.0f}")

data["jobs"] = jobs
with open(db_path, "w") as f:
    json.dump(data, f, indent=2)
PYEOF
