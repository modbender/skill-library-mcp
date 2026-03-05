---
name: datamerge
description: Use when enriching B2B company or contact data — looking up companies by domain, exploring company hierarchies, finding contacts at companies, discovering lookalike companies, or managing lists of leads.
license: MIT
metadata:
    author: DataMerge
    version: "1.3.0"
    homepage: https://www.datamerge.ai
    docs: https://www.datamerge.ai/docs/llms.txt
    openapi: https://api.datamerge.ai/schema
    mcp: https://mcp.datamerge.ai
inputs:
    - name: DATAMERGE_API_KEY
      description: >
        DataMerge API key. Sign up free at https://app.datamerge.ai — no credit card required.
        New accounts receive 20 free credits immediately on email verification.
        Get your API key from the Account page after signup.
      required: true
---

# DataMerge

> **MCP server (Claude Desktop, Cursor, Windsurf):** `https://mcp.datamerge.ai` — see https://www.datamerge.ai/docs/mcp.md
> **Complete documentation (all-in-one):** https://www.datamerge.ai/docs/llms.txt
> **Quick Start guide:** https://www.datamerge.ai/docs/quickstart.md
> **OpenAPI Schema:** https://api.datamerge.ai/schema

## Getting Started — 20 Free Credits, No Credit Card

1. Sign up at https://app.datamerge.ai (email + password)
2. Verify your email
3. Copy your API key from the Account page
4. You now have **20 free credits** — company records, contacts, lookalikes

## Overview

DataMerge is a B2B data enrichment platform. Given a company domain, it returns the actual **legal entity** registered to that domain — including official legal name, registered address, jurisdiction, and position in the **corporate hierarchy**.

For multinationals, DataMerge can return any entity in the corporate tree: a country-specific subsidiary, a regional parent, or the global ultimate holding company. Full corporate hierarchy traversal is available via a dedicated endpoint.

DataMerge also finds and enriches contacts at companies (emails, mobile numbers, LinkedIn). Covers 375M+ companies globally.

**API base URL:** `https://api.datamerge.ai`

**OpenAPI spec:** `https://api.datamerge.ai/schema`

**Interactive docs:** `https://api.datamerge.ai/docs`

## Authentication

All requests require an API key:

```
Authorization: Token YOUR_API_KEY
```

Store the key as an environment variable: `DATAMERGE_API_KEY`

Incorrect or missing API key returns `401 Unauthorized`.

## Credit Costs

- **1 credit** = 1 company record or 1 contact with validated email
- **4 credits** = 1 mobile phone number
- **0 credits** = failed lookups (you only pay for successful results)

## Core Pattern — Async Processing

All enrichment endpoints are **asynchronous**. The pattern is always:

1. POST to start the job → receive a `job_id`
2. GET the status endpoint with that `job_id` → poll until `status` is `"completed"` or `"failed"`
3. Status response includes `record_ids` — call `GET /v1/company/get?record_id=<id>` or `GET /v1/contact/get?record_id=<id>` for each

**Status values:** `queued` → `processing` → `completed` or `failed`

## Enrich a Company

```bash
# Step 1: Start enrichment (single domain)
curl -X POST https://api.datamerge.ai/v1/company/enrich \
  -H "Authorization: Token $DATAMERGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"domain": "stripe.com"}'

# Response: {"job_id": "abc123...", "status": "queued", ...}

# Step 2: Poll for status
curl https://api.datamerge.ai/v1/company/enrich/abc123.../status \
  -H "Authorization: Token $DATAMERGE_API_KEY"

# Response includes: {"status": "completed", "record_ids": ["uuid1", ...], ...}

# Step 3: Fetch the full record (free — no credits)
curl "https://api.datamerge.ai/v1/company/get?record_id=uuid1" \
  -H "Authorization: Token $DATAMERGE_API_KEY"
```

**Batch enrichment** — pass `domains` array instead:
```json
{"domains": ["stripe.com", "shopify.com", "github.com"]}
```

**Enrich response fields include:** `legal_name`, `display_name`, `address1`, `city`, `region`, `country`, `country_code`, `industry_sic_name`, `industry_nace_name`, `group_employees`, `group_revenue`, `social_linkedin`, `social_facebook`, `social_x`, `datamerge_id`, `record_id`, `logo`, `year_started`, `parent_id`, `global_ultimate_id`, `global_ultimate_name`, `hierarchy_level`

## Country & Hierarchy Controls

Two parameters on the enrich endpoint control which legal entity is returned:

- **`country_code`** (array): Return the subsidiary registered in one of these countries. E.g. `["DE"]` returns the German entity of a multinational.
- **`global_ultimate`** (boolean): If `true`, return the top-level parent company.

Example: `google.com` with no params → `Google LLC` (US). With `country_code: ["DE"]` → `Google Germany GmbH`. With `global_ultimate: true` → `Alphabet Inc.`

## Get Company by ID

```bash
# By DataMerge ID (charges 1 credit)
curl "https://api.datamerge.ai/v1/company/get?datamerge_id=DM001283124635" \
  -H "Authorization: Token $DATAMERGE_API_KEY"

# By record UUID (free — returns your stored record)
curl "https://api.datamerge.ai/v1/company/get?record_id=YOUR-UUID" \
  -H "Authorization: Token $DATAMERGE_API_KEY"
```

Provide either `datamerge_id` or `record_id`, not both.

## Company Hierarchy

```bash
curl "https://api.datamerge.ai/v1/company/hierarchy?datamerge_id=DM001283124635&include_names=true" \
  -H "Authorization: Token $DATAMERGE_API_KEY"
```

Returns all entities in the same global ultimate hierarchy. By default, names are excluded (free). Set `include_names=true` to include company names (charges 1 credit).

## Find Contacts at a Company

```bash
# Step 1: Search for contacts
curl -X POST https://api.datamerge.ai/v1/contact/search \
  -H "Authorization: Token $DATAMERGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["stripe.com"],
    "max_results_per_company": 5,
    "job_titles": {
      "include": {
        "1": ["CEO", "CTO", "Chief Technology Officer"],
        "2": ["VP Engineering", "VP of Engineering"]
      },
      "exclude": ["Intern", "Assistant"]
    },
    "location": {
      "include": [
        {"type": "country", "value": "United States"}
      ]
    },
    "enrich_fields": ["contact.emails", "contact.phones"]
  }'

# Response: {"job_id": "...", "status": "queued", ...}

# Step 2: Poll for status
curl https://api.datamerge.ai/v1/contact/search/JOB_ID/status \
  -H "Authorization: Token $DATAMERGE_API_KEY"

# Response includes: {"status": "completed", "record_ids": [...], ...}

# Step 3: Fetch each contact (free)
curl "https://api.datamerge.ai/v1/contact/get?record_id=uuid1" \
  -H "Authorization: Token $DATAMERGE_API_KEY"
```

**Key:** `max_results_per_company` is at the top level of the request body. `job_titles.include` uses priority tiers (`"1"` = primary, `"2"` = secondary). `location.include` is an array of `{type, value}` objects.

## Enrich Specific Contacts

```bash
curl -X POST https://api.datamerge.ai/v1/contact/enrich \
  -H "Authorization: Token $DATAMERGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contacts": [
      {"linkedin_url": "https://www.linkedin.com/in/johndoe"},
      {"firstname": "Jane", "lastname": "Smith", "domain": "stripe.com"}
    ],
    "enrich_fields": ["contact.emails", "contact.phones"]
  }'
```

## Find Lookalike Companies

```bash
# Step 1: Find lookalikes (async)
curl -X POST https://api.datamerge.ai/v1/company/lookalike \
  -H "Authorization: Token $DATAMERGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "companiesFilters": {
      "lookalikeDomains": ["stripe.com"],
      "primaryLocations": {
        "includeCountries": ["us", "gb"]
      },
      "companySizes": ["51-200", "201-500"]
    },
    "size": 20
  }'

# Response: {"job_id": "...", "status": "queued", "message": "..."}

# Step 2: Poll for status
curl https://api.datamerge.ai/v1/company/lookalike/JOB_ID/status \
  -H "Authorization: Token $DATAMERGE_API_KEY"

# Response includes: {"status": "completed", "record_ids": [...], ...}

# Step 3: Fetch each company (free)
curl "https://api.datamerge.ai/v1/company/get?record_id=uuid1" \
  -H "Authorization: Token $DATAMERGE_API_KEY"
```

**Key:** `companiesFilters.lookalikeDomains` takes an array of seed domains. `size` is the number of results. Filters (`primaryLocations`, `companySizes`, `revenues`, `yearFounded`) are all optional.

## Managing Lists

```bash
# Create a list
curl -X POST https://api.datamerge.ai/v1/lists \
  -H "Authorization: Token $DATAMERGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Target Accounts", "object_type": "company"}'

# Get all lists
curl https://api.datamerge.ai/v1/lists \
  -H "Authorization: Token $DATAMERGE_API_KEY"

# Get list members (by slug)
curl "https://api.datamerge.ai/v1/lists/company/target-accounts" \
  -H "Authorization: Token $DATAMERGE_API_KEY"

# Remove an item from a list
curl -X DELETE "https://api.datamerge.ai/v1/lists/company/target-accounts/RECORD_ID" \
  -H "Authorization: Token $DATAMERGE_API_KEY"

# Delete a list
curl -X DELETE "https://api.datamerge.ai/v1/lists/company/target-accounts" \
  -H "Authorization: Token $DATAMERGE_API_KEY"
```

To add enriched records to a list, include `"list": "list-slug"` in your enrich or lookalike request body.

## Check Credit Balance

```bash
curl https://api.datamerge.ai/v1/credits/balance \
  -H "Authorization: Token $DATAMERGE_API_KEY"

# Response: {"credits_balance": 5440, "balances": {"one_off": 5440, "recurring": 0, "rollover": 0, "total": 5440}}
```

## Key Behaviours to Know

- **Deduplication:** Enrich a domain already in a list with `skip_if_exists: true` — existing record returned, no credits charged.
- **Caching:** Previously enriched domains return quickly from cache.
- **`not_found` status:** Domain valid but not in database — no credits charged.
- **Record retrieval is free:** `GET /v1/company/get?record_id=<id>` and `GET /v1/contact/get?record_id=<id>` never charge credits.
- **List paths use slugs:** Lists are referenced by their `slug` (e.g. `target-accounts`), not by UUID, in URL paths.

## Resources

- [MCP Server](https://www.datamerge.ai/docs/mcp.md): Setup guide for Claude Desktop, Cursor, Windsurf — remote URL: `https://mcp.datamerge.ai`
- [MCP GitHub](https://github.com/poolside-ventures/datamerge-mcp): Source + npm package `@datamerge/mcp`
- [Complete Docs (all-in-one)](https://www.datamerge.ai/docs/llms.txt)
- [Quick Start Guide](https://www.datamerge.ai/docs/quickstart.md)
- [Enrich Company — full guide](https://www.datamerge.ai/docs/enrich-company.md)
- [Find Contacts — full guide](https://www.datamerge.ai/docs/find-contacts.md)
- [Find Lookalikes — full guide](https://www.datamerge.ai/docs/find-lookalikes.md)
- [OpenAPI Schema (YAML)](https://api.datamerge.ai/schema)
- [Interactive Docs (Redoc)](https://api.datamerge.ai/docs)
- [Swagger UI](https://api.datamerge.ai/swagger)
- [Web Application](https://app.datamerge.ai)
- [Pricing](https://www.datamerge.ai/pricing)
