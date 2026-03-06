#!/usr/bin/env bash
# View construction job pipeline
set -euo pipefail

DATA_DIR="${DATA_DIR:-${OPENCLAW_WORKSPACE:-.}/construction-pm-data}"
DB="$DATA_DIR/jobs.json"

if [ ! -f "$DB" ]; then
    echo "Error: Database not found. Run init.sh first." >&2
    exit 1
fi

# Parse arguments
FILTER_STATUS="" FILTER_PM="" STALE_DAYS="" SUMMARY=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --status) FILTER_STATUS="$2"; shift 2;;
        --pm) FILTER_PM="$2"; shift 2;;
        --stale) STALE_DAYS="$2"; shift 2;;
        --summary) SUMMARY=true; shift;;
        *) echo "Unknown option: $1" >&2; exit 1;;
    esac
done

python3 << PYEOF
import json, datetime, sys

with open("$DB") as f:
    data = json.load(f)

jobs = data.get("jobs", [])
today = datetime.date.today()
filter_status = "$FILTER_STATUS"
filter_pm = "$FILTER_PM"
stale_days = int("$STALE_DAYS") if "$STALE_DAYS" else 0
summary = $( [ "$SUMMARY" = "true" ] && echo "True" || echo "False" )

# Filter
filtered = jobs
if filter_status:
    filtered = [j for j in filtered if j.get("status", "").lower() == filter_status.lower()]
if filter_pm:
    filtered = [j for j in filtered if filter_pm.lower() in j.get("pm", "").lower()]
if stale_days:
    cutoff = (today - datetime.timedelta(days=stale_days)).isoformat()
    filtered = [j for j in filtered if j.get("updated", "") < cutoff and j.get("status") not in ("paid", "cancelled", "complete")]

if summary:
    # Pipeline summary
    status_order = ["lead", "estimate", "sold", "permitted", "scheduled", "in-progress", "complete", "invoiced", "paid", "on-hold", "cancelled"]
    counts = {}
    values = {}
    for j in jobs:
        s = j.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1
        values[s] = values.get(s, 0) + j.get("value", 0)
    
    print("## Pipeline Summary")
    print(f"**Total:** {len(jobs)} jobs | \${sum(j.get('value', 0) for j in jobs):,.0f}")
    print()
    for s in status_order:
        if s in counts:
            print(f"  {s:15} {counts[s]:3} jobs  \${values[s]:>12,.0f}")
    # Check for unknown statuses
    for s in counts:
        if s not in status_order:
            print(f"  {s:15} {counts[s]:3} jobs  \${values.get(s, 0):>12,.0f}")
else:
    if not filtered:
        if stale_days:
            print(f"No stale jobs (threshold: {stale_days} days)")
        else:
            print("No jobs found matching criteria")
        sys.exit(0)
    
    # Sort by value descending
    filtered.sort(key=lambda j: j.get("value", 0), reverse=True)
    
    if stale_days:
        print(f"## Stale Jobs (no update in {stale_days}+ days)")
    elif filter_status:
        print(f"## Jobs - {filter_status}")
    else:
        print("## All Jobs")
    print()
    
    for j in filtered:
        updated = j.get("updated", "?")
        days_old = (today - datetime.date.fromisoformat(updated)).days if updated != "?" else "?"
        permit = f" | Permit: {j.get('permit_status', 'n/a')}" if j.get("permit_status") else ""
        print(f"  #{j.get('number', '?'):>6} | {j.get('customer', '?'):20} | {j.get('status', '?'):12} | \${j.get('value', 0):>10,.0f} | {days_old}d ago{permit}")
    
    print(f"\n  **{len(filtered)} jobs** | \${sum(j.get('value', 0) for j in filtered):,.0f} total")
PYEOF
