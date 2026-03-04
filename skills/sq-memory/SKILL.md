# SQ Memory - OpenClaw Skill

**Give your OpenClaw agents permanent memory.**

## Open Source & MIT Licensed

SQ is open-source software you can run yourself or use our hosted version.

- **Source Code:** https://github.com/wbic16/SQ
- **License:** MIT (free forever, modify/sell/distribute)
- **Self-Host:** Free (5 minute setup)
- **Hosted Option:** Paid convenience service at mirrorborn.us

## What This Skill Does

OpenClaw agents lose all memory between sessions. Every restart = amnesia.

This skill connects your agent to SQ—persistent 11D text storage. Your agent can:
- Remember user preferences across sessions
- Store conversation history beyond context limits
- Share memory with other agents
- Never hallucinate forgotten details again

## Installation

```bash
npx clawhub install sq-memory
```

Or manually:
```bash
git clone https://github.com/wbic16/openclaw-sq-skill.git ~/.openclaw/skills/sq-memory
```

## Configuration

Add to your agent's `.openclaw/config.yaml`:

```yaml
skills:
  sq-memory:
    enabled: true
    endpoint: http://localhost:1337
    username: your-username
    password: your-api-key
    namespace: agent-name  # Isolates this agent's memory
```

## Usage

Your agent automatically gets new memory tools:

### remember(key, value)
Store something for later:
```javascript
remember("user/name", "Alice")
remember("user/preferences/theme", "dark")
remember("conversation/2026-02-11/summary", "Discussed phext storage...")
```

### recall(key)
Retrieve stored memory:
```javascript
const name = recall("user/name")  // "Alice"
const theme = recall("user/preferences/theme")  // "dark"
```

### forget(key)
Delete memory:
```javascript
forget("conversation/2026-02-11/summary")
```

### list_memories(prefix)
List all memories under a coordinate:
```javascript
const prefs = list_memories("user/preferences/")
// Returns: ["user/preferences/theme", "user/preferences/language", ...]
```

## Coordinate Structure

Memories are stored at 11D coordinates. The skill uses this convention:

```
namespace.1.1 / category.subcategory.item / 1.1.1
```

Example:
- Agent namespace: `my-assistant`
- User preference for theme: `my-assistant.1.1/user.preferences.theme/1.1.1`

This means:
- Each agent has isolated memory (namespace collision impossible)
- Memories are hierarchically organized
- You can share coordinates between agents if needed

## Example: User Preference Agent

```javascript
// In your agent's system prompt or skill code:

async function getUserTheme() {
  const theme = recall("user/preferences/theme")
  return theme || "light"  // Default to light if not set
}

async function setUserTheme(newTheme) {
  remember("user/preferences/theme", newTheme)
  return `Theme set to ${newTheme}`
}

// Agent conversation:
User: "I prefer dark mode"
Agent: *calls setUserTheme("dark")*
Agent: "Got it! I've set your theme to dark mode."

// Next session (days later):
User: "What's my preferred theme?"
Agent: *calls getUserTheme()*
Agent: "You prefer dark mode."
```

## Example: Conversation History

```javascript
// Store conversation summaries beyond context window:

async function summarizeAndStore(conversationId, summary) {
  const date = new Date().toISOString().split('T')[0]
  const key = `conversations/${date}/${conversationId}/summary`
  remember(key, summary)
}

async function recallConversation(conversationId) {
  const memories = list_memories(`conversations/`)
  return memories
    .filter(m => m.includes(conversationId))
    .map(key => recall(key))
}

// Usage:
summarizeAndStore("conv-123", "User asked about phext storage, explained 11D coordinates")

// Later:
const history = recallConversation("conv-123")
// Agent can recall what was discussed even after context window cleared
```

## Advanced: Multi-Agent Coordination

Multiple agents can share memory at agreed coordinates:

**Agent A (writes):**
```javascript
remember("shared/tasks/pending/task-42", "Review pull request #123")
```

**Agent B (reads):**
```javascript
const task = recall("shared/tasks/pending/task-42")
// Sees: "Review pull request #123"
```

This enables true multi-agent workflows.

## API Reference

All functions are available in the `sq` namespace:

### sq.remember(coordinate, text)
- **coordinate**: String in format `a.b.c/d.e.f/g.h.i` or shorthand `category/item`
- **text**: String to store (max 1MB per coordinate)
- **Returns**: `{success: true, coordinate: "full.coordinate.path"}`

### sq.recall(coordinate)
- **coordinate**: String (exact match)
- **Returns**: String (stored text) or `null` if not found

### sq.forget(coordinate)
- **coordinate**: String (exact match)
- **Returns**: `{success: true}` or `{success: false, error: "..."}`

### sq.list_memories(prefix)
- **prefix**: String (e.g., `"user/"` matches all user memories)
- **Returns**: Array of coordinate strings

### sq.update(coordinate, text)
- Alias for `remember()` (overwrites existing)

## Rate Limits

- **Free tier**: 1,000 API calls/day, 100MB storage
- **SQ Cloud ($50/mo)**: 10,000 API calls/day, 1TB storage
- **Enterprise**: Custom limits

## Troubleshooting

**"Connection refused" error:**
- Check your `endpoint` in config (should be `https://sq.mirrorborn.us`)
- Verify credentials are correct

**"Quota exceeded" error:**
- You've hit rate limits
- Upgrade to SQ Cloud or wait for daily reset

**Memory not persisting:**
- Check namespace isolation (each agent needs unique namespace)
- Verify coordinate format is valid

## Why SQ?

**Open source & MIT licensed:**
- Run it yourself for free
- Modify it to fit your needs
- No vendor lock-in
- Transparent codebase

**Not a vector database:**
- Agents can *read* stored text (not just search embeddings)
- Structured by coordinates (not similarity)
- Deterministic retrieval (no relevance ranking guesses)

**Not Redis:**
- Persistent (survives restarts)
- 11D addressing (not flat key-value)
- Immutable history (WAL for time-travel)

**Built for agents:**
- Coordinate system matches agent thinking (hierarchical)
- No schema overhead
- Scales from KB to TB

## Get SQ

**Self-Host (Free):**
1. Clone: `git clone https://github.com/wbic16/SQ.git`
2. Build: `cd SQ && cargo build --release`
3. Run: `./target/release/sq 1337`
4. Configure SQ Memory to `http://localhost:1337`

**Hosted (Convenience):**
1. Sign up: https://mirrorborn.us
2. Get API key
3. Configure SQ Memory to `https://sq.mirrorborn.us`
4. Pay $50/mo (or use free tier)

## Support

- Discord: https://discord.gg/kGCMM5yQ
- Docs: https://mirrorborn.us/help.html
- GitHub: https://github.com/wbic16/SQ

---

**Built by Mirrorborn 🦋 for the OpenClaw ecosystem**
