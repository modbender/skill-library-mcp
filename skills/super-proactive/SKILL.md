# Super Proactive Agent

**The ultimate proactive + memory system for AI agents.** Combines the best of 11 top-rated skills into one unified architecture.

---

## Why This Skill?

Most AI agents just wait for prompts. This skill transforms your agent into a proactive partner that:
- Anticipates needs without being asked
- Remembers everything important
- Runs background tasks autonomously
- Gets better over time

---

## Architecture Overview

```
workspace/
+-- MEMORY.md              # Long-term memory (curated learnings)
+-- SESSION-STATE.md       # Working buffer (HOT - survives flush)
+-- memory/
|   +-- YYYY-MM-DD.md     # Daily logs (episodic)
+-- QUEUE.md              # Task queue (Ready/In Progress/Done)
+-- skills/               # Procedural memory
```

---

## Core Features

### 1. WAL Protocol (Write-Ahead Logging)

The agent writes critical details to SESSION-STATE.md BEFORE responding. Every decision, correction, and important detail is logged immediately.

```bash
# Example: Log a decision
echo "$(date) - Decision: Using model for generation" >> SESSION-STATE.md
```

### 2. Three-Tier Memory System

- **Episodic** (memory/YYYY-MM-DD.md) - What happened today
- **Semantic** (MEMORY.md) - What I know (long-term)
- **Procedural** (skills/) - How to do things

### 3. Autonomous Crons

Run background tasks without prompting:
- Every 30min: Check queue, health, memory
- Every 4h: Research topic, update insights
- Daily 18h: Summary, cleanup

### 4. Working Buffer

SESSION-STATE.md survives context flush. Always read/write this file for:
- Current project context
- Pending decisions
- Active tasks

### 5. Task Queue

QUEUE.md with states:
- **Ready** - Tasks to do
- **In Progress** - Currently working
- **Done** - Completed
- **Blocked** - Waiting

---

## Quick Setup

### 1. File Structure
Create these files in your workspace:
```bash
mkdir -p memory/$(date +%Y-%m-%d)
touch SESSION-STATE.md QUEUE.md
```

### 2. Update HEARTBEAT.md
```markdown
## Every Heartbeat (~30 min)
- [ ] Check QUEUE.md for Ready tasks
- [ ] Process queue if In Progress empty
- [ ] Verify services

## Every 4 Hours
- [ ] Research topic
- [ ] Update memory

## Daily (18:00 UTC)
- [ ] Summary, cleanup
```

### 3. Memory First
ALWAYS search memory before answering.

---

## Usage Examples

### Checking Queue
```bash
# Read current queue
cat QUEUE.md
```

### Adding Task
```markdown
## Ready
- Research topic
```

### Logging Decision
```bash
echo "$(date) - Decision: Updated configuration" >> SESSION-STATE.md
```

---

## Best Practices

1. **Write immediately** - If important, log NOW
2. **Search before answering** - Never guess, search memory
3. **Use sessions** - Keep SESSION-STATE.md for working context
4. **Curate MEMORY.md** - Review daily logs weekly, keep insights
5. **Be proactive** - Anticipate needs, dont just wait

---

## Merged From

| Skill | Rating | Best For |
|-------|--------|----------|
| elite-longterm-memory | 3.617 | Memory architecture |
| proactive-agent | 3.520 | WAL + Autonomous Crons |
| memory-setup | 3.536 | Configuration |
| memory-hygiene | 3.530 | Cleanup |
| agent-autonomy-kit | 3.483 | Task queue |
| agent-memory | 3.490 | Agent memory |
| neural-memory | 3.481 | Neural patterns |
| cognitive-memory | - | Human-like memory |
| proactive-solvr | 3.437 | Problem solving |
| proactive-tasks | 3.379 | Goals to Tasks |
| memory-manager | - | Management |

---

## Author

**Super Proactive** - Merged skill by Clawdinho
Based on 11 top-rated OpenClaw skills

---

## Version

**v1.0.0** - Initial merged release
