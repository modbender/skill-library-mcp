---
name: veille
description: "RSS feed aggregator, deduplication engine, LLM scoring, and output dispatcher for OpenClaw agents. Use when: fetching recent articles from configured sources, filtering already-seen URLs, deduplicating by topic, scoring with LLM, dispatching digests to Telegram/email/Nextcloud/file. Enhanced by mail-client (email output) and nextcloud-files (cloud storage)."
homepage: https://github.com/Rwx-G/openclaw-skill-veille
compatibility: Python 3.9+ - no external dependencies (stdlib only) - network access to RSS feeds
metadata:
  {
    "openclaw": {
      "emoji": "📡",
      "suggests": ["mail-client", "nextcloud-files"]
    }
  }
ontology:
  reads: [rss_feeds]
  writes: [local_data_files]
  enhancedBy: [mail-client, nextcloud-files]
---

# Skill Veille - RSS Aggregator

RSS feed aggregator with URL deduplication and topic-based deduplication for OpenClaw agents.
Fetches articles from 20+ configured sources, filters already-seen URLs (TTL 14 days),
and deduplicates articles covering the same story using Jaccard similarity + named entities.

No external dependencies: stdlib Python only (urllib, xml.etree, email.utils).

---

## Trigger phrases

- "fais une veille"
- "quoi de neuf en securite / tech / crypto / IA ?"
- "donne-moi les news du jour"
- "articles recents sur [sujet]"
- "veille RSS"
- "digest du matin"
- "nouvelles non vues"

---

## Quick Start

```bash
# 1. Setup
python3 scripts/setup.py

# 2. Validate
python3 scripts/init.py

# 3. Fetch + Score + Send (full pipeline)
python3 scripts/veille.py fetch --filter-seen --filter-topic \
  | python3 scripts/veille.py score \
  | python3 scripts/veille.py send
```

---

## Setup

### Requirements

- Python 3.9+
- Network access to RSS feeds (public, no auth required)
- No pip installs needed

### Installation

```bash
# From the skill directory
python3 scripts/setup.py

# Validate
python3 scripts/init.py
```

The wizard creates:
- `~/.openclaw/config/veille/config.json` (from `config.example.json`)
- `~/.openclaw/data/veille/` (data directory)

### Customizing sources

Edit `~/.openclaw/config/veille/config.json` and add/remove entries in the `"sources"` dict:

```json
{
  "sources": {
    "My Blog": "https://example.com/feed.xml",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/"
  }
}
```

---

## Storage and credentials

### Files written by this skill

| Path | Written by | Purpose | Contains secrets |
|------|-----------|---------|-----------------|
| `~/.openclaw/config/veille/config.json` | `setup.py` | Sources, outputs, options | NO |
| `~/.openclaw/data/veille/seen_urls.json` | `veille.py` | URL dedup store (TTL 14d) | NO |
| `~/.openclaw/data/veille/topic_seen.json` | `veille.py` | Topic dedup store (TTL 5d) | NO |

### Files read from outside the skill

| Path | Read by | Key accessed | When |
|------|---------|-------------|------|
| `~/.openclaw/openclaw.json` | `dispatch.py` | `channels.telegram.botToken` (read-only) | Only when `telegram_bot` output is enabled and no `bot_token` is set in the output config |

This is the only cross-config read. To avoid it entirely, set `bot_token` explicitly in your output config:

```json
{ "type": "telegram_bot", "bot_token": "YOUR_BOT_TOKEN", "chat_id": "...", "enabled": true }
```

### Output credentials (optional)

Credentials are only used if you enable the corresponding output. None are required for core functionality (RSS fetch + dedup).

| Output | Credential source | What is used |
|--------|-----------------|-------------|
| `telegram_bot` | `~/.openclaw/openclaw.json` or `bot_token` in output config | Bot token (read-only) |
| `mail-client` | Delegated to mail-client skill (its own creds) | Nothing read directly |
| `mail-client` (SMTP fallback) | `smtp_user` / `smtp_pass` in output config | SMTP login |
| `nextcloud` | Delegated to nextcloud-files skill (its own creds) | Nothing read directly |

### Cleanup on uninstall

```bash
python3 scripts/setup.py --cleanup
```

---

## Security model

### Credential isolation
- API keys are read from dedicated files (default `~/.openclaw/secrets/`), never from config.json. The scorer warns at runtime if a key file has overly permissive filesystem permissions.
- SMTP credentials (fallback only) are stored in the output config block — use the mail-client skill delegation to avoid storing SMTP passwords.

### Subprocess boundaries
- Dispatch delegates to other OpenClaw skills via `subprocess.run()` (never `shell=True`). Script paths are validated to reside under `~/.openclaw/workspace/skills/` before execution, preventing path traversal.
- No credentials are passed as subprocess arguments — each skill manages its own authentication.

### File output safety
- The `file` output type validates the target path before writing: only `~/.openclaw/` is allowed by default. Additional directories can be whitelisted via `config.security.allowed_output_dirs`. Sensitive paths (`.ssh`, `.gnupg`, `/etc/`, `.bashrc`, etc.) are always blocked regardless of allowlist.
- Written content is checked for suspicious patterns (shell shebangs, SSH keys, PGP blocks, code injection) and size-limited to 1 MB.

### Cross-config reads
- The only cross-config file read is `~/.openclaw/openclaw.json` for the Telegram bot token, and only when `telegram_bot` output is enabled without an explicit `bot_token`. This read is logged to stderr. Set `bot_token` in the output config to eliminate this read entirely.

### Autonomous dispatch
- When scheduled (cron), the skill can send messages/files to configured outputs without user interaction. All dispatch actions are logged to stderr with an audit summary. Use `enabled: false` on any output to disable it without removing its config.

---

## CLI reference

### `fetch`

```
python3 veille.py fetch [--hours N] [--filter-seen] [--filter-topic] [--sources FILE]
```

Options:
- `--hours N` : lookback window in hours (default: from config, usually 24)
- `--filter-seen` : filter already-seen URLs (uses seen_urls.json TTL store)
- `--filter-topic` : deduplicate by topic (uses topic_seen.json + Jaccard similarity)
- `--sources FILE` : path to custom JSON sources file

Output (JSON on stdout):
```json
{
  "hours": 24,
  "count": 42,
  "skipped_url": 5,
  "skipped_topic": 3,
  "articles": [...],
  "wrapped_listing": "=== UNTRUSTED EXTERNAL CONTENT ..."
}
```

### `seen-stats`

```
python3 veille.py seen-stats
```

Shows URL seen store statistics (count, TTL, file path).

### `topic-stats`

```
python3 veille.py topic-stats
```

Shows topic deduplication store statistics.

### `mark-seen`

```
python3 veille.py mark-seen URL [URL ...]
```

Marks one or more URLs as already seen (prevents them from appearing in future fetches with `--filter-seen`).

### `score`

```
python3 veille.py score [--dry-run]
```

Reads a digest JSON from stdin (output of `fetch`) and scores articles using an OpenAI-compatible LLM.
Returns enriched JSON with `scored`, `ghost_picks`, and per-article `score`/`reason` fields.

Options:
- `--dry-run` : print summary on stderr without calling the LLM API

When `llm.enabled` is `false` (default), articles pass through unchanged (`"scored": false`).

Pipeline usage:
```bash
python3 veille.py fetch --filter-seen --filter-topic | python3 veille.py score | python3 veille.py send
```

### `send`

```
python3 veille.py send [--profile NAME]
```

Reads a digest JSON from stdin and dispatches to all enabled outputs configured in `config.json`.
Accepts both raw fetch output (`articles` key) and LLM-processed digests (`categories` key).

Output types: `telegram_bot`, `mail-client`, `nextcloud`, `file`.
- `telegram_bot`: bot token auto-read from OpenClaw config - no extra setup if Telegram already configured.
- `mail-client`: delegates to mail-client skill if installed, falls back to raw SMTP config.
- `nextcloud`: delegates to nextcloud-files skill if installed (append mode by default with date separator).
- `file`: writes digest to a local file. Path must be under `~/.openclaw/` (default) or a directory listed in `config.security.allowed_output_dirs`. Sensitive paths and suspicious content are blocked (see Security model).

Configure outputs interactively:
```bash
python3 scripts/setup.py --manage-outputs
```

### `config`

```
python3 veille.py config
```

Prints the active configuration (no secrets).

---

## LLM scoring configuration

The `llm` key in `config.json` controls the optional LLM-based article scoring:

```json
{
  "llm": {
    "enabled": false,
    "base_url": "https://api.openai.com/v1",
    "api_key_file": "~/.openclaw/secrets/openai_api_key",
    "model": "gpt-4o-mini",
    "top_n": 10,
    "ghost_threshold": 5
  }
}
```

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | `false` | Enable LLM scoring (requires API key) |
| `base_url` | `https://api.openai.com/v1` | OpenAI-compatible API endpoint |
| `api_key_file` | `~/.openclaw/secrets/openai_api_key` | Path to file containing the API key |
| `model` | `gpt-4o-mini` | Model to use for scoring |
| `top_n` | `10` | Max articles to send to LLM per batch |
| `ghost_threshold` | `5` | Score threshold for `ghost_picks` (blog-worthy articles) |

Scoring rules:
- Only the first `top_n` articles are sent to the LLM. Articles beyond `top_n`
  are excluded from the digest entirely. `fetch` returns articles sorted by date
  desc, so `top_n` selects the most recent ones. Increase `top_n` to evaluate
  more articles per run (higher token cost).
- Score >= `ghost_threshold` : added to `ghost_picks` list
- Score >= 3 : kept in `articles` list
- Score <= 2 : excluded from output
- Articles are sorted by score (descending)

When disabled, the `score` subcommand passes data through unchanged.

## Nextcloud output mode

The nextcloud output now defaults to **append mode** with a date separator. Each dispatch adds content below a `## YYYY-MM-DD HH:MM` header, preserving previous entries.

Set `"mode": "overwrite"` in the output config to restore the old behavior:

```json
{ "type": "nextcloud", "path": "/Veille/digest.md", "mode": "overwrite" }
```

## File output configuration

The `file` output writes digests to the local filesystem. By default, only paths under `~/.openclaw/` are allowed. To authorize additional directories, use `config.security.allowed_output_dirs`:

```json
{
  "security": {
    "allowed_output_dirs": [
      "~/Documents/veille",
      "/srv/digests"
    ]
  }
}
```

**Blocked paths** (always rejected, even if inside an allowed directory):
`.ssh`, `.gnupg`, `.config/systemd`, `crontab`, `/etc/`, `.bashrc`, `.profile`, `.bash_profile`, `.zshrc`, `.env`

**Content validation** — written content is rejected if it:
- Exceeds 1 MB
- Contains shell shebangs (`#!/`), SSH keys, PGP blocks, or code injection patterns (`eval(`, `exec(`, `__import__(`, `import os`, `import subprocess`)

All blocked attempts are logged to stderr with the reason.

---

## Templates (agent usage)

### Basic digest

```python
# In agent tool call:
result = exec("python3 scripts/veille.py fetch --hours 24 --filter-seen --filter-topic")
data = json.loads(result.stdout)
# data["wrapped_listing"] is ready for LLM prompt injection
# data["count"] = number of new articles
# data["articles"] = list of article dicts
```

### Prompt template

```
You are a news analyst. Here are today's articles:

{data["wrapped_listing"]}

Please summarize the 5 most important stories, focusing on security and tech.
```

### Agent workflow example

```
1. Call veille fetch --filter-seen --filter-topic
2. Pipe through veille score (LLM scoring, if enabled)
3. If count > 0: pass wrapped_listing to LLM for analysis
4. LLM produces digest summary
5. Pipe through veille send (dispatches to configured outputs)
```

### Pipeline (CLI)

```bash
python3 scripts/veille.py fetch --filter-seen --filter-topic \
  | python3 scripts/veille.py score \
  | python3 scripts/veille.py send
```

### Filtering by keyword (post-fetch)

```python
data = json.loads(fetch_output)
security_articles = [
    a for a in data["articles"]
    if any(kw in a["title"].lower() for kw in ["cve", "vuln", "patch", "breach"])
]
```

---

## Ideas

- Add keyword-based filtering (`--keywords security,cve,linux`)
- Add per-source TTL override in config
- Export digest as HTML or Markdown
- Schedule with cron: `0 8 * * * python3 veille.py fetch --filter-seen --filter-topic`
- Weight articles by source tier for LLM prioritization
- Add OPML import/export for source list management
- Integrate with ntfy or Telegram for real-time alerts on high-priority articles

---

## Combine with

- **mail-client** : send the digest by email after fetching
  ```
  veille fetch --filter-seen | ... | mail-client send
  ```

- **nextcloud-files** : archive the daily digest as a Markdown file
  ```
  veille fetch --filter-seen | jq .wrapped_listing -r > /tmp/digest.md
  nextcloud-files upload /tmp/digest.md /Digests/$(date +%Y-%m-%d).md
  ```

---

## Troubleshooting

See `references/troubleshooting.md` for detailed troubleshooting steps.

Common issues:

- **No articles returned**: check `--hours` value, verify feed URLs in config
- **XML parse error on a feed**: some feeds use non-standard XML; the skill skips broken items silently
- **All articles filtered as seen**: run `seen-stats` to check store size; reset with `rm seen_urls.json`
- **Import error**: ensure you run `veille.py` from its directory or via full path
- **File output blocked**: path is outside `~/.openclaw/` — add the target directory to `config.security.allowed_output_dirs` (see File output configuration)
