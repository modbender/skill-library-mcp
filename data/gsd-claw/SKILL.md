---
name: GSD Claw
description: Spec-driven development with built-in verification for substantial projects. Use when user wants to plan a project, scope a feature, build something with structure, or says "GSD mode", "let's plan", "scope out", "spec-driven". Workflow is Discuss → Plan → Execute → Verify. Based on glittercowboy's GSD system (MIT license). NOT for quick questions or simple tasks.
---

# GSD Claw

A spec-driven development system adapted for OpenClaw. Transforms vague ideas into verified, working implementations through structured workflows.

**Based on:** [glittercowboy/get-shit-done](https://github.com/glittercowboy/get-shit-done)  
**Original Author:** Lex Christopherson (@glittercowboy)  
**License:** MIT

## When to Use

Trigger this skill when user says:
- "Let's plan [project/feature]"
- "I want to build [something]"
- "Scope out [project name]"
- "GSD mode" or "spec-driven"
- "Plan and execute [task]"
- Any substantial project that needs structure

**NOT for:** Quick questions, simple tasks, chat conversations.

## Core Philosophy

From the original GSD:
> "The complexity is in the system, not in your workflow."

**Principles:**
1. **Plans ARE prompts** — Executable instructions, not documents to interpret
2. **Verification built-in** — Every task has acceptance criteria
3. **Fresh context per task** — Subagents prevent context rot
4. **Solo developer + AI** — No enterprise theater

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│  1. DISCUSS     Capture decisions before planning           │
│  2. PLAN        Research → Create verified specs            │
│  3. EXECUTE     Work through tasks with deviation rules     │
│  4. VERIFY      Confirm deliverables actually work          │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: DISCUSS

**Purpose:** Capture user's vision BEFORE any planning.

**Process:**
1. Ask about the goal (what are we building?)
2. Identify gray areas based on domain:
   - Visual features → layout, interactions, empty states
   - APIs → response format, error handling
   - Content → structure, tone, depth
3. For each area, ask until user is satisfied
4. Document decisions in `{project}/.gsd/CONTEXT.md`

**Output Structure:**
```markdown
# Context: [Project/Phase Name]

## Decisions (Locked)
- [User decision 1]
- [User decision 2]

## Agent Discretion (Freedom Areas)
- [Area where agent can choose approach]

## Deferred Ideas (Out of Scope)
- [Not doing this now]
```

**Rule:** Never assume. Always ask.

---

## Phase 2: PLAN

**Purpose:** Create executable task specs with built-in verification.

### Research (Optional but Recommended)

Spawn sub-agent to investigate:
- Technical approach options
- Potential pitfalls
- Best practices for the domain

Save to: `{project}/.gsd/RESEARCH.md`

### Create Plans

Each plan = 2-3 tasks maximum (context efficiency).

**Task XML Structure:**
```xml
<task type="auto">
  <name>Task N: Action-oriented name</name>
  <files>src/path/file.ts, src/other/file.ts</files>
  <action>
    What to do, what to avoid and WHY.
    Be specific. No guessing.
  </action>
  <verify>Command or check to prove completion</verify>
  <done>Measurable acceptance criteria</done>
</task>
```

**Task Types:**
- `type="auto"` — Agent executes autonomously
- `type="checkpoint:verify"` — User must verify
- `type="checkpoint:decision"` — User must choose

### Plan Verification

Before execution, verify plans against:
- [ ] Tasks are specific and actionable
- [ ] Each task has verify + done criteria
- [ ] Scope matches CONTEXT.md decisions
- [ ] No enterprise bloat

Save plans to: `{project}/.gsd/plans/{phase}-{N}-PLAN.md`

---

## Phase 3: EXECUTE

**Purpose:** Work through tasks with deviation handling.

### Execution Rules

1. Read plan as literal instructions
2. Execute each task in order
3. Verify done criteria before moving on
4. Apply deviation rules automatically
5. Document everything

### Deviation Rules

**Apply automatically — track for summary:**

| Rule | Trigger | Action | Permission |
|------|---------|--------|------------|
| **Bug** | Broken behavior, errors, security issues | Fix → verify → track | Auto |
| **Missing Critical** | Missing validation, auth, error handling | Add → verify → track | Auto |
| **Blocking** | Prevents completion (missing deps, wrong types) | Fix blocker → track | Auto |
| **Architectural** | New table, schema change, breaking API | STOP → ask user | Ask |

**Rule 4 (Architectural) Format:**
```
⚠️ Architectural Decision Needed

Current task: [task name]
Discovery: [what prompted this]
Proposed change: [modification]
Why needed: [rationale]
Alternatives: [other approaches]

Proceed? (yes / different approach / defer)
```

### Fresh Context Pattern

For multi-task execution, spawn sub-agents:
- Each sub-agent gets fresh 200k context
- Main context stays lean for user interaction
- Prevents quality degradation

### Task Completion

After each task:
1. Verify done criteria met
2. Commit changes (if applicable)
3. Record in summary
4. Move to next task

---

## Phase 4: VERIFY

**Purpose:** Confirm deliverables actually work.

### Automated Verification
- Run verify commands from each task
- Check files exist
- Run tests if applicable

### User Acceptance

Walk user through testable deliverables:
1. Extract what they should be able to do now
2. Present one at a time
3. Get yes/no or issue description
4. If issues found → create fix plans

**If all pass:** Mark phase complete.  
**If issues:** Don't debug manually — create fix plan and re-execute.

---

## File Structure

```
{project}/
└── .gsd/
    ├── PROJECT.md           # Vision, always loaded
    ├── STATE.md             # Current position, decisions, blockers
    ├── REQUIREMENTS.md      # Scoped v1/v2 requirements
    ├── ROADMAP.md           # Phases and progress
    ├── CONTEXT.md           # User decisions from discuss phase
    ├── RESEARCH.md          # Domain research (optional)
    └── plans/
        ├── 01-01-PLAN.md    # Phase 1, Plan 1
        ├── 01-01-SUMMARY.md # Execution results
        └── ...
```

**Templates:** Copy from `assets/` directory when initializing project files.

---

## Quick Mode

For small tasks that don't need full planning:

**Trigger:** "Quick: [task description]"

**Process:**
1. Skip research and discussion
2. Create single plan with 1-3 tasks
3. Execute with deviation rules
4. Verify and commit

**When to use:**
- Bug fixes
- Small features
- Config changes
- One-off tasks

---

## State Management

### STATE.md Template
```markdown
# Project State

## Current Position
Phase: [N]
Plan: [N of M]
Status: [planning | executing | verifying | blocked]

## Decisions Made
- [Decision 1] — [rationale]
- [Decision 2] — [rationale]

## Blockers
- [Blocker if any]

## Deviations Applied
- [Rule N] [Description] — [resolution]
```

Update STATE.md after each significant action.

---

## Anti-Patterns (Banned)

From original GSD:

❌ **Enterprise theater**
- Story points, sprint ceremonies
- Human time estimates (days/weeks)
- RACI matrices, stakeholder syncs

❌ **Vague tasks**
```xml
<!-- BAD -->
<task>
  <name>Add authentication</name>
  <action>Implement auth</action>
  <verify>???</verify>
</task>
```

❌ **Filler language**
- "Let me...", "I'd be happy to..."
- "Great question!", "Excellent!"

✅ **Direct, imperative, technical**

---

## OpenClaw Adaptations

**Original GSD** → **OpenClaw Version**

| GSD | OpenClaw |
|-----|----------|
| `/gsd:command` slash commands | Natural language triggers |
| Claude Code Task() spawning | `sessions_spawn` sub-agents |
| `.claude/` directory | `{project}/.gsd/` directory |
| Bash scripts | PowerShell/cross-platform |
| git commit protocol | Optional, user preference |

**Preserved Core:**
- XML task structure with verify/done
- Deviation rules
- Fresh context via sub-agents
- State management
- Plan verification loop

---

## Example Usage

**User:** "Let's plan the ORO website SEO overhaul"

**Agent (DISCUSS):**
```
Starting GSD workflow for: ORO Website SEO Overhaul

Before planning, I need to understand your vision.

1. What's the primary goal?
   a) Rank higher for specific keywords
   b) Improve technical SEO scores
   c) Both
   d) Something else

2. Any pages that are highest priority?
3. Budget constraints for tools/services?
4. Timeline expectations?
```

**After discussion → creates CONTEXT.md**

**Agent (PLAN):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► PLANNING: ORO SEO Overhaul
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Spawning research sub-agent...
[Research complete]

Creating plans...
- Plan 1: Technical SEO fixes (3 tasks)
- Plan 2: Content optimization (2 tasks)
- Plan 3: Performance improvements (3 tasks)

Verifying plans against requirements...
✓ All checks passed

Ready to execute?
```

---

## Credits

This skill is adapted from **Get Shit Done (GSD)** by **Lex Christopherson** (@glittercowboy).

- **Original Repository:** https://github.com/glittercowboy/get-shit-done
- **License:** MIT
- **Philosophy:** Solo developer + AI, no enterprise bloat

Thank you Lex for creating an incredibly effective system for building things with AI.

---

## Version History

- **1.0.0** — Initial OpenClaw adaptation
