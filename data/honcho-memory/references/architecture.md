# Honcho Memory Architecture

## Data Flow

```
Agent conversations → Feed script → Honcho Sessions → Neuromancer (reasoning) → Peer Representations
                                                                                        ↓
Agent session start ← Context files ← Generate script ← Query/Context API ← Reasoned understanding
                                                                                        ↓
Mid-conversation   ← Direct answer  ← Query script    ← peer.chat()       ← On-demand recall
```

## Integration Patterns

### Pattern 1: Hourly Cron (Recommended)

Feed new messages + generate context files on a schedule:

```
Feed (write): Read new transcript lines → attribute to peers → add_messages()
Generate (read): Pull representations + summaries → write HONCHO-CONTEXT.md files
```

Context files load at session start and survive compaction.

### Pattern 2: On-Demand Query

Agent runs query script mid-conversation when it doesn't remember something:

```
Agent: "I don't know what CoShip is. Let me check."
→ python3 scripts/query.py "What is CoShip?" --peer j
→ "CoShip is a revenue-sharing marketplace for SaaS builders..."
```

### Pattern 3: Session Context API

Pull context directly into the prompt at session start:

```python
session = honcho.session("agent-main")
ctx = session.context(tokens=3000)
# Inject ctx.summary + ctx.peer_representation into system prompt
```

## File Structure

```
HONCHO-CONTEXT.md (workspace root)    — Shared context, all agents load this
agents/{name}/HONCHO-CONTEXT.md       — Agent-specific context
~/.config/honcho/credentials.json     — API key + workspace config
~/.config/honcho/feed-state.json      — Sync position tracker (per-transcript)
```

## What Honcho Learns

From raw conversation data, [[research/honcho-integration-plan|Honcho]]'s Neuromancer model produces:

- **Deductive observations**: Logical conclusions from explicit statements
- **Inductive observations**: Patterns detected across multiple conversations
- **Peer representations**: Synthesized understanding of each entity

Example: From 975 messages, [[research/honcho-integration-plan|Honcho]] deduced J's editorial control pattern (delete → feedback → revise), the multi-persona platform separation, tiered quality standards based on bounty value, and the approval workflow logic.

## Replacing Static Memory Files

| Before (files) | After ([[research/honcho-integration-plan|Honcho]]) |
|---|---|
| MEMORY.md (manually curated) | Peer representations (auto-reasoned) |
| Daily notes (append-only logs) | Session messages (properly attributed) |
| Entity files (manual summaries) | Peer entities (evolving understanding) |
| memory_search (embedding lookup) | peer.chat() (reasoned retrieval) |

Keep: ACTIVE.md, STANDING-ORDERS.md, SOUL.md, [[projects/axel-command/CORTEX-VISION|Cortex]] graph
