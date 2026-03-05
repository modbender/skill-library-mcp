---
name: twitter-x-apify-actors
description: Use this skill when the user needs Twitter/X audience collection through Apify actors (followers/following/both) with optional email enrichment, username extraction from links, normalized row output, or webhook-ready payload building.
required_env_vars:
  - APIFY_TOKEN
required-env-vars:
  - APIFY_TOKEN
primary_credential: APIFY_TOKEN
primary-credential: APIFY_TOKEN
metadata:
  short-description: Run Apify Twitter/X follower and email actors
  openclaw:
    requires:
      env:
        - APIFY_TOKEN
    primaryCredential: APIFY_TOKEN
---

# Twitter/X Apify Actors

## Overview

This skill runs a reliable actor-based pipeline for Twitter/X lead collection using Apify. It extracts a username from an X/Twitter link, runs a follower/following actor, optionally runs an email actor, and returns normalized rows for outreach workflows.

Use this skill when a user asks to:
- collect followers/following from X via Apify actors
- enrich collected usernames with emails
- convert profile links to actor-ready usernames
- build JSON/webhook payloads for n8n or API endpoints

Default actor IDs in this skill:
- Followers actor: `bIYXeMcKISYGnHhBG`
- Email actor: `mSaHt2tt3Z7Fcwf0o`

## Quick Workflow

1. Parse input target (`https://x.com/...`, `https://twitter.com/...`, or `@username`).
2. Build follower actor payload using `collectType` and `limit`.
3. Run follower actor and normalize usernames.
4. If enrichment is enabled, run email actor and merge results.
5. Return final rows + summary metrics.

## Execution Rules

- Prefer script execution for reliability: use `scripts/apify_twitter_actors.py`.
- Keep actor IDs configurable, but default to the IDs above.
- Always validate `collectType` (`followers`, `following`, `both`) and positive limit.
- If email enrichment is disabled, skip email actor entirely.
- Never hardcode the Apify token in outputs. Use env `APIFY_TOKEN` or explicit CLI argument.

## Authentication (Apify token)

Users can provide the Apify API token in two supported ways.

### Option A: Environment variable (recommended)

```bash
export APIFY_TOKEN='apify_api_xxx'
python3 scripts/apify_twitter_actors.py run-pipeline \
  --target 'https://x.com/elonmusk' \
  --collect-type followers \
  --limit 1000 \
  --include-emails
```

### Option B: CLI argument

```bash
python3 scripts/apify_twitter_actors.py run-pipeline \
  --apify-token 'apify_api_xxx' \
  --target 'https://x.com/elonmusk' \
  --collect-type followers \
  --limit 1000 \
  --include-emails
```

If both are provided, `--apify-token` is used. If neither is provided, the script returns an explicit authentication error.

## Script Usage

Run with Python 3.10+.

```bash
python3 scripts/apify_twitter_actors.py parse-username --target 'https://x.com/elonmusk'
```

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/apify_twitter_actors.py run-followers \
  --target 'https://x.com/elonmusk' \
  --collect-type followers \
  --limit 1000
```

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/apify_twitter_actors.py run-pipeline \
  --target 'https://x.com/elonmusk' \
  --collect-type followers \
  --limit 1000 \
  --include-emails
```

Quick auth check:

```bash
APIFY_TOKEN='apify_api_xxx' \
python3 scripts/apify_twitter_actors.py run-followers \
  --target 'https://x.com/elonmusk' \
  --collect-type followers \
  --limit 10
```

For contracts and payload details, read:
- `references/actor-contracts.md`
- `references/troubleshooting.md`

## Output Contract

The pipeline returns JSON with:
- `targetUsername`
- `collectType`
- `totalCollected`
- `emailsFound`
- `rows[]` with `username`, `name`, `email`, `sourceType`, `collectedAt`

Use this output directly in n8n Code/HTTP nodes or export to CSV/Google Sheets.
