---
name: gsd:resume-project
description: Instantly restore full project context for session continuation
argument-hint: ""
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
  - AskUserQuestion
---

<objective>
Instantly restore full project context so "Where were we?" has an immediate, complete answer.

**Trigger - Use this workflow when:**
- Starting a new session on an existing project
- User says "continue", "what's next", "where were we", "resume"
- Any planning operation when .planning/ already exists
- User returns after time away from project
</objective>

<execution_context>
@/usr/lib/node_modules/clawdbot/skills/gsd/references/continuation-format.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/PROJECT.md
</context>

<process>

## Phase 1: Detect Existing Project

Check if this is an existing project:

```bash
ls .planning/STATE.md 2>/dev/null && echo "Project exists"
ls .planning/ROADMAP.md 2>/dev/null && echo "Roadmap exists"
ls .planning/PROJECT.md 2>/dev/null && echo "Project file exists"
```

**If STATE.md exists:** Proceed to load state
**If only ROADMAP.md/PROJECT.md exist:** Offer to reconstruct STATE.md
**If .planning/ doesn't exist:** This is a new project - route to /gsd:new-project

## Phase 2: Load State

Read and parse STATE.md, then PROJECT.md:

```bash
cat .planning/STATE.md
cat .planning/PROJECT.md
```

**From STATE.md extract:**

- **Project Reference**: Core value and current focus
- **Current Position**: Phase X of Y, Plan A of B, Status
- **Progress**: Visual progress bar
- **Recent Decisions**: Key decisions affecting current work
- **Pending Todos**: Ideas captured during sessions
- **Blockers/Concerns**: Issues carried forward
- **Session Continuity**: Where we left off, any resume files

**From PROJECT.md extract:**

- **What This Is**: Current accurate description
- **Requirements**: Validated, Active, Out of Scope
- **Key Decisions**: Full decision log with outcomes
- **Constraints**: Hard limits on implementation

## Phase 3: Check Incomplete Work

Look for incomplete work that needs attention:

```bash
# Check for continue-here files (mid-plan resumption)
ls .planning/phases/*/.continue-here*.md 2>/dev/null

# Check for plans without summaries (incomplete execution)
for plan in .planning/phases/*/*-PLAN.md; do
  summary="${plan/PLAN/SUMMARY}"
  [ ! -f "$summary" ] && echo "Incomplete: $plan"
done 2>/dev/null

# Check for interrupted agents
if [ -f .planning/current-agent-id.txt ] && [ -s .planning/current-agent-id.txt ]; then
  AGENT_ID=$(cat .planning/current-agent-id.txt | tr -d '\n')
  echo "Interrupted agent: $AGENT_ID"
fi
```

**If .continue-here file exists:**
- This is a mid-plan resumption point
- Flag: "Found mid-plan checkpoint"

**If PLAN without SUMMARY exists:**
- Execution was started but not completed
- Flag: "Found incomplete plan execution"

**If interrupted agent found:**
- Subagent was spawned but session ended before completion
- Flag: "Found interrupted agent"

## Phase 4: Present Status

Present complete project status to user:

```
╔══════════════════════════════════════════════════════════════╗
║  PROJECT STATUS                                               ║
╠══════════════════════════════════════════════════════════════╣
║  Building: [one-liner from PROJECT.md "What This Is"]         ║
║                                                               ║
║  Phase: [X] of [Y] - [Phase name]                            ║
║  Plan:  [A] of [B] - [Status]                                ║
║  Progress: [██████░░░░] XX%                                  ║
║                                                               ║
║  Last activity: [date] - [what happened]                     ║
╚══════════════════════════════════════════════════════════════╝

[If incomplete work found:]
⚠️  Incomplete work detected:
    - [.continue-here file or incomplete plan]

[If interrupted agent found:]
⚠️  Interrupted agent detected:
    Agent ID: [id]
    Task: [task description from agent-history.json]

[If pending todos exist:]
📋 [N] pending todos — /gsd:check-todos to review

[If blockers exist:]
⚠️  Carried concerns:
    - [blocker 1]
    - [blocker 2]
```

## Phase 5: Determine Next Action

Based on project state, determine the most logical next action:

**If interrupted agent exists:**
→ Primary: Resume interrupted agent
→ Option: Start fresh

**If .continue-here file exists:**
→ Primary: Resume from checkpoint
→ Option: Start fresh on current plan

**If incomplete plan (PLAN without SUMMARY):**
→ Primary: Complete the incomplete plan
→ Option: Abandon and move on

**If phase in progress, all plans complete:**
→ Primary: Transition to next phase
→ Option: Review completed work

**If phase ready to plan:**
→ Check if CONTEXT.md exists for this phase:
- If CONTEXT.md missing: Primary: Discuss phase vision
- If CONTEXT.md exists: Primary: Plan the phase

**If phase ready to execute:**
→ Primary: Execute next plan
→ Option: Review the plan first

## Phase 6: Offer Options

Present contextual options based on project state:

```
What would you like to do?

[Primary action based on state]
1. {Primary action}

[Secondary options:]
2. Review current phase status
3. Check pending todos ([N] pending)
4. Review brief alignment
5. Something else
```

Wait for user selection.

## Phase 7: Route to Workflow

Based on user selection, route to appropriate workflow:

- **Execute plan** → Show command for user to run after clearing:
  ```
  ---

  ## ▶ Next Up

  **{phase}-{plan}: [Plan Name]** — [objective]

  `/gsd:execute-phase {phase}`

  <sub>`/clear` first → fresh context window</sub>

  ---
  ```

- **Plan phase** → Show command for user to run after clearing:
  ```
  ---

  ## ▶ Next Up

  **Phase [N]: [Name]** — [Goal]

  `/gsd:plan-phase [phase-number]`

  <sub>`/clear` first → fresh context window</sub>

  ---
  ```

- **Transition** → /gsd:transition
- **Check todos** → Read .planning/todos/pending/, present summary
- **Something else** → Ask what they need

## Phase 8: Update Session

Before proceeding, update session continuity in STATE.md:

```markdown
## Session Continuity

Last session: [now]
Stopped at: Session resumed, proceeding to [action]
Resume file: [updated if applicable]
```

</process>

<reconstruction>
If STATE.md is missing but other artifacts exist:

"STATE.md missing. Reconstructing from artifacts..."

1. Read PROJECT.md → Extract "What This Is" and Core Value
2. Read ROADMAP.md → Determine phases, find current position
3. Scan *-SUMMARY.md files → Extract decisions, concerns
4. Count pending todos in .planning/todos/pending/
5. Check for .continue-here files → Session continuity

Reconstruct and write STATE.md, then proceed normally.
</reconstruction>

<quick_resume>
If user says "continue" or "go":
- Load state silently
- Determine primary action
- Execute immediately without presenting options

"Continuing from [state]... [action]"
</quick_resume>

<success_criteria>
- [ ] STATE.md loaded (or reconstructed)
- [ ] Incomplete work detected and flagged
- [ ] Clear status presented to user
- [ ] Contextual next actions offered
- [ ] User knows exactly where project stands
- [ ] Session continuity updated
</success_criteria>
