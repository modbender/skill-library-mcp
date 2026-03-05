# Memphis CLI API Reference

Complete command reference for Memphis Brain.

---

## Core Commands

### `memphis init`
Initialize Memphis in `~/.memphis/`.

**Safe to re-run:** Will refuse if config exists.

**Creates:**
- `~/.memphis/config.yaml`
- `~/.memphis/chains/`
- `~/.memphis/embeddings/`

---

### `memphis status`
Health report.

**Output:**
- Chains count
- Provider status
- Embeddings status
- Vault status
- Recent activity

**Use:** After every major change.

---

### `memphis verify --chain <name>`
Check chain integrity.

**Flags:**
- `--chain <name>` — specific chain
- `--all` — all chains

**Exit codes:**
- 0 — valid
- 1 — corrupted

---

### `memphis repair --chain <name>`
Fix corrupted chain.

**Flags:**
- `--dry-run` — preview fixes
- `--chain <name>` — specific chain

---

## Journaling

### `memphis journal <text>`
Append block to journal chain.

**Syntax:**
```bash
memphis journal "text" --tags tag1,tag2 [--force]
```

**Flags:**
- `--tags <list>` — comma-separated tags
- `--force` — trigger autosummary immediately

**Block structure:**
```json
{
  "type": "journal",
  "text": "text",
  "tags": ["tag1", "tag2"],
  "timestamp": "ISO8601",
  "hash": "sha256"
}
```

---

### `memphis decide <title> <choice>`
Record decision.

**Syntax:**
```bash
memphis decide "Title" "Choice" --options "A|B|C" --reasoning "..." --tags tag1,tag2
```

**Flags:**
- `--options <list>` — pipe-separated options
- `--reasoning <text>` — why this choice
- `--tags <list>` — comma-separated tags

**Block structure:**
```json
{
  "type": "decision",
  "title": "Title",
  "choice": "Choice",
  "options": ["A", "B", "C"],
  "reasoning": "...",
  "tags": ["tag1"],
  "timestamp": "ISO8601",
  "status": "active"
}
```

**Statuses:**
- `active` — current
- `superseded` — replaced by newer
- `contradicted` — proven wrong
- `stale` — outdated

---

### `memphis show decision <id>`
Display decision details.

**Output:**
- Full decision block
- Status
- Related decisions

---

## Recall

### `memphis ask <question>`
Query Memphis with semantic search + LLM.

**Syntax:**
```bash
memphis ask "Question" [flags]
```

**Flags:**
- `--provider <name>` — LLM provider (ollama, openai, codex)
- `--top <n>` — context blocks (default 8, use 20+)
- `--graph` — include knowledge graph
- `--prefer-summaries` — use summary chains
- `--since <date>` — filter from date
- `--until <date>` — filter until date
- `--type <type>` — filter by type
- `--tags <list>` — filter by tags
- `--semantic-only` — skip keyword search
- `--no-semantic` — keyword only
- `--no-save` — don't save to ask chain (bug: still saves)
- `--json` — JSON output
- `--use-vault` — unlock vault keys
- `--vault-password-env <var>` — vault password env var

**Example:**
```bash
memphis ask "What are my preferences?" \
  --provider ollama \
  --top 20 \
  --graph \
  --prefer-summaries \
  --since 2026-02-28
```

---

## Embeddings

### `memphis embed`
Generate embeddings for chains.

**Syntax:**
```bash
memphis embed [--chain <name>]
```

**Flags:**
- `--chain <name>` — specific chain (default: all)

**Backend:** Ollama `nomic-embed-text`

**When to run:**
- After batch journaling (>10 blocks)
- After ingestion
- After editing chains manually

---

## Ingestion

### `memphis ingest <path>`
Import documents into chains.

**Syntax:**
```bash
memphis ingest <path> [flags]
```

**Flags:**
- `--recursive` — recurse directories
- `--chain <name>` — target chain (default: from path)
- `--embed` — generate embeddings
- `--dry-run` — preview only

**Formats:** `.md`, `.txt`, `.json`, `.jsonl`, `.pdf`

**Example:**
```bash
memphis ingest ./docs --recursive --chain research --embed
```

---

## Knowledge Graph

### `memphis graph build`
Build knowledge graph from chains.

**Creates:**
- `~/.memphis/graph/nodes.jsonl`
- `~/.memphis/graph/edges.jsonl`

**Edge types:**
- `semantic` — similarity-based
- `tag` — shared tags
- `ref` — explicit references

---

### `memphis graph show`
Display graph nodes/edges.

**Flags:**
- `--chain <name>` — filter by chain
- `--limit <n>` — max nodes (default 10)
- `--json` — JSON output

---

## Reflection

### `memphis reflect`
Analyze patterns and generate insights.

**Syntax:**
```bash
memphis reflect [--daily|--weekly|--deep] [--save]
```

**Flags:**
- `--daily` — quick daily reflection
- `--weekly` — comprehensive weekly
- `--deep` — full analysis
- `--save` — save to reflection chain
- `--json` — JSON output

**Insight types:**
- Tag frequency
- Theme extraction
- Decision patterns
- Graph clusters
- Stale decisions
- Contradictions
- Opportunities

---

## Share-Sync

### `memphis share-sync`
Sync shareable blocks via IPFS/Pinata.

**Syntax:**
```bash
memphis share-sync [flags]
```

**Flags:**
- `--push` — push local blocks to IPFS
- `--pull` — pull remote blocks from network
- `--all` — push + pull
- `--push-disabled` — pull only (read-only node)
- `--cleanup` — remove old pins (TTL 7 days)
- `--limit <n>` — max blocks
- `--since <date>` — from date
- `--dry-run` — preview only

**Requires:**
- `share` tag on blocks
- Pinata JWT in config or env

---

### `memphis share plan`
Dry-run diff of what would sync.

**Shows:**
- Blocks to push
- Blocks to pull
- Conflicts

---

## Workspace

### `memphis workspace list`
List available workspaces.

**Output:**
- Workspace IDs
- Names
- Active workspace

---

### `memphis workspace set <id>`
Switch active workspace.

**Effect:**
- Changes chain directory
- Isolates memory

---

## Trade

### `memphis trade create <recipient>`
Create trade offer.

**Syntax:**
```bash
memphis trade create <recipient-did> --blocks <spec> --ttl <days>
```

**Flags:**
- `--blocks <spec>` — block spec (e.g., `journal:0-100`)
- `--ttl <days>` — offer validity

**Output:** Manifest JSON

---

### `memphis trade accept <manifest>`
Accept trade offer.

**Validates:**
- Signature
- Block availability
- TTL

---

### `memphis trade list`
List pending offers.

---

### `memphis trade verify <manifest>`
Verify manifest signature.

---

## MCP

### `memphis mcp start`
Start MCP server (stdio).

**Tools exposed:**
- `memphis_search` — semantic search
- `memphis_recall` — get blocks
- `memphis_decision_create` — create decision
- `memphis_journal_add` — add journal
- `memphis_status` — health check

**Use:** External tools integration.

---

### `memphis mcp inspect`
Show available tools.

---

## Offline

### `memphis offline status`
Show offline mode status.

**Output:**
- Mode (on/off/auto)
- Network status
- Active model

---

### `memphis offline on`
Force offline mode.

**Effect:** Use only local models.

---

### `memphis offline auto`
Auto-detect network.

**Behavior:** Switch based on connectivity.

---

### `memphis offline model <name>`
Set offline model.

**Example:**
```bash
memphis offline model qwen2.5:3b
```

---

## Vault

### `memphis vault init`
Initialize encrypted vault.

**Syntax:**
```bash
memphis vault init --password-env <var>
```

**Creates:** `~/.memphis/vault.enc`

---

### `memphis vault add <key> <value>`
Store secret.

**Syntax:**
```bash
memphis vault add <key> <value> --password-env <var>
```

---

### `memphis vault get <key>`
Retrieve secret.

**Syntax:**
```bash
memphis vault get <key> --password-env <var>
```

---

### `memphis vault list`
List stored keys (not values).

---

### `memphis vault delete <key>`
Delete secret.

---

### `memphis vault backup`
Generate 24-word recovery seed.

**Output:** Mnemonic phrase

**⚠️ STORE SECURELY OFFLINE**

---

### `memphis vault recover --seed "..."`
Recover vault from seed.

**Syntax:**
```bash
memphis vault recover --seed "word1 word2 ... word24"
```

---

## Daemon

### `memphis daemon start`
Start background collectors.

**Collectors:**
- Git — commit history
- Shell — command history
- File — watch changes

---

### `memphis watch <path>`
Watch directory for changes.

**Syntax:**
```bash
memphis watch <path> --chain <name> [--no-embed]
```

**Flags:**
- `--chain <name>` — target chain
- `--no-embed` — skip auto-embed

---

## Summary

### `memphis summarize`
Generate chain summaries.

**Syntax:**
```bash
memphis summarize --chain <name> [--force]
```

**Flags:**
- `--chain <name>` — specific chain
- `--force` — regenerate existing

**Autosummary:** Triggers every N blocks (config).

---

## Version

### `memphis --version`
Show version.

---

## Help

### `memphis --help`
Show general help.

### `memphis <command> --help`
Show command help.
