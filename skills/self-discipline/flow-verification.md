# Flow Verification — Self Discipline

The critical step: **Will the next agent actually see this instruction?**

## Why This Matters

Writing an instruction is not the same as the instruction being followed.

```
┌─────────────────────────────────────────────────────────────┐
│                    THE ILLUSION OF FIXING                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ❌ What usually happens:                                  │
│                                                             │
│   Agent makes mistake                                       │
│        ↓                                                    │
│   "I'll write this in memory.md"                           │
│        ↓                                                    │
│   Writes rule somewhere                                     │
│        ↓                                                    │
│   Feels resolved                                            │
│        ↓                                                    │
│   NEW SESSION STARTS                                        │
│        ↓                                                    │
│   That file is never loaded                                 │
│        ↓                                                    │
│   Same mistake happens                                      │
│                                                             │
│   ✅ What should happen:                                    │
│                                                             │
│   Agent makes mistake                                       │
│        ↓                                                    │
│   VERIFY: What files are ACTUALLY loaded?                   │
│        ↓                                                    │
│   VERIFY: Is the target file in that list?                  │
│        ↓                                                    │
│   If NO: Add to loaded file OR add reference to it          │
│        ↓                                                    │
│   CONFIRM: Instruction now reachable                        │
│        ↓                                                    │
│   Actually resolved                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## The Agent Load Path

Every agent session starts with a specific set of files. Map this exactly.

### Typical Load Path (OpenClaw/Claude)

```
1. System prompt (built-in, not editable)
     ↓
2. Project context files (injected)
   - AGENTS.md (if exists)
   - SOUL.md (if exists)
   - USER.md (if exists)
   - MEMORY.md (if exists)
   - TOOLS.md (if exists)
   - IDENTITY.md (if exists)
   - HEARTBEAT.md (if exists)
     ↓
3. Session-specific context
   - memory/groups.md (for group sessions)
   - memory/YYYY-MM-DD.md (today + yesterday)
     ↓
4. Skill files (if skill activated)
   - SKILL.md
   - Referenced files from SKILL.md
     ↓
5. Conversation history
```

### Finding Your Load Path

Ask yourself:
1. What files appear in "Project Context" at session start?
2. What files does the session's AGENTS.md tell it to read?
3. What additional files are referenced in those files?

**This is the ONLY path that matters. Everything else is invisible.**

## Verification Protocol

### Step 1: List the Load Path

```markdown
## Load Path for [this agent/session type]

Files loaded at start:
1. [file1.md]
2. [file2.md]
3. [file3.md]

Files referenced from those:
4. [file4.md] (referenced in file1.md)
5. [file5.md] (referenced in file2.md)

Files NOT in path (will NOT be seen):
- memory/random-notes.md
- archive/*.md
- etc.
```

### Step 2: Check Instruction Location

Where is the instruction currently written?

| Location | In Load Path? | Action |
|----------|---------------|--------|
| AGENTS.md | ✅ Yes | Verify it's not buried |
| MEMORY.md | ✅ Yes | Verify it's not buried |
| memory/random.md | ❌ No | MOVE or ADD REFERENCE |
| skill-specific file | ⚠️ Only if skill active | Add to AGENTS.md if critical |

### Step 3: Ensure Reachability

If instruction is NOT in load path:

**Option A: Move the instruction**
- Copy to a file that IS in the load path
- Delete from old location (avoid duplication)

**Option B: Add a reference**
```markdown
# In AGENTS.md (which IS loaded)

## Critical Rules
See `memory/critical-rules.md` for rules that must ALWAYS be followed.
Read this file at the start of every session.
```

**Option C: Add to AGENTS.md directly**
For critical rules, the safest is adding directly to AGENTS.md.

### Step 4: Verify Not Buried

Even if in load path, check:
- Is it near the top of the file?
- Is it under a clear heading?
- Will context limits cut it off?

If buried:
- Move to top of file
- Create dedicated section: `## ⚠️ CRITICAL RULES (READ FIRST)`
- Consider separate file with explicit reference

## Verification Checklist

```markdown
## Flow Verification — [Rule/Instruction]

### 1. Current Location
- File: [path]
- Line: [number]
- Section: [heading]

### 2. Load Path Analysis
Agent type: [main/group/sub-agent]
Files loaded:
- [ ] AGENTS.md
- [ ] MEMORY.md
- [ ] [others]

Instruction file in load path: YES / NO

### 3. Reachability
- [ ] File is loaded at session start
- [ ] Instruction is in first 50 lines (not buried)
- [ ] No contradicting instructions elsewhere
- [ ] Clear heading makes it findable

### 4. Fix Applied (if needed)
- [ ] Moved to: [new location]
- [ ] Reference added in: [file]
- [ ] Backup created: [path]

### 5. Confirmation
- [ ] Next session test: instruction was followed
```

## Common Mistakes

| Mistake | Why It Fails | Fix |
|---------|--------------|-----|
| Writing in `memory/notes.md` | Not in load path | Use AGENTS.md or MEMORY.md |
| Adding to bottom of long file | Context overflow | Move to top |
| Creating new file without reference | Nobody knows to read it | Add reference in loaded file |
| Assuming skills are always active | Skills load conditionally | Put critical rules in AGENTS.md |
| Relying on heartbeat to read | Heartbeat is periodic, not session-start | Use always-loaded files |

## The Golden Rule

**If you can't trace the exact path from session start to your instruction, the instruction doesn't exist.**
