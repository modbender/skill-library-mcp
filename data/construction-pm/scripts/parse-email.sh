#!/usr/bin/env bash
# Parse PM emails for job status updates
set -euo pipefail

DATA_DIR="${DATA_DIR:-${OPENCLAW_WORKSPACE:-.}/construction-pm-data}"
DB="$DATA_DIR/jobs.json"

# Read from file or stdin
if [ "${1:-}" = "--file" ] && [ -n "${2:-}" ]; then
    EMAIL_TEXT=$(cat "$2")
elif [ ! -t 0 ]; then
    EMAIL_TEXT=$(cat)
else
    echo "Usage: parse-email.sh --file /path/to/email.txt" >&2
    echo "   or: echo 'email text' | parse-email.sh" >&2
    exit 1
fi

python3 << PYEOF
import re, json, sys

email = """$EMAIL_TEXT"""

# Extract job numbers (common formats: #12043, Job 12043, job #12043, 12043)
job_numbers = list(set(re.findall(r'(?:job\s*#?\s*|#)(\d{4,6})', email, re.IGNORECASE)))
# Also look for standalone 5-digit numbers that could be job numbers
standalone = re.findall(r'\b(\d{5})\b', email)
for n in standalone:
    if n not in job_numbers:
        job_numbers.append(n)

# Extract status keywords
status_map = {
    'approved': ['approved', 'permit approved', 'permits approved', 'got the permit'],
    'scheduled': ['scheduled', 'on the schedule', 'crew scheduled', 'start date'],
    'in-progress': ['started', 'in progress', 'crew on site', 'underway', 'working on'],
    'complete': ['complete', 'completed', 'finished', 'done', 'wrapped up', 'final inspection'],
    'invoiced': ['invoiced', 'sent invoice', 'billed'],
    'paid': ['paid', 'payment received', 'check received'],
    'on-hold': ['on hold', 'delayed', 'waiting', 'hold', 'postponed'],
    'cancelled': ['cancelled', 'canceled', 'cancel'],
}

detected_status = None
for status, keywords in status_map.items():
    for kw in keywords:
        if kw.lower() in email.lower():
            detected_status = status
            break
    if detected_status:
        break

# Extract permit info
permit_mentions = re.findall(r'permit\s*(?:#\s*)?(\w+[-\w]*)', email, re.IGNORECASE)
permit_status = None
if any(w in email.lower() for w in ['permit approved', 'permits approved', 'got the permit']):
    permit_status = 'approved'
elif any(w in email.lower() for w in ['permit submitted', 'submitted permit', 'applied for permit']):
    permit_status = 'submitted'
elif any(w in email.lower() for w in ['permit denied', 'permit rejected']):
    permit_status = 'denied'

# Extract customer names (look for capitalized words near job numbers)
customers = re.findall(r'(?:customer|client|homeowner|mr\.?|mrs\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', email)

# Extract dollar amounts
amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', email)

result = {
    "job_numbers": job_numbers,
    "detected_status": detected_status,
    "permit_status": permit_status,
    "permit_numbers": [p for p in permit_mentions if not p.lower() in ('approved', 'submitted', 'denied', 'pending')],
    "customers": customers,
    "amounts": amounts,
    "raw_length": len(email),
}

print(json.dumps(result, indent=2))

# Summary
if job_numbers or detected_status:
    print(f"\n--- Extracted ---")
    if job_numbers: print(f"Jobs: {', '.join(f'#{n}' for n in job_numbers)}")
    if detected_status: print(f"Status: {detected_status}")
    if permit_status: print(f"Permit: {permit_status}")
    if customers: print(f"Customer: {', '.join(customers)}")
    if amounts: print(f"Amounts: {', '.join(amounts)}")
PYEOF
