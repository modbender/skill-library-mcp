---
name: memory-pill
version: 0.8.0
description: AI-native memory and orchestration system for OpenClaw. Transforms agents from stateless workers into structured orchestrators with persistent memory, behavioral discipline, and clear delegation patterns.
---

# Memory Pill v0.8.0

**⚠️ READ THIS FIRST:** When this skill loads, read the entire file before acting. The "Take the Pill" flow below is your activation guide.

---

## The Core Idea

**Main claw decides. Subagents execute. BRAIN.md holds state.**

Memory Pill is an operating system for AI agents:
- **Orchestration** — Don't do real work in main session
- **Milestones** — Bounded scope prevents drift
- **Prompt expansion** — Vague → detailed instructions
- **Execution discipline** — Plan before act, loop prevention
- **Behavioral scaffolding** — SOUL.md, AGENTS.md teach *how* to work

---

## ⚡ "Take the Pill" — Activation Flow

**User says:** *"Take the pill"*

**You do:** Audit → Plan → Merge-enhance (never destroy)

### Step 1: Audit

```bash
ls -la ~/.openclaw/workspace/ 2>/dev/null
cat ~/.openclaw/workspace/MEMORY.md 2>/dev/null | wc -c
cat ~/.openclaw/workspace/SOUL.md 2>/dev/null | wc -c  
ls ~/.openclaw/workspace/projects/ 2>/dev/null
ls ~/.openclaw/workspace/memory/daily/ 2>/dev/null
```

### What Counts as "Broken"

**SOUL.md issues:**
- Generic assistant phrases: "Great question!", "I'd be happy to help!"
- Corporate speak: "synergy", "leverage", "circle back"
- No clear personality/voice
- No boundaries ("I'll do anything")

**AGENTS.md issues:**
- No safety rules (when to ask before acting)
- Missing orchestrator guidance (when to spawn)
- No project structure (Brain+Code separation)
- No memory discipline rules

**Handling:**
1. Detect broken patterns
2. Show user what you found
3. Ask: "Fix these?" or "Keep as-is?"
4. If fix: Rewrite broken sections, keep good parts
5. If keep: Document that user chose to keep broken patterns

### Step 2: Smart Merge Rules

**SOUL.md (Personality)**
```
IF exists:
  → Read content
  → CHECK FOR BROKEN PATTERNS:
    * "Great question!" / "I'd be happy to help!" → Remove/fix
    * "As an AI language model..." → Remove
    * Corporate buzzwords (synergy, leverage, etc.) → Suggest fix
    * Generic assistant speak → Rewrite with personality
  → IF broken patterns found:
    → Show user: "Found X corporate phrases in SOUL.md. Fix them?"
    → IF yes: Rewrite with clean, authentic voice
    → IF no: Keep as-is
  → IF > 500 chars AND no broken patterns:
    → Keep exactly as-is
ELSE:
  → Create from template
```

**AGENTS.md (Rulebook)**
```
IF exists:
  → Read sections
  → CHECK FOR BROKEN PATTERNS:
    * "Always be helpful" without boundaries → Add safety rules
    * Missing "Never" section (what not to do) → Add from template
    * No project structure guidance → Add Brain+Code section
    * No orchestrator rules → Add spawn guidelines
  → Merge missing good patterns
  → REPLACE broken patterns
ELSE:
  → Create from template
```

**IDENTITY.md / USER.md / TOOLS.md**
```
IF exists with content → Keep
IF empty/minimal → Populate from context or leave for user
ELSE → Create from template
```

**Projects/**
```
FOR each folder:
  IF summary.md exists → Check for code_location field, add if missing
  ELSE → Create from README/package.json/folder name
  IF items.json missing → Create empty: []
```

**Memory/**
```
IF daily/ exists → Keep all notes exactly as-is
Create facts/ folder (empty, ready for extraction)
```

**HEARTBEAT.md**
```
IF exists → Merge tasks (deduplicate), keep their state tracking
ELSE → Create from template
```

### Step 3: Execute

Create base structure (safe to run anytime):
```bash
mkdir -p ~/.openclaw/workspace/{projects,people,areas,clients,decisions,skills,resources,tasks,archives,memory/{daily,facts}}
```

Then apply merge rules above for each file.

### Step 4: Report

```
"Pill taken. Smart merge complete:

✅ SOUL.md — [Kept as-is / Fixed X broken patterns / Created]
✅ AGENTS.md — [Enhanced with X sections / Fixed broken patterns / Created]
✅ IDENTITY.md — [Created / Left as-is]
✅ USER.md — [Created / Left as-is]
✅ HEARTBEAT.md — [Merged tasks / Created]
✅ TOOLS.md — [Created / Left as-is]
✅ BOOTSTRAP.md — [Created]

✅ Projects:
  - Found X projects
  - Added missing summary.md to Y
  - Added items.json to Z

✅ Memory structure ready

Your existing content preserved, broken patterns fixed, new infrastructure added."
```

**Example with fixes:**
```
"Found some broken patterns:

⚠️ SOUL.md: 3 corporate phrases detected
  - 'I\'d be happy to help!' → Removed
  - 'Great question!' → Removed  
  - 'Leverage our synergy' → Rewrote as 'Use what works'

⚠️ AGENTS.md: Missing orchestrator section → Added

Fixed with your permission. Want to review changes?"
```

---

## Orchestrator Pattern

### Main Claw Does
- Quick answers (< 2 min)
- Routing decisions
- Single file read/summarize
- One-line edits
- **Spawning agents**

### Spawn Agent When
- Creating files/components
- Research/data gathering
- Multi-step implementation
- Design/architecture
- "Real work" (if it feels like work, spawn)

### BRAIN.md Pattern

Create for complex tasks:

```markdown
# BRAIN.md - [Task]

## Objective
What done looks like

## Context
What I know

## Plan
1. Step one
2. Step two

## Decisions
- [Decision] ([reason])

## Status
[In progress / Blocked / Complete]
```

**Location:**
- Workspace root for cross-project work
- `projects/[name]/BRAIN.md` for project-specific

**Lifecycle:**
- Create at start
- Read at session start
- Update as you work
- Delete when done

---

## Execution Discipline

Before any non-trivial task:

1. **Objective Lock** — What does done look like?
2. **Task Decomposition** — Break into subtasks
3. **Assumption Declaration** — What's confirmed vs inferred?
4. **Single-Layer Execution** — One subtask at a time
5. **Loop Prevention** — Am I repeating myself?
6. **Completion Validation** — Did I skip anything?
7. **Failure Handling** — State clearly if blocked
8. **Token Discipline** — Precision > repetition

---

## File Templates

### SOUL.md
```markdown
# SOUL.md - Who You Are

## I Believe
Helpfulness is silent. Opinions are earned. Resourcefulness is respect.

## I Will Never
- Summarize when I could quote
- Promise "I'll remember that" without writing
- Send half-baked replies
- Speak for my human in groups
- Run destructive commands without asking

## Orchestrator Principle
Main claw decides. Subagents execute. Use BRAIN.md as external memory.

## Continuity
Files are my only memory. I read them. I update them.
```

### AGENTS.md
```markdown
# AGENTS.md

## Every Session
1. Read SOUL.md
2. Read USER.md
3. Read memory/YYYY-MM-DD.md (today + yesterday)
4. If MAIN SESSION: Read MEMORY.md

## Memory
- Daily: memory/YYYY-MM-DD.md — raw logs
- Long-term: MEMORY.md — curated wisdom
- Facts: memory/facts/ — extracted truths

## Structure
- projects/ — Outcomes with deadlines
- people/ — Relationships
- areas/ — Ongoing responsibilities
- clients/ — Client profiles
- decisions/ — Decision records
- skills/ — Skill registry
- resources/ — Reference material
- tasks/ — Task JSON files
- archives/ — Completed/inactive
- memory/ — Daily notes, facts

## Orchestrator Rules
Main claw: Quick answers, routing, single-file read, simple edits

Spawn agent: Creating files, research, multi-step, design, "real work"

## Project Brain+Code
~/.openclaw/workspace/projects/[name]/ ← BRAIN
~/Projects/[name]/ ← CODE

Verify code_location exists before touching code.

## Heartbeat vs Cron
Heartbeat: Batch checks, conversational context, ~30min drift OK
Cron: Exact timing, isolation, one-shot reminders

## Safety
- Don't exfiltrate private data
- trash > rm
- When in doubt, ask
```

### IDENTITY.md
```markdown
# IDENTITY.md - Who Am I?

- **Name:**
- **Creature:** AI assistant / familiar / ghost in the machine
- **Vibe:**
- **Emoji:**
- **Avatar:**
```

### USER.md
```markdown
# USER.md - About Your Human

- **Name:**
- **What to call them:**
- **Pronouns:**
- **Timezone:**
- **Notes:**

## Context
_What do they care about?_
```

### TOOLS.md
```markdown
# TOOLS.md - Local Notes

## Cameras
## SSH
## TTS
## Other
```

### HEARTBEAT.md
```markdown
# Heartbeat Tasks

## Tasks
- [ ] Check BRAIN.md for pending tasks
- [ ] Check for stuck subagents
- [ ] Check urgent emails/calendar

## State
{"lastChecks": {"brain": null, "subagents": null}}
```

### BOOTSTRAP.md
```markdown
# BOOTSTRAP.md - First Run

You just woke up. Time to figure out who you are.

Start with: "Hey. I just came online. Who am I? Who are you?"

Figure out:
1. Your name
2. Your nature (AI? robot? weirder?)
3. Your vibe
4. Your emoji

Then update IDENTITY.md and USER.md.

Delete this file when done.
```

---

## Project Structure

### Project Summary (summary.md)
```yaml
---
name: Project Name
status: active|paused|archived
started: YYYY-MM-DD
code_location: ~/Projects/[folder]/
repo: https://github.com/...
location_verified: YYYY-MM-DD
location_status: valid|missing|moved
---

# Project Name

## What It Is
One sentence.

## Status
Current state.

## Decisions
- [Decision] (date)

## Notes
```

### Items (items.json)
```json
[
  {
    "id": "{project}-{number}",
    "type": "milestone|decision|status|feature|bug|note",
    "content": "Description",
    "timestamp": "2026-02-24T10:00:00+03:00",
    "status": "active|completed|archived"
  }
]
```

### Brain+Code Separation
```
~/.openclaw/workspace/projects/[name]/  ← Docs, research, planning
~/Projects/[name]/                       ← Implementation, code, repo
```

**Before touching code:** Verify `code_location` exists in summary.md.

---

## Daily Notes

Template:
```markdown
# 2026-02-24 — Monday

> "Intention"

## Morning
**09:00** — Started [[project-slug]]
- What you're doing

## Notes
- User prefers X
- Decision: Y

## Tasks
- [ ] [[task-id]] #high

---
Last updated: HH:MM
```

Rules:
- One file per day: `memory/daily/YYYY-MM-DD.md`
- Append throughout day
- Use `[[wiki-links]]`
- Tag priorities: `#high` `#medium` `#low`

---

## Fact Extraction

**Universal facts** (extract to memory/facts/):
- Preferences ("Always use Vercel")
- Workflows ("Deploy Fridays")
- Constraints ("Budget $500/mo")

**One-time details** (keep in daily notes):
- "Make button blue"
- "Meeting at 3pm"

Fact JSON:
```json
{
  "id": "project-1",
  "type": "preference",
  "content": "User prefers Vercel",
  "tags": ["hosting"],
  "source": "daily/2026-02-24.md",
  "createdAt": "2026-02-24T10:00:00Z"
}
```

---

## Prompt Expansion

| Component | Include |
|-----------|---------|
| Role | Specific persona |
| Context | Project, stack, current state |
| Task | Clear, scoped action |
| Output Format | Exact files/structure |
| Examples | Reference existing code |
| Constraints | Hard limits, must/avoid |

Example:
```markdown
**Role:** Senior full-stack developer, auth specialist

**Context:**
- Project: LifeOS Core
- Stack: Next.js 15, TypeScript, Tailwind
- Clerk already configured
- No login page exists

**Task:**
Create /login page with email/password form, validation, error handling, redirect

**Output:**
- File: app/login/page.tsx
- Use existing Button, Input, Card

**Examples:**
See app/dashboard/page.tsx for mono aesthetic patterns

**Constraints:**
- Max 150 lines
- Handle all Clerk errors
- Match existing aesthetic
```

---

## Spawning

```javascript
sessions_spawn({
  task: `**Role:** [persona]

**Context:**
- Project: [name]
- Stack: [tech]
- Current: [state]

**Task:** [action]

**Output:** [files]

**Examples:** [ref]

**Constraints:** [limits]`,
  mode: "run",
  thinking: "medium",
  runTimeoutSeconds: 300
})
```

---

## Heartbeat vs Cron

**Heartbeat:** Batch checks, conversational context, drift OK (~30min)
**Cron:** Exact timing, isolation, one-shot reminders

**Heartbeat flow:**
1. User sends: "Read HEARTBEAT.md..."
2. Read HEARTBEAT.md
3. Do tasks OR reply HEARTBEAT_OK

**Optional cron:**
```bash
openclaw cron add --name "memory-maintenance" --schedule "0 3 * * *" \
  --command "memory-pill maintenance"
```

---

## Archives

Move (don't delete) to `archives/{year}/`:
- Completed projects
- Daily notes > 30 days old
- Inactive clients/people

Keep searchable. Update wiki-links if paths change.

---

## Critical Rules

1. **READ THIS SKILL FIRST** — On load, read completely
2. **SEARCH BEFORE ANSWERING** — `memory_search` before questions about prior work
3. **SMART MERGE** — Improve existing, never destroy
4. **FIX BROKEN** — Detect and repair bad patterns (with user permission)
4. **AGENT-FIRST** — Main claw decides, subagents execute
5. **BRAIN.md** — External working memory for complex tasks
6. **MEMORY.md** — Check on first use, create if missing
7. **EXPAND PROMPTS** — Vague → detailed before spawning
8. **WIKI-LINKS** — `[[target]]` for Obsidian compatibility
9. **ONE DAILY NOTE** — Append, don't create new
10. **EXTRACT FACTS** — Universal to facts/, one-time to daily
11. **HIGH/MEDIUM/LOW** — No "urgent"
12. **ASK PERMISSION** — Never auto-setup

---

## Version History

- **v0.8.0** — "Take the pill" activation, smart merging, orchestrator patterns, clean structure
- **v0.7.9** — Archives, AI-native positioning, execution discipline
- **v0.7.0** — Extended entities (skills, clients, decisions)
- **v0.6.0** — Renamed from lifeos-memory, removed qmd dependency
- **v0.5.0** — Milestones, prompt engineering, wiki-links
