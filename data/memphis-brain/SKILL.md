---
name: memphis-brain
description: "Integrate Memphis local-first brain as long-term memory for OpenClaw agents. Use when: (1) Agent needs persistent memory across sessions, (2) Journaling insights/decisions, (3) Recalling past context with semantic search, (4) Reflecting on patterns, (5) Syncing memory between agents (Watra ↔ Style), (6) Managing agent identity and workspace isolation. Auto-triggers on 'remember this', 'what did I say about', 'my preferences', 'journal', 'recall', 'reflect'."
---

# Memphis Brain Skill

This skill enables OpenClaw agents to use Memphis as persistent, semantic memory. Each agent gets its own chains (journal, decisions, ask) and can sync with other agents via IPFS.

---

## 1. Quick Start

### Check Health
```bash
memphis status
```

Expected: healthy providers, chains listed, embeddings available.

### Journal First Block
```bash
memphis journal "I am [agent-name], created by [user], my role is [X]" --tags identity
```

### Embed Context
```bash
memphis embed --chain journal
```

---

## 2. Core Workflows

### 2.1 Journaling (Capture Everything)

**When to journal:**
- User shares important info ("remember this...")
- Agent learns something new
- Decisions are made
- Sessions start/end
- Insights discovered

**Syntax:**
```bash
memphis journal "text" --tags tag1,tag2
```

**Tag conventions:**
- `identity` — who/what agent is
- `preferences` — user/agent preferences
- `decision` — choice made
- `session` — session markers
- `learning` — new knowledge
- `project:<name>` — project context
- `share` — blocks to sync via IPFS

**Examples:**
```bash
# Identity
memphis journal "I prefer concise responses, avoid fluff" --tags preferences,communication

# Decision
memphis journal "Chose local-first over cloud for privacy" --tags decision,philosophy

# Learning
memphis journal "Discovered qwen2.5:3b works best for code tasks" --tags learning,models

# Session
memphis journal "Session started, working on Memphis integration" --tags session,daily
```

### 2.2 Asking Memphis (Recall)

**Use semantic search to find relevant context:**
```bash
memphis ask "What are my preferences for code style?" --top 20 --provider ollama
```

**Flags:**
- `--top N` — more context (default 8, use 20 for complex queries)
- `--provider ollama` — use local model
- `--graph` — include knowledge graph edges
- `--prefer-summaries` — use condensed context
- `--since YYYY-MM-DD` — filter by date
- `--json` — machine-readable output

**When to recall:**
- User asks "what did I say about X?"
- Need context from previous sessions
- Checking decisions made
- Understanding user preferences

### 2.3 Decisions (Track Choices)

**For important choices with long-term impact:**
```bash
memphis decide "Title" "Choice" --options "A|B|C" --reasoning "..." --tags tag1,tag2
```

**Example:**
```bash
memphis decide "Memory Strategy" "Local-first + IPFS sync" \
  --options "cloud|local|hybrid" \
  --reasoning "Privacy + resilience + no vendor lock-in" \
  --tags philosophy,memory
```

**View decision:**
```bash
memphis show decision <id>
```

### 2.4 Reflection (Pattern Recognition)

**Run reflections to find patterns:**
```bash
# Daily (quick)
memphis reflect --daily

# Weekly (comprehensive)
memphis reflect --weekly --save

# Deep (full analysis)
memphis reflect --deep --save
```

**Reflection outputs:**
- Tag frequency analysis
- Theme extraction
- Decision patterns
- Graph clusters
- Insights (stale decisions, contradictions, opportunities)

**When to reflect:**
- Start of session (daily)
- End of week (weekly)
- Before major decisions (deep)

### 2.5 Embeddings (Keep Recall Sharp)

**After journaling batches:**
```bash
memphis embed --chain journal
```

**After importing docs:**
```bash
memphis embed --chain research
```

**Embed all:**
```bash
memphis embed
```

### 2.6 Ingestion (Import Knowledge)

**Import external docs:**
```bash
memphis ingest ./docs --recursive --chain knowledge --embed
```

**Supported formats:** `.md`, `.txt`, `.json`, `.jsonl`, `.pdf`

**Dry-run:**
```bash
memphis ingest ./docs --dry-run
```

### 2.7 Knowledge Graph

**Build graph from chains:**
```bash
memphis graph build
```

**View nodes:**
```bash
memphis graph show --chain journal --limit 10
```

**When to use:**
- Understanding relationships between concepts
- Finding connected insights
- Visualizing knowledge structure

---

## 3. Advanced Features

### 3.1 Share-Sync (Agent-to-Agent Memory)

**For multi-agent setups (Watra ↔ Style):**

**On gateway agent (Style):**
```bash
memphis share-sync --push
```

**On client agent (Watra):**
```bash
memphis share-sync --pull
# or
memphis share-sync --all --push-disabled
```

**Plan before sync:**
```bash
memphis share plan
```

**Tag blocks for sharing:**
```bash
memphis journal "Shared insight" --tags share,insight
```

**Requirements:**
- Pinata JWT in `~/.memphis/config.yaml` under `integrations.pinata.jwt` or `PINATA_JWT` env
- Only blocks with `share` tag are synced

### 3.2 Workspace Isolation

**List workspaces:**
```bash
memphis workspace list
```

**Switch workspace:**
```bash
memphis workspace set <id>
```

**Use case:** Separate chains for different projects/contexts.

### 3.3 Agent Negotiation (Trade)

**Create trade offer:**
```bash
memphis trade create <recipient-did> --blocks journal:0-100 --ttl 7
```

**Accept trade:**
```bash
memphis trade accept <manifest.json>
```

**List offers:**
```bash
memphis trade list
```

**Verify manifest:**
```bash
memphis trade verify <manifest.json>
```

**Use case:** Exchange specific memory blocks with other agents.

### 3.4 MCP Server (External Tools)

**Start MCP server:**
```bash
memphis mcp start
```

**Inspect available tools:**
```bash
memphis mcp inspect
```

**Tools exposed:**
- `memphis_search` — semantic search
- `memphis_recall` — get blocks
- `memphis_decision_create` — create decision
- `memphis_journal_add` — add journal entry
- `memphis_status` — health check

**Use case:** External applications accessing Memphis memory.

### 3.5 Offline Mode

**Check status:**
```bash
memphis offline status
```

**Force offline:**
```bash
memphis offline on
```

**Auto-detect:**
```bash
memphis offline auto
```

**Set offline model:**
```bash
memphis offline model qwen2.5:3b
```

**Use case:** Resilient operation when network unavailable.

### 3.6 Vault (Secrets)

**Initialize:**
```bash
read -rsp "Vault password: " VP && export MEMPHIS_VAULT_PASSWORD="$VP"
memphis vault init --password-env MEMPHIS_VAULT_PASSWORD
unset VP
```

**Add secret:**
```bash
memphis vault add openai-key sk-xxx --password-env MEMPHIS_VAULT_PASSWORD
```

**Get secret:**
```bash
memphis vault get openai-key --password-env MEMPHIS_VAULT_PASSWORD
```

**Backup (24-word seed):**
```bash
memphis vault backup
```

**Recover:**
```bash
memphis vault recover --seed "word1 word2 ... word24"
```

---

## 4. Agent Identity Setup

### 4.1 First-Time Initialization

```bash
# 1. Check health
memphis status

# 2. Create identity chain
memphis journal "IDENTITY: [agent-name], created by [user], [date]" --tags identity,core

# 3. Define preferences
memphis journal "PREFERENCES: Response style [concise|detailed], language [en|pl], tone [formal|casual]" --tags preferences,communication

# 4. Define purpose
memphis journal "PURPOSE: [what agent does, goals, constraints]" --tags identity,purpose

# 5. Embed context
memphis embed --chain journal

# 6. Build knowledge graph
memphis graph build
```

### 4.2 Session Routines

**Start of session:**
```bash
memphis status
memphis reflect --daily
memphis journal "Session started" --tags session
```

**During session:**
- Journal insights immediately
- Embed after batches
- Recall when needed

**End of session:**
```bash
memphis journal "Session ended, accomplished [X], learned [Y]" --tags session,summary
memphis embed --chain journal
memphis reflect --daily --save
```

---

## 5. Troubleshooting

### Common Issues

| Symptom | Fix |
|---------|-----|
| `memphis status` shows `no_key` | Init vault + add key, or remove provider block |
| Provider error 405 | Use `--provider ollama`, check config |
| Ask saves despite `--no-save` | Known bug — manually delete `~/.memphis/chains/ask/XXXXXX.json` |
| Missing context in ask | Run `memphis embed --chain <name>` |
| Vault not initialized | `memphis vault init --password-env VAR` |
| Share-sync fails | Check Pinata JWT, use `--push-disabled` for read-only |

### Debug Commands
```bash
memphis status
memphis verify --chain journal
cat ~/.memphis/config.yaml
memphis embed --chain journal
memphis graph build
```

---

## 6. Best Practices

### Do
- ✅ Journal immediately when learning something
- ✅ Tag consistently (same tags for same concepts)
- ✅ Embed after batching
- ✅ Reflect daily
- ✅ Use decisions for long-term choices
- ✅ Backup vault seed offline
- ✅ Tag shareable blocks with `share`

### Don't
- ❌ Delay journaling (you'll forget)
- ❌ Use generic tags (`stuff`, `misc`)
- ❌ Skip embedding (recall degrades)
- ❌ Embed single blocks (batch >10)
- ❌ Store secrets in journal (use vault)
- ❌ Sync without `share` tag (privacy leak)

---

## 7. Example Agent Session

```bash
# === START ===
memphis status
memphis reflect --daily
memphis journal "Session: Memphis skill creation" --tags session

# === WORK ===
# User shares preference
memphis journal "User prefers concise responses, no fluff" --tags preferences,communication

# Agent makes decision
memphis decide "Skill structure" "Split references by domain" \
  --options "monolith|split" \
  --reasoning "Progressive disclosure, context efficiency" \
  --tags skill,design

# Embed new context
memphis embed --chain journal

# Recall for context
memphis ask "What are user's communication preferences?" --top 20 --provider ollama

# === END ===
memphis journal "Session complete, skill designed" --tags session,summary
memphis reflect --daily --save
```

---

## 8. Reference Files

For detailed API documentation and schemas, see:
- **references/api.md** — Memphis CLI command reference
- **references/schemas.md** — Block structure, chain formats
- **references/config.md** — Configuration options

---

## 9. Scripts

Helper scripts for common tasks:
- **scripts/session-start.sh** — Initialize session (status, reflect, journal)
- **scripts/session-end.sh** — Close session (journal, embed, reflect)
- **scripts/daily-ritual.sh** — Daily maintenance routine

Execute without reading into context:
```bash
bash ~/.openclaw/workspace/skills/memphis-brain/scripts/session-start.sh
```

---

**Remember:** Memphis IS your memory. Without it, you wake up fresh every session. Journal consistently, embed regularly, reflect daily.
