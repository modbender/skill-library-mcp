# Session Wrap Report Template

Use this template for the final inline wrap-up output.

Mode: `execute` or `dry-run`

## Ship State

- Repos checked:
- Commits created:
- Push status:
- Deploy status:
- File placement fixes:
- Task cleanup actions:

## Memory Writes

| Destination | Item | Confidence | Evidence source | TTL | Status |
|---|---|---|---|---|---|
|  |  | low/medium/high |  |  | active/needs-review |

## Findings (applied)

1. ✅ Category: 
   Action: 
   Target: 

## No action needed

1. Category: 
   Reason: 

## Publish queue

- Candidate title:
- Platform:
- Draft path:
- Post status:

## KPIs

- Noise rate:
- Reuse rate:
- Correction rate:

## Blocked items

- Item:
- Blocker:
- Next action:

## Machine-readable JSON

```json
{
  "mode": "execute|dry-run",
  "shipState": {},
  "memoryWrites": [],
  "findingsApplied": [],
  "noActionNeeded": [],
  "publishQueue": [],
  "blockedItems": [],
  "kpis": {
    "noiseRate": 0,
    "reuseRate": 0,
    "correctionRate": 0
  }
}
```

## Optional appendices

- Risk notes:
- Follow-up checks:
