---
name: linkedin-email-phone-apify
description: Use this skill when the user needs LinkedIn contact enrichment by URLs with both phone and email lookup via Apify actors (phones: X95BXRaFOqZ7rzjxM, emails: q3wko0Sbx6ZAAB2xf), including optional branches and merged output.
required_env_vars:
  - APIFY_TOKEN
required-env-vars:
  - APIFY_TOKEN
primary_credential: APIFY_TOKEN
primary-credential: APIFY_TOKEN
metadata:
  short-description: Enrich LinkedIn URLs with emails and phones
  openclaw:
    requires:
      env:
        - APIFY_TOKEN
    primaryCredential: APIFY_TOKEN
---

# LinkedIn Email + Phone Enrichment (Apify)

## Overview

This skill runs two Apify actors in one pipeline and merges results by LinkedIn profile URL:
- Phone actor: `X95BXRaFOqZ7rzjxM`
- Email actor: `q3wko0Sbx6ZAAB2xf`

Use this when the user wants one command to enrich a LinkedIn URL list with:
- mobile phones
- work emails
- personal emails
- unified rows for n8n/Sheets/CRM

## Step-by-step workflow

1. Accept LinkedIn URLs (`linkedinUrls`) from user.
2. Validate and normalize URLs.
3. Decide branches:
- run phone actor if `includePhones=true`
- run email actor if `includeEmails=true`
4. Run selected actors on the same URL list.
5. Merge results by normalized LinkedIn URL.
6. Return summary + merged rows.

## Authentication

```bash
export APIFY_TOKEN='apify_api_xxx'
```

or

```bash
python3 scripts/linkedin_email_phone_pipeline.py run \
  --apify-token 'apify_api_xxx' \
  --input-file references/sample_input.json
```

## Quick start

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/linkedin_email_phone_pipeline.py run \
  --input-file references/sample_input.json
```

## Toggle branches

Emails only:

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/linkedin_email_phone_pipeline.py run \
  --input-json '{
    "linkedinUrls": ["https://www.linkedin.com/in/williamhgates"],
    "includeEmails": true,
    "includePhones": false,
    "includeWorkEmails": true,
    "includePersonalEmails": true,
    "onlyWithEmails": true
  }'
```

Phones only:

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/linkedin_email_phone_pipeline.py run \
  --input-json '{
    "linkedinUrls": ["https://www.linkedin.com/in/williamhgates"],
    "includeEmails": false,
    "includePhones": true,
    "onlyWithPhones": true
  }'
```

## Notes

- Actor IDs are hardcoded to your provided IDs.
- `linkedinUrls` is required.
- At least one branch must be enabled (`includeEmails` or `includePhones`).
- Output rows contain available email/phone fields in one record.

## References

- `references/input-contract.md`
- `references/troubleshooting.md`
