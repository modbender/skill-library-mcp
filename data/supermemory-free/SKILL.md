---
name: supermemory-free
description: Cloud knowledge backup and retrieval using Supermemory.ai free tier. Store high-value insights to the cloud and search them back when local memory is insufficient. Uses standard /v3/documents and /v3/search endpoints (no Pro-only features).
---

# Supermemory Free — Cloud Knowledge Backup

Backs up important knowledge and insights to Supermemory.ai's cloud using the **free tier API**.  
Uses only `/v3/documents` (store) and `/v3/search` (retrieve) — no Pro-only endpoints.

## Prerequisites

Set in `.env`
```
SUPERMEMORY_OPENCLAW_API_KEY="sm_..."
```

## Tools

### supermemory_cloud_store
Store a knowledge string to the cloud.

```bash
python3 skills/supermemory-free/store.py "Your knowledge string here"

# With optional container tag (namespace/filter)
python3 skills/supermemory-free/store.py "knowledge string" --tag openclaw

# With metadata
python3 skills/supermemory-free/store.py "knowledge string" --tag fixes --source "session"

# Output raw JSON
python3 skills/supermemory-free/store.py "knowledge string" --json
```

**When to use:**
- User asks to "remember" something permanently
- Important configuration/setup knowledge
- Resolved problems / solutions discovered
- Key facts you want cross-session persistence for

---

### supermemory_cloud_search
Search the cloud memory for relevant knowledge.

```bash
python3 skills/supermemory-free/search.py "your query"

# With container tag filter
python3 skills/supermemory-free/search.py "your query" --tag openclaw

# More results
python3 skills/supermemory-free/search.py "your query" --limit 10

# Higher precision (less noise)
python3 skills/supermemory-free/search.py "your query" --threshold 0.7

# Search across ALL tags
python3 skills/supermemory-free/search.py "your query" --no-tag
```

**When to use:**
- Local memory (MEMORY.md, daily logs) doesn't have the answer
- User references something from "a long time ago"
- Cross-session knowledge lookup
- "Do you remember when..." queries

---

### Auto-Capture (Cron)
Scans recent session memory logs and automatically pushes high-value insights to Supermemory cloud.

```bash
# Run manually
python3 skills/supermemory-free/auto_capture.py

# Dry run (show what would be captured, no upload)
python3 skills/supermemory-free/auto_capture.py --dry-run

# Scan last N days (default: 3)
python3 skills/supermemory-free/auto_capture.py --days 7

# Force re-upload even if already seen
python3 skills/supermemory-free/auto_capture.py --force

# Verbose mode
python3 skills/supermemory-free/auto_capture.py --verbose
```

**Install cron job (runs daily at 2:00 AM UTC):**
```bash
bash skills/supermemory-free/install_cron.sh
```

**Remove cron job:**
```bash
bash skills/supermemory-free/install_cron.sh --remove
```

**Check cron status:**
```bash
bash skills/supermemory-free/install_cron.sh --status
```

---

## What Gets Auto-Captured

The auto-capture script identifies "high-value" insights from memory logs using these heuristics:

| Pattern | Label | Example |
|---------|-------|---------|
| Resolved errors / fixes | `fix` | `Fixed: SSL cert error by running...` |
| Error context | `error` | `Exception: Connection refused on port 5432` |
| Configuration paths | `config` | `/etc/nginx/sites-available/default` |
| API/endpoint info | `api` | `Endpoint: POST /v3/documents for storage` |
| User preferences | `preference` | `User prefers Python over Node for scripts` |
| Decisions made | `decision` | `Decided to use PostgreSQL because...` |
| Learned facts | `insight` | `Learned that cron syntax for...` |
| Installs / setup | `setup` | `Installed nginx, configured with...` |
| Bullet-point blocks | `bullet` | `- Key finding: X works better than Y` |

**Deduplication:** Already-uploaded items are tracked in `.capture_state.json` — re-running is safe.

---

## Container Tags

Use `--tag` to namespace your memories:

| Tag | Purpose |
|-----|---------|
| `openclaw` | General OpenClaw session knowledge (default) |
| `fixes` | Bug fixes and solutions |
| `config` | Configuration and setup |
| `user-prefs` | User preferences |
| `projects` | Project-specific knowledge |

---

## Files

| File | Purpose |
|------|---------|
| `store.py` | CLI tool: upload knowledge to cloud |
| `search.py` | CLI tool: search cloud knowledge |
| `auto_capture.py` | Cron script: auto-analyze memory logs |
| `install_cron.sh` | Install/remove/status of cron job |
| `.capture_state.json` | Dedup state (auto-generated, gitignore) |
| `SKILL.md` | This file |
| `_meta.json` | Skill metadata |

---

## API Info

- **Base URL:** `https://api.supermemory.ai`
- **Store endpoint:** `POST /v3/documents`
- **Search endpoint:** `POST /v3/search`
- **Auth:** Bearer token from `SUPERMEMORY_OPENCLAW_API_KEY`
- **Free tier limits:** Check https://console.supermemory.ai for current quotas
- **Note:** Cloudflare-compatible headers included — avoids 1010 access denial errors

---

## Troubleshooting

**HTTP 403 / 1010 Access Denied:**  
The scripts include proper `User-Agent`, `Origin`, and `Referer` headers to satisfy Cloudflare. If it recurs, verify the API key is valid at https://console.supermemory.ai.

**No memory files found:**  
Auto-capture looks in `memory/YYYY-MM-DD.md`. Ensure your memory skill is writing daily logs there.

**Re-upload everything:**  
Delete `.capture_state.json` or use `--force` to ignore the dedup state.
