---
name: google-search-console
description: Use this skill when working with this repository's `gsc` CLI, including Google Cloud OAuth client setup, CLI authentication, troubleshooting auth/config issues, and running all supported commands (site, sitemap, url inspection, analytics, doctor, config).
---

# Google Search Console CLI Skill

Use this skill to operate and troubleshoot the `gsc` CLI in this repository.

## When To Use

Use this skill when the task involves any of:
- setting up OAuth credentials for Google Search Console
- authenticating this CLI
- listing properties, managing sitemaps, URL inspection, or Search Analytics queries
- diagnosing auth/config/API connectivity issues

## Prerequisites

- Python environment with this project installed (`gsc` command available)
- A Google account with access to at least one Search Console property
- Search Console API enabled for the Google Cloud project used by OAuth

## Install This CLI

Recommended (`pipx`, global `gsc` command):

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install google-search-console-cli
gsc --version
```

From source (development):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
gsc --help
```

From source (`pipx`, editable):

```bash
pipx install -e /absolute/path/to/google-search-console-cli
gsc --help
```

## OAuth Client Setup In Google Cloud (Desktop App)

As of February 26, 2026, create OAuth client credentials in Google Cloud Console using these steps:

1. Open Google Cloud Console and select/create a project.
2. Enable the Search Console API for that project.
3. Configure OAuth consent screen:
   - choose `External` for personal/testing usage (or `Internal` for Workspace org-only)
   - fill required app fields (app name, support email, developer contact)
   - add your Google account as a test user if app is in testing mode
4. Go to `APIs & Services` -> `Credentials`.
5. Click `Create credentials` -> `OAuth client ID`.
6. Choose application type `Desktop app`.
7. Create and download the OAuth client JSON (`client_secret_*.json`).

Notes:
- UI labels can shift, but you must end with a Desktop OAuth client JSON file.
- Keep the downloaded JSON private.

## Authenticate This CLI

Preferred login flow:

```bash
gsc auth login --client-secret /absolute/path/to/client_secret.json
```

Useful auth options:
- `--readonly`: request readonly scope only (`webmasters.readonly`)
- `--no-launch-browser`: print the auth URL without auto-opening a browser

Verify credentials:

```bash
gsc auth whoami
gsc doctor
```

Default storage paths:
- credentials: `~/.config/gsc-cli/credentials.json`
- app config: `~/.config/gsc-cli/config.json`

Env overrides:
- `GSC_CREDENTIALS_FILE`
- `GSC_APP_CONFIG_FILE`
- `GSC_CONFIG_DIR`

## Optional: Set Default Property

```bash
gsc config set default-site sc-domain:example.com
gsc config get default-site
```

When set, commands that accept `--site` can omit it.

## Command Reference

Top-level:
- `gsc --version`
- `gsc --help`
- `gsc doctor`

### `auth`

- `gsc auth login --client-secret FILE [--readonly] [--no-launch-browser]`
- `gsc auth whoami [--output table|json]`

### `config`

- `gsc config set default-site SITE_URL`
- `gsc config get default-site`

### `site`

- `gsc site list [--output table|json|csv] [--csv-path FILE]`
- `gsc site get [--site SITE] [--output table|json|csv] [--csv-path FILE]`
- `gsc site add [--site SITE]`

`SITE` example: `sc-domain:example.com`.

### `sitemap`

- `gsc sitemap list [--site SITE] [--sitemap-index TEXT] [--output table|json|csv] [--csv-path FILE]`
- `gsc sitemap get [--site SITE] --feedpath TEXT [--output table|json|csv] [--csv-path FILE]`
- `gsc sitemap submit [--site SITE] --feedpath TEXT`
- `gsc sitemap delete [--site SITE] --feedpath TEXT`

`--feedpath` alias: `--path`.

### `url`

- `gsc url inspect [--site SITE] --url URL [--language-code CODE] [--output table|json|csv] [--csv-path FILE]`

Defaults:
- `--language-code en-US`

### `analytics`

- `gsc analytics query --start-date YYYY-MM-DD --end-date YYYY-MM-DD [options]`

Options:
- `--site SITE`
- `--dimension country|date|device|hour|page|query|searchAppearance` (repeatable)
- `--type discover|googleNews|image|news|video|web`
- `--aggregation-type auto|byNewsShowcasePanel|byPage|byProperty`
- `--row-limit 1..25000`
- `--start-row >=0`
- `--data-state all|final|hourly_all`
- `--filter dimension:operator:expression` (repeatable)
- `--output table|json|csv`
- `--csv-path FILE`

Supported filter dimensions:
- `country`, `device`, `page`, `query`, `searchAppearance`

Supported filter operators:
- `contains`, `equals`, `notContains`, `notEquals`, `includingRegex`, `excludingRegex`

Constraint:
- `--aggregation-type byProperty` cannot be combined with `page` dimension or `page` filter.

## Quick Examples

```bash
# List properties
gsc site list

# Get one property
gsc site get --site sc-domain:example.com

# List sitemaps
gsc sitemap list --site sc-domain:example.com

# Inspect one URL
gsc url inspect --site sc-domain:example.com --url https://example.com/page --output json

# Analytics query
gsc analytics query \
  --site sc-domain:example.com \
  --start-date 2026-01-01 \
  --end-date 2026-01-31 \
  --dimension date \
  --dimension query \
  --filter query:contains:brand
```

## Troubleshooting

- `Auth error: Stored credentials do not include required scope ...`
  - Re-run login with needed scope. For write commands, run login without `--readonly`.

- `No local OAuth credentials found...`
  - Run: `gsc auth login --client-secret <path>`

- `No site specified. Pass --site or set one...`
  - pass `--site` or set default via `gsc config set default-site ...`

- API failures / uncertain setup state
  - run `gsc doctor` first, then address failing checks.
