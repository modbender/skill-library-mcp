# Memphis Brain Skill

Integrate Memphis local-first brain as persistent memory for OpenClaw agents.

## What It Does

- **Persistent Memory**: Agents remember across sessions
- **Semantic Recall**: Find relevant context with embeddings
- **Journaling**: Capture insights, decisions, learnings
- **Reflection**: Daily/weekly pattern recognition
- **Multi-Agent Sync**: Share memory via IPFS (Watra ↔ Style)

## Quick Start

```bash
# Initialize new agent
bash ~/.openclaw/workspace/skills/memphis-brain/scripts/agent-init.sh

# Start session
bash ~/.openclaw/workspace/skills/memphis-brain/scripts/session-start.sh

# Journal insight
memphis journal "Discovered X works best for Y" --tags learning,discovery

# Recall context
memphis ask "What did I learn about X?" --top 20 --provider ollama

# End session
bash ~/.openclaw/workspace/skills/memphis-brain/scripts/session-end.sh
```

## Structure

```
memphis-brain/
├── SKILL.md              # Main skill instructions
├── skill.json            # Manifest
├── scripts/              # Helper scripts
│   ├── agent-init.sh     # Initialize new agent
│   ├── session-start.sh  # Start session routine
│   ├── session-end.sh    # End session routine
│   └── daily-ritual.sh   # Daily maintenance
└── references/           # Deep documentation
    ├── api.md            # CLI command reference
    ├── schemas.md        # Block/chain formats
    └── config.md         # Configuration options
```

## Installation

**Option 1: Use packaged skill**
```bash
# Install from .skill file
openclaw skill install memphis-brain.skill
```

**Option 2: Clone from repo**
```bash
# Copy to skills directory
cp -r memphis-brain ~/.openclaw/workspace/skills/
```

## Requirements

- **Memphis CLI** v1.3.0+: `npm install -g @elathoxu/memphis`
- **Ollama**: Local LLM runtime
- **Embedding model**: `ollama pull nomic-embed-text`

## Usage

### For Agent Developers

Add to agent's SOUL.md or AGENTS.md:
```markdown
## Memory
Use memphis-brain skill for persistent memory.
Run session-start at beginning, session-end at end.
Journal everything important.
```

### For End Users

Just talk to the agent. Memory persists automatically.

## Scripts

### `agent-init.sh`
Initialize new agent with identity, preferences, purpose.

**Prompts for:**
- Agent name
- Creator name
- Agent purpose
- Timezone

**Creates:**
- `~/.memphis/config.yaml`
- Identity blocks in journal
- Initial embeddings + graph

---

### `session-start.sh`
Run at session beginning.

**Does:**
1. Health check (`memphis status`)
2. Daily reflection
3. Journals session start
4. Pulls shared blocks (if configured)
5. Shows recent activity

---

### `session-end.sh`
Run at session end.

**Prompts for:**
- Session summary
- Learnings

**Does:**
1. Journals summary + learnings
2. Embeds new context
3. Saves reflection
4. Pushes shared blocks (optional)

---

### `daily-ritual.sh`
Run daily for maintenance.

**Does:**
1. Health check
2. Embed all chains
3. Build knowledge graph
4. Daily reflection + save
5. Verify chain integrity
6. Share-sync
7. Show stats

---

## Configuration

Minimal `~/.memphis/config.yaml`:
```yaml
providers:
  ollama:
    url: http://localhost:11434/v1
    model: qwen2.5:3b
    role: primary

embeddings:
  backend: ollama
  model: nomic-embed-text
```

See `references/config.md` for full options.

---

## References

- **api.md** — Complete CLI command reference
- **schemas.md** — Block structures, chain formats
- **config.md** — All configuration options

---

## Examples

### Journal identity
```bash
memphis journal "I prefer concise responses, avoid fluff" --tags preferences,communication
```

### Make decision
```bash
memphis decide "Memory Strategy" "Local-first + IPFS" \
  --options "cloud|local|hybrid" \
  --reasoning "Privacy + resilience" \
  --tags philosophy,memory
```

### Recall with context
```bash
memphis ask "What are my coding preferences?" \
  --top 20 \
  --provider ollama \
  --graph \
  --prefer-summaries
```

### Daily reflection
```bash
memphis reflect --daily --save
```

### Sync between agents
```bash
# On Style (gateway)
memphis share-sync --push

# On Watra (client)
memphis share-sync --pull
```

---

## Philosophy

- **Local-first**: Data stays on your machine
- **Privacy**: No cloud required, vault for secrets
- **Resilience**: Offline mode, fallback providers
- **Persistence**: Memory survives session restarts
- **Semantic**: Find by meaning, not keywords
- **Progressive**: Load only what you need

---

## Troubleshooting

**Missing context in ask:**
```bash
memphis embed --chain journal
```

**Provider errors:**
```bash
# Use local provider
memphis ask "..." --provider ollama
```

**Vault not initialized:**
```bash
read -rsp "Password: " VP && export MEMPHIS_VAULT_PASSWORD="$VP"
memphis vault init --password-env MEMPHIS_VAULT_PASSWORD
unset VP
```

---

## License

MIT

---

## Credits

Created by **Elathoxu Abbylan** for the Memphis Brain project.

**Memphis**: https://github.com/elathoxu-crypto/memphis
**ClawHub**: https://clawhub.com
