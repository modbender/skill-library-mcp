# Skill Update Feedback Loop - Meta Enforcement

**The Meta-Problem:** Enforcement improvements don't automatically flow back to skills.

**Example:**
1. Project A builds `.deployment-check.sh` to prevent deployment gaps
2. Works great in Project A
3. **Gap:** Project B, C, D don't know about it
4. **Root cause:** Improvement stayed in Project A, didn't flow back to shared skill

**The Loop:**
```
Project improvement → [Manual remember?] → Update skill → Other projects benefit
                              ↑
                         Often breaks here
```

---

## Solution: Automatic Feedback Loop

**Make it impossible to forget:**

```
Project improvement → [Auto-detect] → Create task → [Semi-auto commit] → Skill updated
                           ↓
                    No memory required
```

**Components:**

1. **Git post-commit hook** - Runs after every commit
2. **detect-enforcement-improvement.sh** - Scans for enforcement patterns
3. **auto-commit-skill-updates.sh** - Semi-automatic commit with confirmation
4. **.pending-skill-updates.txt** - Task queue

---

## How It Works

### Phase 1: Detection (Automatic)

**Trigger:** Every `git commit`

**Process:**
```bash
commit → .git/hooks/post-commit
      → scripts/detect-enforcement-improvement.sh
      → Scans changed files for patterns:
         - *.deployment-check.sh
         - *DEPLOYMENT-CHECKLIST.md
         - *pre-commit*, *post-create*
         - *enforcement*, *guardrails*
      → If found → Creates task in .pending-skill-updates.txt
```

**Task format:**
```
---
Date: 2026-02-02 21:45 UTC
Commit: abc123
Skill: agent-guardrails
Files: project/.deployment-check.sh

Action needed:
1. Review improvement
2. Extract reusable parts
3. Update skills/agent-guardrails/
4. Commit
---
```

### Phase 2: Update (Manual)

**Human does:**
1. Reviews the improvement
2. Extracts reusable patterns/scripts
3. Updates skill files (scripts/, references/, SKILL.md)
4. Tests if needed

**Why manual:**
- Judgment needed on what's reusable
- Some improvements are project-specific
- Quality control

### Phase 3: Commit (Semi-Automatic)

**Human runs:**
```bash
bash scripts/auto-commit-skill-updates.sh
```

**Script does:**
1. Checks for uncommitted changes in `skills/`
2. Parses `.pending-skill-updates.txt` to get context
3. Generates commit message automatically
4. **Asks for confirmation** (y/N)
5. Commits if approved
6. Archives task
7. Clears pending tasks file

**Safety:**
- ✅ Shows what will be committed
- ✅ Confirmation step
- ✅ Auto-generated commit message includes context
- ✅ Can abort safely

---

## Installation

### In a Project

```bash
cd your-project/
bash /path/to/agent-guardrails/scripts/install-skill-feedback-loop.sh .
```

This installs:
- Detection script
- Auto-commit script
- Git post-commit hook
- Workflow documentation

### In Agent Guardrails Itself

Same process - the system is self-hosting:
```bash
cd agent-guardrails/
bash scripts/install-skill-feedback-loop.sh .
```

**Bootstrapping note:** First installation needs manual setup since the system doesn't exist yet.

---

## Maintenance

### Check Pending Tasks

```bash
cat .pending-skill-updates.txt
```

### View Archive

```bash
cat .skill-updates-archive.txt
```

### Update Detection Patterns

Edit `scripts/detect-enforcement-improvement.sh`:
```bash
ENFORCEMENT_PATTERNS=(
    "\.deployment-check\.sh"
    "your-new-pattern"
)
```

---

## Benefits

**Without feedback loop:**
- ❌ Improvements stay siloed
- ❌ Rely on human memory
- ❌ Skills become stale
- ❌ Knowledge doesn't compound

**With feedback loop:**
- ✅ Can't forget (mechanical reminder)
- ✅ Improvements automatically tracked
- ✅ Skills stay current
- ✅ Knowledge compounds across projects

---

## Dogfooding

**This system was built to solve its own problem:**

1. We built deployment verification (project-level)
2. Almost forgot to update agent-guardrails
3. User pointed out the gap
4. We built automatic feedback loop
5. **The feedback loop itself needed to be added to agent-guardrails**
6. Bootstrapping: Manual first time, automatic after

**Meta-meta note:** If we improve this feedback loop, the loop will detect its own improvement!

---

## Future Enhancements

### Phase 4: Fully Automatic (Vision)

Replace manual Phase 2 with AI:
```bash
# AI agent does:
1. Reads pending task
2. Analyzes changed files
3. Extracts reusable patterns automatically
4. Generates skill updates
5. Runs tests
6. If tests pass → Auto-commits
7. If tests fail → Creates manual review task
```

**Requirements:**
- AI capable of code analysis and generation
- Comprehensive test suite for skills
- Safety rails for review

---

## TL;DR

**Problem:** Enforcement improvements don't flow back to skills → knowledge siloed

**Solution:** Automatic detection + semi-automatic commit → can't forget

**How:** Git hook detects → Creates task → Human updates → Script commits

**Result:** Every improvement becomes reusable knowledge

**This is meta-enforcement:** Enforcing that enforcement improvements are preserved and shared.
