# Arknights Operator Gacha Scripts

Worker script for the Arknights Operator Gacha skill.

## Architecture

This skill uses a **worker script + LLM generation** architecture:

| Component | Responsibility |
|-----------|----------------|
| **Worker script** (`gacha_worker.py`) | Deterministic tasks: roll, fetch data, create agent, download avatar, git operations |
| **LLM (agent)** | Creative tasks: generate SOUL.md, interpret lore, spawn operator for roleplay |

## Worker Script

### gacha_worker.py

Executes all deterministic tasks and outputs JSON for LLM consumption.

**Usage:**
```bash
# Random operator (auto-roll stars)
python3 gacha_worker.py

# Force specific operator (requires --stars)
python3 gacha_worker.py --operator "Lin" --stars 6

# Dry run (no agent creation, only output JSON)
python3 gacha_worker.py --operator "Provence" --stars 5 --dry-run
```

**Output:** JSON to stdout with bilingual operator data

```json
{
  "success": true,
  "stars": 6,
  "operator": {
    "en_name": "Lin",
    "cn_name": "林",
    "avatar_url": "https://static.wikia.nocookie.net/.../Lin_icon.png",
    "en_detail_url": "https://arknights.fandom.com/wiki/Lin",
    "cn_detail_url": "https://prts.wiki/w/%E6%9E%97"
  },
  "agent_name": "lin",
  "workspace": "~/.openclaw/workspace-lin",
  "duplicate": false,
  "dialogue_url": "https://arknights.fandom.com/wiki/Lin/Dialogue"
}
```

**Output fields:**
- `operator.en_name`: Operator name in English
- `operator.cn_name`: Operator name in Chinese (from Fandom data-source="cnname")
- `operator.avatar_url`: Icon URL from Fandom
- `operator.en_detail_url`: Fandom wiki page for English lore
- `operator.cn_detail_url`: PRTS wiki page for Chinese lore
- `dialogue_url`: Fandom Dialogue page (voice lines, always in English)
- `agent_name`: Sanitized agent ID (filesystem-safe, lowercase)
- `workspace`: Path to agent workspace
- `duplicate`: True if agent already exists (needs re-roll)

**Security features:**
- Input validation (agent names: alphanumeric + hyphens only)
- Path traversal prevention
- URL domain whitelist
- HTTPS enforcement
- Content-type validation
- File size limits
- Safe subprocess (argument lists, not shell)

## Data Flow

```
User: "抽卡！" / "Gacha!"
  ↓
Agent execs: gacha_worker.py [--operator X --stars N] [--dry-run]
  ↓
Worker: Roll → Fetch list → Select → Fetch CN name → Create agent → Download → Git commit
  ↓
Worker outputs JSON (bilingual URLs)
  ↓
Agent fetches lore from en_detail_url + cn_detail_url + dialogue_url
  ↓
Agent generates SOUL.md (blending EN+CN sources)
  ↓
Agent spawns operator for 报道
  ↓
User sees operator greeting
```

## Requirements

- Python 3.7+
- requests library (`pip install requests`)
- openclaw CLI configured
- git

## Why This Architecture?

1. **Efficiency**: Worker handles all deterministic operations without LLM tokens
2. **Security**: All external inputs validated in isolated script
3. **Reliability**: Worker can be tested independently
4. **Token efficiency**: LLM only used for creative generation (SOUL.md)
5. **Progress visibility**: Worker prints progress to stderr in real-time
6. **Bilingual support**: Both English and Chinese sources always provided
