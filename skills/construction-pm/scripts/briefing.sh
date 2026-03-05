#!/usr/bin/env bash
# Generate daily construction PM briefing
set -euo pipefail

DATA_DIR="${DATA_DIR:-${OPENCLAW_WORKSPACE:-.}/construction-pm-data}"
DB="$DATA_DIR/jobs.json"

if [ ! -f "$DB" ]; then
    echo "Error: Database not found. Run init.sh first." >&2
    exit 1
fi

STALE_DAYS="${1:-14}"

python3 << PYEOF
import json, datetime, sys

with open("$DB") as f:
    data = json.load(f)

jobs = data.get("jobs", [])
today = datetime.date.today()
stale_threshold = int("$STALE_DAYS")
week_end = today + datetime.timedelta(days=7)

active_statuses = {"lead", "estimate", "sold", "permitted", "scheduled", "in-progress", "complete", "invoiced"}
active = [j for j in jobs if j.get("status") in active_statuses]

print(f"# Daily PM Briefing - {today.strftime('%A, %B %d, %Y')}")
print()

# 1. Pipeline snapshot
status_order = ["lead", "estimate", "sold", "permitted", "scheduled", "in-progress", "complete", "invoiced", "paid"]
counts = {}
values = {}
for j in jobs:
    s = j.get("status", "unknown")
    counts[s] = counts.get(s, 0) + 1
    values[s] = values.get(s, 0) + j.get("value", 0)

total_active = sum(counts.get(s, 0) for s in active_statuses)
total_value = sum(values.get(s, 0) for s in active_statuses)
print(f"## Pipeline: {total_active} active jobs | \${total_value:,.0f}")
print()
for s in status_order:
    if s in counts:
        bar = "#" * min(counts[s], 20)
        print(f"  {s:15} {counts[s]:3}  \${values[s]:>10,.0f}  {bar}")
print()

# 2. Needs attention
print("## Needs Attention")
print()

# Stale jobs
stale_cutoff = (today - datetime.timedelta(days=stale_threshold)).isoformat()
stale = [j for j in active if j.get("updated", "") < stale_cutoff]
if stale:
    stale.sort(key=lambda j: j.get("updated", ""))
    print(f"### Stale ({stale_threshold}+ days since update)")
    for j in stale:
        days = (today - datetime.date.fromisoformat(j.get("updated", today.isoformat()))).days
        print(f"  - **#{j['number']}** {j.get('customer', '?')} - {j.get('status', '?')} - {days} days stale")
    print()

# Permits pending
permits_pending = [j for j in active if j.get("permit_status", "").lower() in ("pending", "submitted", "applied", "review")]
if permits_pending:
    print("### Permits Pending")
    for j in permits_pending:
        days = (today - datetime.date.fromisoformat(j.get("updated", today.isoformat()))).days
        print(f"  - **#{j['number']}** {j.get('customer', '?')} - permit {j.get('permit_status', '?')} ({days}d)")
    print()

# Recently sold, not yet permitted
newly_sold = [j for j in active if j.get("status") == "sold"]
if newly_sold:
    print("### Sold - Needs Permit")
    for j in newly_sold:
        print(f"  - **#{j['number']}** {j.get('customer', '?')} \${j.get('value', 0):,.0f}")
    print()

# 3. This week
scheduled = [j for j in active if j.get("status") in ("scheduled", "in-progress")]
if scheduled:
    print("## Active This Week")
    for j in scheduled:
        print(f"  - **#{j['number']}** {j.get('customer', '?')} [{j.get('status')}] \${j.get('value', 0):,.0f}")
        if j.get("notes"):
            print(f"    {j['notes'][:80]}")
    print()

# 4. Revenue outlook
invoiced = sum(j.get("value", 0) for j in active if j.get("status") == "invoiced")
completed = sum(j.get("value", 0) for j in active if j.get("status") == "complete")
in_progress = sum(j.get("value", 0) for j in active if j.get("status") == "in-progress")

if invoiced or completed or in_progress:
    print("## Revenue Outlook")
    if invoiced: print(f"  Invoiced (awaiting payment): \${invoiced:,.0f}")
    if completed: print(f"  Completed (needs invoice):   \${completed:,.0f}")
    if in_progress: print(f"  In progress:                 \${in_progress:,.0f}")
    print()

# 5. Nothing to report
if not stale and not permits_pending and not newly_sold and not scheduled:
    print("All clear. No items needing immediate attention.")
    print()
PYEOF
