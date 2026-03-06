# Apollo-like B2B Leads Scraper Skill for OpenClaw (Apify Actor)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Apify Actor](https://img.shields.io/badge/Apify-LurATYM4hkEo78GVj-ff6b00)](https://console.apify.com/actors/LurATYM4hkEo78GVj/source)
[![Skill Type](https://img.shields.io/badge/OpenClaw-Skill-111827)](./SKILL.md)

This repository provides a production-ready **OpenClaw skill** for running an **Apollo-like B2B leads scraper** through Apify actor [`LurATYM4hkEo78GVj`](https://console.apify.com/actors/LurATYM4hkEo78GVj/source).

If you are looking for an **Apollo alternative**, **B2B contact scraper**, **lead generation automation**, or **Apify sales prospecting workflow**, this skill is built for that use case.

## Why this skill

Most teams lose time on the same problems:
- manually crafting payloads for each target ICP
- inconsistent filtering for titles, seniority, geo, and company size
- weak credential handling inside scripts and workflows
- non-standard outputs that are hard to move into n8n or Google Sheets

This skill solves that with:
- validated payload execution against a real Apify actor
- secure auth using `APIFY_TOKEN` (env var or CLI)
- reusable presets (including **50 US founders**)
- JSON output ready for n8n, Sheets, and CRM pipelines

## Actor and stack

- Apify actor: [`LurATYM4hkEo78GVj`](https://console.apify.com/actors/LurATYM4hkEo78GVj/source)
- Runtime: Python 3.10+
- Auth: `APIFY_TOKEN`
- Use case: B2B lead scraping, outbound list building, Apollo-style prospecting

## Quick start

### 1) Set token

```bash
export APIFY_TOKEN='apify_api_xxx'
```

### 2) Run preset: 50 US founders

```bash
python3 scripts/apollo_like_leads_actor.py quick-founders-us-50
```

### 3) Run custom payload from file

```bash
python3 scripts/apollo_like_leads_actor.py run --input-file references/sample_input.json
```

### 4) Run custom payload inline

```bash
python3 scripts/apollo_like_leads_actor.py run --input-json '{
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

## Input fields (Apollo-like filters)

Common payload fields:
- `max_results`
- `job_titles`
- `job_title_seniority`
- `person_location_country`
- `person_location_region`
- `employee_size`
- `industries`
- `email_status`
- `include_emails`
- `include_phones`

Notes:
- Seniority should use actor enum values (`owner`, `cxo`, `vp`, `director`, `manager`, `senior`, `entry`, `training`, `unpaid`).
- The runner auto-normalizes common Apollo-style values (`founder`, `co-founder`) into `owner`.

Detailed examples are in:
- `references/actor-input-guide.md`
- `references/sample_input.json`

## Output format

The runner returns JSON with:
- `ok`
- `actorId`
- `fetchedAt`
- `leadsCount`
- `inputUsed`
- `rows[]` (lead objects from actor output)

This structure is ready for:
- n8n HTTP/Code nodes
- Google Sheets append flows
- CRM ingest pipelines
- lead scoring/enrichment post-processing

## Repository structure

- `SKILL.md` - OpenClaw invocation instructions and step-by-step flow
- `scripts/apollo_like_leads_actor.py` - actor runner CLI
- `references/actor-input-guide.md` - payload field guide
- `references/troubleshooting.md` - operational fixes
- `references/sample_input.json` - ready-to-run input
- `agents/openai.yaml` - skill UI metadata

## Security and credential handling

- Never hardcode Apify tokens in source code.
- Use `APIFY_TOKEN` via environment variables.
- Keep test runs small first (`max_results` 50-200).
- Use scoped tokens for automation environments.

## SEO keywords

apollo alternative, apollo like scraper, b2b leads scraper, apify b2b actor, sales prospecting automation, linkedin leads extractor, verified email leads, openclaw skill, lead generation workflow, b2b contact enrichment
