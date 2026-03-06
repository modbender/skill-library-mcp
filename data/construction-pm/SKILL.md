---
name: construction-pm
version: 1.0.0
description: "Construction project management toolkit for AI agents. Use when: (1) Tracking construction jobs through the full lifecycle from lead to paid, (2) Generating daily PM briefings on job status and pipeline health, (3) Checking for stale permits or aging jobs that need attention, (4) Parsing emails from project managers for job updates, (5) Monitoring revenue pipeline across all job statuses."
metadata:
  openclaw:
    requires:
      bins: ["bash"]
      env: []
      config: []
    user-invocable: true
---

# Construction PM

Production-tested construction project management toolkit. Built from real roofing company workflows managing 36+ active jobs and $1.8M+ pipeline.

## When to Activate

Use Construction PM when:
1. **Tracking jobs** through the full lifecycle (lead → estimate → sold → permitted → scheduled → in-progress → complete → invoiced → paid)
2. **Generating daily briefings** for project managers on job status and pipeline health
3. **Checking permits** - identifying permits pending longer than threshold days
4. **Parsing emails** from field staff for job status updates
5. **Monitoring pipeline revenue** across all job statuses to forecast cash flow

## Guardrails / Anti-Patterns

**DO:**
- ✓ Initialize the database with `init.sh` before using other commands
- ✓ Use consistent job numbers that match your accounting/CRM system
- ✓ Update job status promptly when conditions change
- ✓ Run daily briefings to catch stale jobs before they fall through cracks
- ✓ Set permit-check thresholds appropriate for your jurisdiction (14-30 days typical)

**DON'T:**
- ✗ Delete job history - status changes are append-only audit trail
- ✗ Skip the stale check - jobs without updates often indicate problems
- ✗ Use generic customer names - be specific for searchability
- ✗ Forget to set permit numbers when available - they're required for inspections
- ✗ Mix currency formats - use plain integers (49000 not $49,000 or 49k)

## Quick Start

```bash
# Initialize the job tracker (creates JSON database)
bash scripts/init.sh

# Or specify a custom data directory
DATA_DIR=/path/to/data bash scripts/init.sh
```

Default data location: `construction-pm-data/` in your workspace.

## Job Pipeline

### Add a job
```bash
bash scripts/add-job.sh \
  --number "12043" \
  --customer "Nichols" \
  --address "123 Main St" \
  --pm "Greg" \
  --value 49000 \
  --status "permitted" \
  --permit-status "approved" \
  --notes "Roof replacement, 30sq"
```

### Update job status
```bash
bash scripts/add-job.sh --number "12043" --status "in-progress" --notes "Crew on site Monday"
```

### View pipeline
```bash
# All jobs
bash scripts/pipeline.sh

# Filter by status
bash scripts/pipeline.sh --status permitted

# Filter by PM
bash scripts/pipeline.sh --pm Greg

# Stale jobs (no update in 14+ days)
bash scripts/pipeline.sh --stale 14

# Summary stats
bash scripts/pipeline.sh --summary
```

## Daily Briefing

```bash
# Generate today's briefing
bash scripts/briefing.sh

# Custom stale threshold
bash scripts/briefing.sh --stale-days 7

# Output to file
bash scripts/briefing.sh > /path/to/briefing.md
```

The briefing includes:
- Jobs starting this week
- Permits pending > 7 days
- Stale jobs (no update in 14+ days)
- Pipeline summary by status
- Revenue at each stage

## Permit Tracking

```bash
# Check all pending permits
bash scripts/permit-check.sh

# Flag permits older than N days
bash scripts/permit-check.sh --threshold 30
```

## Email Parsing

```bash
# Parse a PM email for job updates
bash scripts/parse-email.sh --file /path/to/email.txt

# Parse from stdin
echo "Job 12043 Nichols - permit approved, scheduling crew for next week" | bash scripts/parse-email.sh
```

Extracts: job numbers, customer names, status keywords, permit mentions, dates.

## Job Statuses

| Status | Description |
|--------|-------------|
| `lead` | Initial inquiry, not yet estimated |
| `estimate` | Estimate sent, waiting for approval |
| `sold` | Contract signed, not yet permitted |
| `permitted` | Permits approved, ready to schedule |
| `scheduled` | Crew and materials scheduled |
| `in-progress` | Work underway |
| `complete` | Work done, pending final inspection |
| `invoiced` | Invoice sent |
| `paid` | Payment received |
| `on-hold` | Paused for any reason |
| `cancelled` | Job cancelled |

## Data Format

Jobs are stored as JSON in `construction-pm-data/jobs.json`:

```json
{
  "jobs": [
    {
      "number": "12043",
      "customer": "Nichols",
      "address": "123 Main St",
      "pm": "Greg",
      "value": 49000,
      "status": "permitted",
      "permit_status": "approved",
      "permit_number": "",
      "notes": "Roof replacement, 30sq",
      "created": "2026-02-08",
      "updated": "2026-02-08",
      "history": [
        {"date": "2026-02-08", "from": "", "to": "permitted", "note": "Initial entry"}
      ]
    }
  ]
}
```

## Integration with OpenClaw

The briefing script outputs clean Markdown. Pipe it to your preferred delivery:
- Telegram: `bash scripts/briefing.sh | your-send-script`
- Obsidian vault: `bash scripts/briefing.sh > ~/vault/Inbox/PM-Briefing-$(date +%F).md`
- Email: Combine with `gog gmail send`

## Construction-Specific Features

- **Permit aging**: Flags permits pending longer than threshold
- **Revenue pipeline**: Shows total value at each stage
- **Stale detection**: Catches jobs that fell through the cracks
- **Status history**: Full audit trail of every status change
- **Trade-aware**: Understands roofing, siding, gutters, HVAC, electrical
