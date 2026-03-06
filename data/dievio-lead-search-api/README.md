# Dievio Lead Search API Skill for OpenClaw

Automate B2B lead discovery and LinkedIn profile enrichment with the Dievio API, including filter-based search, pagination loops, and credit-aware result handling.

[![Dievio](https://img.shields.io/badge/Dievio-Lead%20API-0ea5e9)](https://dievio.com)
[![Docs](https://img.shields.io/badge/Docs-dievio.com%2Fapi--reference-22c55e)](https://docs.dievio.com/api-reference/overview)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-f59e0b)](https://docs.openclaw.ai/tools/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

## Quick Links

- Website: [dievio.com](https://dievio.com)
- API Overview: [Overview](https://docs.dievio.com/api-reference/overview)
- Authentication: [Authentication](https://docs.dievio.com/api-reference/authentication)
- Lead Search: [Search](https://docs.dievio.com/api-reference/search)
- LinkedIn Lookup: [LinkedIn Lookup](https://docs.dievio.com/api-reference/linkedin-lookup)
- Filters: [Filters](https://docs.dievio.com/api-reference/filters)
- Pagination: [Pagination](https://docs.dievio.com/api-reference/pagination)

## Table of Contents

- [What This Skill Does](#what-this-skill-does)
- [Who This Skill Is For](#who-this-skill-is-for)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Install as a Skill (skills.sh)](#install-as-a-skill-skillssh)
- [Install from ClawHub](#install-from-clawhub)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Release Process](#release-process)
- [SEO Keywords](#seo-keywords)
- [License](#license)

## What This Skill Does

`dievio-lead-search-api` is an OpenClaw-compatible skill for:

- Running `POST /api/public/search` with structured filters
- Running `POST /api/linkedin/lookup` for profile enrichment
- Applying pagination (`_page`, `_per_page`, `max_results`)
- Returning consistent result objects for downstream automations
- Handling common Dievio API failures and credit constraints

## Who This Skill Is For

- Growth teams and SDR workflows
- B2B lead generation automations
- Agencies enriching prospect lists from LinkedIn URLs
- Builders integrating Dievio into AI or backend pipelines

## Features

- Full OpenClaw skill (`SKILL.md`, `agents/openai.yaml`, references, script)
- Python CLI with:
  - `search`
  - `linkedin-lookup`
  - optional auto-pagination
- API key auth via `Authorization: Bearer` or `X-API-Key`
- Credit-aware behavior and clear error pass-through

## Project Structure

```text
dievio-lead-search-api/
├── SKILL.md
├── README.md
├── LICENSE
├── .gitignore
├── agents/
│   └── openai.yaml
├── references/
│   ├── api-reference.md
│   ├── filters-cheatsheet.md
│   ├── pagination.md
│   └── errors.md
└── scripts/
    └── dievio_api.py
```

## Requirements

- Python 3.9+
- `DIEVIO_API_KEY` (required)
- Network access to `https://dievio.com`

## Installation

### 1) Clone repository

```bash
git clone https://github.com/hundevmode/dievio-lead-search-openclaw-skill.git
cd dievio-lead-search-openclaw-skill
```

### 2) Set API key

```bash
export DIEVIO_API_KEY="your_api_key"
```

### 3) Verify CLI

```bash
python3 scripts/dievio_api.py --help
```

## Usage

### Search (filters JSON file)

```bash
python3 scripts/dievio_api.py search \
  --body-file ./search_body.json \
  --auto-paginate
```

Default output is summary-only (safe for logs).  
If you need full row payloads, pass `--raw-output`.

### LinkedIn lookup (URL list)

```bash
python3 scripts/dievio_api.py linkedin-lookup \
  --linkedin-url "https://www.linkedin.com/in/example-1" \
  --linkedin-url "https://www.linkedin.com/in/example-2" \
  --include-work-emails \
  --include-personal-emails \
  --only-with-emails
```

### Use `X-API-Key` header mode

```bash
python3 scripts/dievio_api.py search \
  --auth-mode x-api-key \
  --body-file ./search_body.json
```

## Install as a Skill (skills.sh)

```bash
npx skills add hundevmode/dievio-lead-search-openclaw-skill --skill dievio-lead-search-api
```

Preview available skills in repo:

```bash
npx skills add https://github.com/hundevmode/dievio-lead-search-openclaw-skill --list
```

## Install from ClawHub

```bash
clawhub install dievio-lead-search-api
```

Search:

```bash
clawhub search dievio-lead-search-api
```

## API Endpoints

- `POST https://dievio.com/api/public/search`
- `POST https://dievio.com/api/linkedin/lookup`

Auth headers:

- `Authorization: Bearer <DIEVIO_API_KEY>`
- `X-API-Key: <DIEVIO_API_KEY>`

## Error Handling

This skill documents and passes through:

- `401` missing/invalid API key
- `402` insufficient API credits
- `502` upstream service failure
- `500` server error

## Release Process

1. Update skill files and script.
2. Commit and push to GitHub.
3. Publish new ClawHub version:

```bash
clawhub publish . \
  --slug dievio-lead-search-api \
  --name "Dievio Lead Search API" \
  --version <next-semver> \
  --tags latest
```

4. Verify:

```bash
clawhub inspect dievio-lead-search-api
npx skills add hundevmode/dievio-lead-search-openclaw-skill --skill dievio-lead-search-api
```

## SEO Keywords

Dievio API, Dievio lead search API, LinkedIn email lookup API, B2B lead enrichment, lead generation automation, OpenClaw skill, API pagination for leads, sales prospecting API.

## License

MIT. See [LICENSE](./LICENSE).
