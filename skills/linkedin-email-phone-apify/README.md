# LinkedIn Email and Phone Finder Skill for OpenClaw (Apify)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Apify Phone Actor](https://img.shields.io/badge/Phone%20Actor-X95BXRaFOqZ7rzjxM-ff6b00)](https://console.apify.com/actors/X95BXRaFOqZ7rzjxM)
[![Apify Email Actor](https://img.shields.io/badge/Email%20Actor-q3wko0Sbx6ZAAB2xf-ff6b00)](https://console.apify.com/actors/q3wko0Sbx6ZAAB2xf)

This repository contains a production-ready OpenClaw skill for **LinkedIn contact enrichment** using two Apify actors in one pipeline:
- Phone enrichment actor: [X95BXRaFOqZ7rzjxM](https://console.apify.com/actors/X95BXRaFOqZ7rzjxM)
- Email enrichment actor: [q3wko0Sbx6ZAAB2xf](https://console.apify.com/actors/q3wko0Sbx6ZAAB2xf)

It is built for teams that need one workflow to enrich LinkedIn URLs with both **emails and mobile phones**, then return clean merged rows for outbound operations.

## Why this skill

Most lead-gen stacks split email and phone scraping into separate tools. That creates duplicate mapping logic and inconsistent outputs. This skill gives you one run command, optional branch control, and merged contact data keyed by normalized LinkedIn URL.

Use cases:
- LinkedIn lead scraping for agencies and SDR teams
- B2B prospecting list enrichment
- CRM-ready contact data preparation
- n8n automation and Google Sheets pipelines

## Stack

- OpenClaw skill framework
- Apify actors for LinkedIn data lookup
- Python 3.10+ runner (no external dependencies)
- Secure token auth via `APIFY_TOKEN`

## Quick start

### 1) Set token

```bash
export APIFY_TOKEN='apify_api_xxx'
```

### 2) Run combined pipeline

```bash
python3 scripts/linkedin_email_phone_pipeline.py run \
  --input-file references/sample_input.json
```

### 3) Run with inline JSON

```bash
python3 scripts/linkedin_email_phone_pipeline.py run \
  --input-json '{
    "linkedinUrls": [
      "https://www.linkedin.com/in/williamhgates",
      "https://www.linkedin.com/in/jeffweiner08"
    ],
    "includeEmails": true,
    "includePhones": true,
    "includeWorkEmails": true,
    "includePersonalEmails": true,
    "onlyWithEmails": true,
    "onlyWithPhones": true
  }'
```

## Branch logic

- `includeEmails=true` runs the email actor
- `includePhones=true` runs the phone actor
- Both can run together
- At least one branch must stay enabled

Email branch options:
- `includeWorkEmails`
- `includePersonalEmails`
- `onlyWithEmails`

Phone branch option:
- `onlyWithPhones`

## Input contract

Required:
- `linkedinUrls` (array)

Optional:
- `includeEmails` (default `true`)
- `includePhones` (default `true`)
- email and phone filter flags above

Full reference:
- `references/input-contract.md`

## Output contract

The script returns JSON with:
- `actors` (hardcoded actor IDs used for run)
- `inputSummary` (branch flags and URL count)
- `counts` (`emailRows`, `phoneRows`, `mergedRows`)
- `rows[]` merged by normalized `linkedin_url`

Primary merged fields:
- `linkedin_url`
- `full_name`
- `job_title`
- `company`
- `work_email`
- `personal_emails`
- `mobile_phone`
- `has_email`
- `has_phone`

## Repository structure

- `SKILL.md` - skill invocation and procedural instructions
- `scripts/linkedin_email_phone_pipeline.py` - combined actor pipeline
- `references/input-contract.md` - request schema
- `references/sample_input.json` - ready payload
- `references/troubleshooting.md` - common failure fixes
- `agents/openai.yaml` - OpenClaw UI metadata

## Security

- Do not hardcode API tokens in scripts or workflow exports.
- Use `APIFY_TOKEN` via env var or `--apify-token`.
- Start with a small URL batch before large runs.

## SEO keywords

linkedin email finder, linkedin phone finder, linkedin scraper api, apify linkedin actor, b2b lead enrichment, contact enrichment workflow, openclaw skill, lead generation automation, linkedin urls to emails, linkedin urls to phone numbers
