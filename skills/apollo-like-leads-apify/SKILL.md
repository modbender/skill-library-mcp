---
name: apollo-like-leads-apify
description: Use this skill when the user needs B2B lead collection via Apify actor LurATYM4hkEo78GVj (Apollo-like), including filter-based payload building, validated run execution, and JSON/CSV-ready lead output for outreach workflows.
required_env_vars:
  - APIFY_TOKEN
required-env-vars:
  - APIFY_TOKEN
primary_credential: APIFY_TOKEN
primary-credential: APIFY_TOKEN
metadata:
  short-description: Run Apollo-like B2B leads actor via Apify
  openclaw:
    requires:
      env:
        - APIFY_TOKEN
    primaryCredential: APIFY_TOKEN
---

# Apollo-like B2B Leads (Apify Actor)

## Overview

This skill runs the Apify actor `LurATYM4hkEo78GVj` to collect Apollo-style B2B leads with filters such as job title, seniority, location, employee size, industry, and email quality.

Actor link:
- `https://console.apify.com/actors/LurATYM4hkEo78GVj/source`

Use this skill when a user asks to:
- collect B2B contacts similar to Apollo workflows
- fetch leads with verified emails and optional phones
- build payloads for founders/execs by geo and industry
- run repeatable lead collection from script/API

## Scope

- Build validated actor input payloads.
- Run actor with secure token handling (`APIFY_TOKEN` env or `--apify-token`).
- Return normalized summary and raw lead rows.
- Support quick preset runs and custom JSON input.

## Step-by-step workflow

1. Confirm target ICP (titles, seniority, location, company size, industries).
2. Build payload with required lead count and enrichment switches.
3. Run actor using `scripts/apollo_like_leads_actor.py`.
4. Validate lead count and inspect sample rows.
5. Export rows to n8n/Sheets/CSV as needed.

## Authentication

Preferred:

```bash
export APIFY_TOKEN='apify_api_xxx'
```

Alternative:

```bash
python3 scripts/apollo_like_leads_actor.py run \
  --apify-token 'apify_api_xxx' \
  --input-json '{"max_results":50,"person_location_country":["United States"]}'
```

## Quick start commands

### 1) Preset: 50 US founders (verified emails)

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/apollo_like_leads_actor.py quick-founders-us-50
```

### 2) Custom run from inline JSON

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/apollo_like_leads_actor.py run \
  --input-json '{
    "max_results": 1000,
    "job_titles": ["CEO", "Founder", "Co-Founder"],
    "job_title_seniority": ["owner", "cxo"],
    "person_location_country": ["United States"],
    "employee_size": ["11-50", "51-200", "201-500"],
    "email_status": "verified",
    "include_emails": true,
    "include_phones": false
  }'
```

### 3) Custom run from JSON file

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/apollo_like_leads_actor.py run \
  --input-file references/sample_input.json
```

## Output contract

Script returns JSON with:
- `ok`
- `actorId`
- `leadsCount`
- `inputUsed`
- `rows[]`

You can pass `rows` directly to n8n HTTP/Code nodes or map into Google Sheets columns.

## Important rules

- Do not hardcode API keys in workflow templates.
- Keep `max_results` realistic for testing first (e.g., 50-200).
- Use `email_status: "verified"` for higher outreach quality.
- If the user wants phone-heavy output, set `include_phones: true` explicitly.
- Seniority values should match actor enum (`owner`, `cxo`, `vp`, `director`, etc.); this script auto-normalizes common Apollo values like `founder -> owner`.

## References

- `references/actor-input-guide.md`
- `references/troubleshooting.md`
