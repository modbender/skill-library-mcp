# Twitter/X Scraper Skill for OpenClaw (Apify Followers + Optional Email Enrichment)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Repo stars](https://img.shields.io/github/stars/hundevmode/twitter-x-apify-actors-openclaw-skill?style=social)](https://github.com/hundevmode/twitter-x-apify-actors-openclaw-skill/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/hundevmode/twitter-x-apify-actors-openclaw-skill)](https://github.com/hundevmode/twitter-x-apify-actors-openclaw-skill/commits/main)

A production-focused OpenClaw **Twitter/X scraper skill** to run lead collection with Apify actors: collect followers/following and optionally enrich with emails.

This skill is built for teams that need repeatable **Twitter scraper automation** and **Twitter lead generation** without manually wiring actor payloads each time.

## Table of Contents

- [Actor Links](#actor-links)
- [What This Skill Does](#what-this-skill-does)
- [Who This Skill Is For](#who-this-skill-is-for)
- [Repository Structure](#repository-structure)
- [Why This Beats Manual Scraping](#why-this-beats-manual-scraping)
- [Twitter Scraper API Workflow](#twitter-scraper-api-workflow)
- [Use-Case Snippets](#use-case-snippets)
- [Requirements](#requirements)
- [Authentication (Apify)](#authentication-apify)
- [Quick Start](#quick-start)
- [Output Format](#output-format)
- [Install as OpenClaw Skill](#install-as-openclaw-skill)
- [ClawHub Publishing Notes](#clawhub-publishing-notes)
- [SEO Keywords](#seo-keywords)
- [License](#license)

## Actor Links

- Followers / following actor: [https://console.apify.com/actors/bIYXeMcKISYGnHhBG](https://console.apify.com/actors/bIYXeMcKISYGnHhBG)
- Email enrichment actor: [https://console.apify.com/actors/mSaHt2tt3Z7Fcwf0o](https://console.apify.com/actors/mSaHt2tt3Z7Fcwf0o)

## What This Skill Does

- Extracts username from `x.com`, `twitter.com`, or `@handle`
- Builds actor-ready payloads for follower/following collection
- Runs follower actor and normalizes output rows
- Optionally runs email actor and merges email/name data
- Returns JSON with metrics and outreach-ready rows

## Who This Skill Is For

- Growth teams building X audience lead lists
- Founders running outbound campaigns from Twitter/X
- Agencies that need repeatable social graph collection
- Operators who want Apify actor automation without custom glue code

## Repository Structure

| Path | Purpose |
|---|---|
| `SKILL.md` | Trigger rules, workflow, execution guidance |
| `agents/openai.yaml` | OpenClaw UI metadata |
| `scripts/apify_twitter_actors.py` | CLI runner for followers + optional email enrichment |
| `references/actor-contracts.md` | Actor input/output contracts |
| `references/troubleshooting.md` | Common failures and fixes |

## Why This Beats Manual Scraping

Manual Twitter/X prospecting usually fails at scale because extraction, filtering, enrichment, and formatting happen in separate steps. That creates inconsistency and slows outbound teams.

This skill improves the process by keeping the pipeline deterministic:

- one input target format (`x.com`, `twitter.com`, or `@handle`)
- one runner for followers/following/both
- one optional enrichment branch (email actor)
- one normalized output contract for downstream systems

For growth teams and agencies, this means faster campaign setup, fewer formatting errors, and better reuse across client niches.

## Twitter Scraper API Workflow

Teams often look for a Twitter scraper API workflow that is simple to run and easy to maintain. This skill follows a clear execution pattern: parse profile target, run followers actor, optionally run email enrichment, and return normalized output. The flow is stable enough for repeated campaign usage while staying flexible through input flags like `collect-type`, `limit`, and `include-emails`.

From an operations perspective, the value is not only in collection speed. The bigger win is predictable structure. Because the output schema stays consistent across runs, it is straightforward to pass results into n8n, Google Sheets, CSV exports, or CRM staging steps without rewriting transformation logic every time.

## Use-Case Snippets

### 1) Founder outbound list from a competitor audience
Collect followers of a target founder account, enrich with emails only when needed, and push final rows to your CRM staging sheet.

### 2) Agency lead sprint for Twitter/X niches
Run multiple profile targets with the same script contract, standardize output schema, and hand off to SDRs without manual cleanup.

### 3) Low-cost discovery mode before enrichment
Run follower-only collection first (`--include-emails` off), evaluate quality, then rerun top segments with enrichment enabled.

## Requirements

- Python 3.10+
- `requests`
- Apify API token

Install dependencies:

```bash
pip install -r requirements.txt
```

## Authentication (Apify)

Two supported ways:

### Option A: Environment variable (recommended)

```bash
export APIFY_TOKEN='apify_api_xxx'
```

### Option B: CLI argument

```bash
--apify-token 'apify_api_xxx'
```

If both are provided, `--apify-token` wins.

## Quick Start

### 1) Parse username

```bash
python3 scripts/apify_twitter_actors.py parse-username --target 'https://x.com/elonmusk'
```

### 2) Collect followers/following only

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/apify_twitter_actors.py run-followers \
  --target 'https://x.com/elonmusk' \
  --collect-type followers \
  --limit 1000
```

### 3) Full pipeline with optional email enrichment

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/apify_twitter_actors.py run-pipeline \
  --target 'https://x.com/elonmusk' \
  --collect-type followers \
  --limit 1000 \
  --include-emails
```

## Commands

- `parse-username`
- `run-followers`
- `run-pipeline`

Supported collect types:

- `followers`
- `following`
- `both`

## Output Format

`run-pipeline` returns:

- `targetUsername`
- `collectType`
- `includeEmails`
- `totalCollected`
- `emailsFound`
- `rows[]` with `username`, `name`, `email`, `sourceType`, `collectedAt`

This is ready for n8n, CSV export, Google Sheets, or CRM staging.

## Install as OpenClaw Skill

If your OpenClaw/skills runtime supports GitHub install:

```bash
npx skills add hundevmode/twitter-x-apify-actors-openclaw-skill --skill twitter-x-apify-actors
```

List skills in repo:

```bash
npx skills add hundevmode/twitter-x-apify-actors-openclaw-skill --list
```

## ClawHub Publishing Notes

Before publishing to ClawHub:

1. Confirm `SKILL.md` frontmatter is correct
2. Ensure `agents/openai.yaml` metadata is present
3. Run a smoke test with valid `APIFY_TOKEN`
4. Keep actor IDs documented and configurable

## SEO Keywords

Twitter scraper, Twitter/X scraper, X followers scraper, social media scraper, Apify actors, OpenClaw skill, email enrichment, Twitter lead generation, outbound automation, growth automation.

## License

MIT (free for commercial and private use).
