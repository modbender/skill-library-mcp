---
name: bing-webmaster-cli
description: Use this skill when working with this repository's `bwm` CLI, including Bing Webmaster API key setup, CLI authentication, site listing, traffic stats, URL index checks with explanation, URL submission, and troubleshooting.
---

# Bing Webmaster CLI Skill

Use this skill to operate and troubleshoot the `bwm` CLI in this repository.

## When To Use

Use this skill when the task involves any of:
- creating or rotating a Bing Webmaster API key
- authenticating this CLI with env var or local stored key
- listing sites in Bing Webmaster
- fetching site/URL traffic stats
- checking whether a URL is indexed and why not
- submitting URLs for indexing

## Prerequisites

- Python environment with this project installed (`bwm` command available)
- Bing Webmaster Tools account with access to at least one site
- Bing Webmaster API key

## Install This CLI

Recommended (`pipx`, global `bwm` command):

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install bing-webmaster-cli
bwm --version
```

From source (development):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
bwm --help
```

From source (`pipx`, editable):

```bash
pipx install -e /absolute/path/to/bing_webmaster_cli
bwm --help
```

## Create API Key (Bing Webmaster)

As of February 26, 2026, create a Bing Webmaster API key using these steps:

1. Open Bing Webmaster Tools: `https://www.bing.com/webmasters/`
2. Sign in and open account/API access settings.
3. Generate a new API key.
4. Copy and securely store the key.

Reference:
- `https://learn.microsoft.com/en-us/bingwebmaster/getting-access`

## Authenticate This CLI

### Environment variable (recommended for CI/ephemeral usage)

```bash
export BING_WEBMASTER_API_KEY="<your_api_key>"
bwm auth whoami
```

### Local stored key

```bash
bwm auth login --api-key "<your_api_key>"
bwm auth whoami
```

Interactive prompt:

```bash
bwm auth login
```

Clear local key:

```bash
bwm auth clear
```

## Optional: Set Default Site

```bash
bwm config set default-site https://example.com/
bwm config get default-site
```

When set, commands that accept `--site` can omit it.

## Command Reference

Top-level:
- `bwm --version`
- `bwm --help`

### `auth`

- `bwm auth login [--api-key TEXT]`
- `bwm auth whoami [--output table|json]`
- `bwm auth clear`

### `config`

- `bwm config set default-site SITE_URL`
- `bwm config get default-site`

### `site`

- `bwm site list [--output table|json|csv] [--csv-path FILE]`

### `stats`

- `bwm stats site [--site SITE] [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD] [--output table|json|csv] [--csv-path FILE]`
- `bwm stats url [--site SITE] --url URL [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD] [--output table|json|csv] [--csv-path FILE]`

### `url`

- `bwm url check-index [--site SITE] --url URL [--output table|json] [--explain]`
- `bwm url submit [--site SITE] [--url URL]... [--file FILE] [--output table|json]`

## Quick Examples

```bash
# List sites
bwm site list --output json

# Site stats for a date window
bwm stats site \
  --site https://example.com/ \
  --start-date 2026-02-01 \
  --end-date 2026-02-26

# URL stats
bwm stats url \
  --site https://example.com/ \
  --url https://example.com/page \
  --output json

# URL index check with richer explanation
bwm url check-index \
  --site https://example.com/ \
  --url https://example.com/page \
  --output json \
  --explain

# Submit one URL
bwm url submit --site https://example.com/ --url https://example.com/new-page

# Submit batch from file
bwm url submit --site https://example.com/ --file ./urls.txt
```

## Troubleshooting

- `Auth error: No API key found...`
  - set `BING_WEBMASTER_API_KEY` or run `bwm auth login`.

- `No site specified. Pass --site or set one...`
  - pass `--site` or set default site with `bwm config set default-site ...`.

- URL appears blocked in Bing UI while simple API fields are sparse
  - run `bwm url check-index --explain ...` to get best-effort diagnostics from API signals.

## Config Paths And Overrides

Defaults:
- credentials: `~/.config/bing-webmaster-cli/credentials.json`
- app config: `~/.config/bing-webmaster-cli/config.json`

Env overrides:
- `BING_WEBMASTER_API_KEY`
- `BWM_CONFIG_DIR`
- `BWM_CREDENTIALS_FILE`
- `BWM_APP_CONFIG_FILE`
- `BWM_API_BASE_URL`
