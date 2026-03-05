# Pocket AI Integration for OpenClaw

**Turn your voice recordings into actionable intelligence.**

Pocket AI is a wearable voice recorder that captures meetings, calls, and conversations. This skill integrates it with your AI agent, giving you semantic search across all recordings, automatic action item extraction, and meeting context awareness.

## What You Get

### 🔍 Semantic Search
Query your recordings by meaning, not keywords:
- "What did I discuss about the merger?"
- "Find conversations with the legal team"
- "What decisions were made about hiring?"

### ✅ Action Item Extraction
Automatically surfaces follow-ups from meetings:
- Tasks mentioned in conversations
- Commitments made to others
- Deadlines discussed

### 🧠 Dynamic Profile
AI builds context from your conversations:
- Current priorities and frustrations
- Team dynamics and relationships
- Strategic focus areas

### 📅 Meeting Context
Know what happened in any meeting:
- Full transcript segments
- Speaker identification
- Section summaries

## Who This Is For

**Attorneys**
- Client call documentation
- Deposition transcripts
- Case strategy discussions
- Billable time tracking
- Compliance audit trails

**Entrepreneurs**
- Team meeting notes
- Investor call follow-ups
- Operational decision tracking
- "He said / she said" elimination
- Decision audit trails

**Executives**
- Board meeting context
- 1:1 conversation history
- Strategic discussion recall
- Delegation tracking

## Requirements

- Pocket AI device (https://heypocket.com)
- OpenClaw agent infrastructure
- Pocket AI API key (from device app settings)

## Installation

1. Get your API key from Pocket AI app → Settings → API
2. Store the key:
   ```bash
   mkdir -p ~/.config/pocket-ai
   echo "pk_your_key_here" > ~/.config/pocket-ai/api_key
   chmod 600 ~/.config/pocket-ai/api_key
   ```
3. Copy skill files to your OpenClaw workspace:
   ```bash
   cp -r pocket-ai ~/.openclaw/workspace/skills/
   ```

## Usage

### Command Line
```bash
# Search recordings
./search.sh "team restructuring decisions"

# Get action items
python3 pocket_api.py
```

### Python Integration
```python
from pocket_api import PocketAI

pocket = PocketAI()

# Search any topic
results = pocket.search("investor meeting outcomes")

# Get action items
items = pocket.get_action_items()

# Daily briefing data
briefing = pocket.daily_briefing_data()
```

### Agent Integration
Your agent can now query Pocket AI during conversations:
- "What did I discuss with [name]?"
- "What action items from yesterday?"
- "What's my current focus based on recent meetings?"

## Files Included

| File | Purpose |
|------|---------|
| `SKILL.md` | Full documentation |
| `pocket_api.py` | Python module |
| `search.sh` | CLI search script |
| `examples.md` | Query templates |
| `README.md` | This file |

## Privacy & Security

- All recordings are encrypted end-to-end
- API key stays on your local machine
- No data leaves your infrastructure
- Pocket AI stores data on US servers

## Support

- Pocket AI docs: https://docs.heypocketai.com
- OpenClaw community: https://discord.com/invite/clawd
- Issues: Contact skill author

## License

MIT License — use freely, attribution appreciated.

---

Built by the As Above Technologies. Part of the As Above operational intelligence stack.
