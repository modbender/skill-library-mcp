---
name: dievio-lead-search-api
description: Run Dievio lead search and LinkedIn lookup workflows through the public API with correct authentication, filters, pagination, and credit-aware handling. Use this skill when users need to find B2B leads, enrich LinkedIn URLs with emails/phones, apply Dievio filter fields, or iterate across paginated API results safely.
compatibility: Requires network access and valid Dievio API key
metadata:
  author: hundevmode
  version: "1.0"
  clawdbot:
    homepage: "https://dievio.com"
    source: "https://github.com/hundevmode/dievio-lead-search-openclaw-skill"
    requires:
      env:
        - DIEVIO_API_KEY
---

# Dievio Lead Search Api

## Overview

Use this skill for end-to-end Dievio API execution: authenticate requests, submit lead searches, enrich LinkedIn profiles, and paginate results.
Prefer the bundled script for deterministic request formatting and response handling.

## Core Endpoints

- Public lead search: `POST https://dievio.com/api/public/search`
- LinkedIn lookup: `POST https://dievio.com/api/linkedin/lookup`

Authentication headers (use one):
- `Authorization: Bearer YOUR_API_KEY`
- `X-API-Key: YOUR_API_KEY`

## Workflow

1. Validate credentials:
- Require `DIEVIO_API_KEY` for API-key flows.
- Never print raw secrets.

2. Build request body:
- Search endpoint uses pagination keys (`_page`, `_per_page`, `max_results`) plus filters.
- LinkedIn lookup requires `linkedinUrls` and optional output flags.

3. Execute request and parse response:
- Validate `success`, `count`, `has_more`, `next_page`, data arrays.
- Respect credit behavior: low credits can return fewer rows than requested.

4. Handle errors:
- `401`: missing/invalid credentials
- `402`: insufficient credits
- `502`: upstream lead service issue
- `500`: server error

## Commands

Show help:

```bash
python3 scripts/dievio_api.py --help
```

Search with JSON body:

```bash
export DIEVIO_API_KEY="your_api_key"
python3 scripts/dievio_api.py search \
  --body-file ./search_body.json \
  --auto-paginate
```

By default the CLI prints a safe summary.
Use `--raw-output` only when you explicitly need full rows (which may contain emails/phones).

LinkedIn lookup from URLs:

```bash
python3 scripts/dievio_api.py linkedin-lookup \
  --linkedin-url "https://www.linkedin.com/in/example-1" \
  --linkedin-url "https://www.linkedin.com/in/example-2" \
  --include-work-emails \
  --include-personal-emails \
  --only-with-emails
```

## Decision Rules

- Use `search` when query is filter-based lead discovery.
- Use `linkedin-lookup` when input is explicit LinkedIn profile URLs.
- For large pulls, enable pagination and stop on `has_more=false`.
- Keep outputs structured and include paging fields for traceability.
- If user asks for exact filter values, read [references/filters-cheatsheet.md](references/filters-cheatsheet.md).

## References

- API contracts: [references/api-reference.md](references/api-reference.md)
- Filter fields and allowed values: [references/filters-cheatsheet.md](references/filters-cheatsheet.md)
- Pagination behavior: [references/pagination.md](references/pagination.md)
- Error handling guidance: [references/errors.md](references/errors.md)
