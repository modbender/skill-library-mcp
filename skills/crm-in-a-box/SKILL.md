---
name: crm-in-a-box
description: Bootstrap and manage an open, file-based CRM using the CRM-in-a-Box protocol (contacts, pipeline, interactions as NDJSON). Use when setting up a new CRM for a company, logging contacts/leads, updating deal stages, or recording interactions — all without any SaaS dependency.
metadata:
  {
    "openclaw":
      {
        "emoji": "📇"
      }
  }
---

# CRM-in-a-Box Skill

An open, agent-native CRM protocol. One directory = one CRM. No vendor lock-in.

## Files

- `contacts.ndjson` — one JSON object per line, each a contact/company record
- `pipeline.ndjson` — deal/opportunity tracking with stages
- `interactions.ndjson` — append-only log of emails, calls, notes, meetings
- `config.yaml` — pipeline stages and labels

## Bootstrap a New CRM

Copy the baseline files into a company directory:

```bash
mkdir -p ./mycompany/crm
cp /path/to/crm-in-a-box/{config.yaml,contacts.ndjson,pipeline.ndjson,interactions.ndjson} ./mycompany/crm/
```

Or start fresh with empty NDJSON files and the default config.

## Contact Schema

```json
{
  "id": "c001",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "company": "Acme Corp",
  "phone": "+1-555-0100",
  "stage": "new",
  "labels": ["hot-lead"],
  "notes": "Referred by John.",
  "created_at": "2026-01-01T00:00:00Z"
}
```

## Pipeline Schema

```json
{
  "id": "p001",
  "contact_id": "c001",
  "stage": "proposal_sent",
  "deal": "Enterprise License",
  "value": 12000,
  "updated_at": "2026-01-15T00:00:00Z"
}
```

## Interaction Schema

```json
{
  "id": "i001",
  "contact_id": "c001",
  "type": "email",
  "summary": "Sent intro email about Denver market sale.",
  "at": "2026-01-15T10:00:00Z"
}
```

## Pipeline Stages (default)

`new` → `contacted` → `meeting_scheduled` → `proposal_sent` → `negotiating` → `won` / `lost`

## Default Labels

`hot-lead`, `warm-lead`, `cold-lead`, `referral`, `conference`, `inbound`, `outbound`

## Agent Instructions

- **Log a contact:** append a JSON line to `contacts.ndjson`
- **Update a stage:** append an updated entry to `pipeline.ndjson` (keep old entries — append-only)
- **Log an interaction:** append to `interactions.ndjson`
- **Search contacts:** `grep -i "name" contacts.ndjson | python3 -m json.tool`
- **List pipeline:** `cat pipeline.ndjson | python3 -c "import sys,json; [print(json.dumps(json.loads(l), indent=2)) for l in sys.stdin]"`

## Forks / Verticals

Fork `config.yaml` to customize stages and labels for your vertical:
- `pm-crm` — Property management (tenants, owners, vendors)
- `saas-crm` — SaaS sales
- `realestate-crm` — Buyers, sellers, listings
- `recruiting-crm` — Candidates, jobs, placements

---

*Part of the [biz-in-a-box](https://biz-in-a-box.org) family of open protocols.*
