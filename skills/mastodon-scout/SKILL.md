---
name: mastodon-scout
description: Read-only Mastodon skill. Outputs human-readable timeline summaries or raw JSON.
metadata: {"clawdhub":{"emoji":"🦣"},"clawdis":{"envVars":[{"name":"MASTODON_TOKEN","required":true},{"name":"MASTODON_INSTANCE","required":false,"default":"https://mastodon.social"}]}}
---

# Mastodon Scout

## Purpose

Read-only Mastodon skill. Fetches data from the Mastodon API via a bundled Python script (`scripts/mastodon_scout.py`). Returns human-readable summaries by default, or raw JSON with `--json`.

---

## Invocation Rules (MANDATORY)

```bash
python3 ./scripts/mastodon_scout.py <command> [options]
```

### Commands

| Command | What it fetches |
|---------|----------------|
| `home` | Authenticated user's home timeline |
| `user-tweets` | Authenticated user's own posts |
| `mentions` | Mentions of the authenticated user |
| `search <query>` | Posts matching the query |

### Options
```
--instance <url>   Mastodon instance base URL (default: $MASTODON_INSTANCE or https://mastodon.social)
--limit <int>      Number of items to return (default: $LIMIT or 20)
--json             Output raw JSON instead of human-readable text
```

### Environment Variables
```
MASTODON_TOKEN      Required. OAuth bearer token.
MASTODON_INSTANCE   Optional. Instance base URL (default: https://mastodon.social).
```

### Examples
```bash
python3 ./scripts/mastodon_scout.py home
python3 ./scripts/mastodon_scout.py mentions --limit 10
python3 ./scripts/mastodon_scout.py search "golang"
python3 ./scripts/mastodon_scout.py home --json
python3 ./scripts/mastodon_scout.py home --instance https://fosstodon.org
```

---

## Output Modes

### Text Mode (Default)
The script formats each post as:
```
[N] Display Name (@user@instance) · <timestamp>
<content>
↩ <replies>  🔁 <reblogs>  ⭐ <favourites>
<url>
```
The agent MAY add a brief summary after the list.

### JSON Mode (`--json`)
Returns raw Mastodon API JSON. Return it verbatim — no interpretation.

---

## Error Handling

The script prints a human-readable error to stderr and exits non-zero:

| Condition | Message |
|-----------|---------|
| Token missing | `Error: MASTODON_TOKEN is not set` |
| 401 | `Mastodon API error: 401 Unauthorized — check MASTODON_TOKEN` |
| 403 | `Mastodon API error: 403 Forbidden` |
| 422 | `Mastodon API error: 422 Unprocessable Entity` |
| 429 | `Mastodon API error: 429 Rate Limited — try again later` |

Do not retry on error. Guide the user to Authentication Setup if the token is missing or invalid.

---

## Examples That Trigger This Skill

- `mastodon-scout home`
- `show my mastodon timeline`
- `check mastodon mentions`
- `search mastodon for "golang"`
- `get my mastodon posts`

---

## Notes

- This skill is **read-only** (no posting, following, or other mutations)
- `scripts/mastodon_scout.py` uses stdlib only — no pip install required
- In JSON mode: output verbatim, no interpretation

---

## Authentication Setup (Agent MAY Help)

**EXCEPTION TO STRICT MODE**: If the user needs help obtaining a token, the agent **may** provide guidance before executing the skill.

### How to Obtain a Token:

**Step 1: Access Development Settings**
- Log into your Mastodon instance (e.g., mastodon.social, fosstodon.org)
- Navigate to: **Settings → Development** (or Preferences → Development)
- Direct URL: `https://[instance-domain]/settings/applications`

**Step 2: Create Application**
- Click "New Application"
  - **Application name**: `mastodon-scout` (or any name)
  - **Redirect URI**: `urn:ietf:wg:oauth:2.0:oob`
  - **Scopes**: **CRITICAL — only select `read`** (uncheck write, follow, push)

**Step 3: Get Access Token**
- Click Submit, then open the created application
- Copy the **"Your access token"** value

**Step 4: Set Environment Variable**
```bash
export MASTODON_TOKEN="paste_token_here"
```

**Step 5: Verify**
```bash
python3 ./scripts/mastodon_scout.py home --limit 5
```

### Common Mastodon Instances:
- `mastodon.social` — General purpose (default)
- `fosstodon.org` — FOSS/tech community
- `mas.to` — Tech focused
- `hachyderm.io` — Tech/infosec community

### Security Notes:
- Token is **read-only** (cannot post, follow, or delete)
- Keep token secret (don't commit to git)
- Can be revoked anytime in Development settings
- Each Mastodon instance requires its own token
