---
name: cross-model-review
description: Adversarial plan review using two different AI models. Supports static mode (fixed roles) and alternating mode (models swap writer/reviewer each round, fully autonomous). Use when building features touching auth/payments/data models, or plans >1hr to implement. NOT for simple fixes, research tasks, or quick scripts.
---

# cross-model-review

## Metadata
```yaml
name: cross-model-review
version: 2.0.0
description: >
  Adversarial plan review using two different AI models.
  v2: Alternating mode — models swap writer/reviewer each round.
  Fully autonomous loop — no human input between rounds.
  Use when: building features touching auth/payments/data models,
  plans that will take >1hr to implement.
  NOT for: simple one-file fixes, research tasks, quick scripts.
triggers:
  - "review this plan"
  - "cross review"
  - "challenge this"
  - "is this plan solid?"
  - "adversarial review"
```

---

## When to Activate
Activate this skill when the user:
- Says any trigger phrase above
- Shares a plan and asks for adversarial/second-opinion review
- Asks you to "sanity check" a multi-step implementation plan

Do NOT activate for: simple fixes, one-liners, pure research tasks.

---

## Modes

### Static Mode (v1 — backward compatible)
Fixed roles: planner always writes, reviewer always reviews. Requires human to trigger each round.

### Alternating Mode (v2 — recommended)
Models swap roles each round. Fully autonomous — no human input between rounds.

**Flow:**
- Round 1: Model A writes the plan. Model B reviews.
- Round 2: Model B rewrites (based on its own review). Model A reviews.
- Round 3: Model A rewrites (based on its own review). Model B reviews.
- ...continues alternating until both agree (reviewer says APPROVED) or max rounds hit.

**Why this works:**
- Each model must implement its own critique — can't nitpick without owning the fix
- The other model catches over-engineering or proportionality issues
- Natural convergence: each round addresses the other's concerns

---

## Autonomous Orchestration (Alternating Mode)

You (the main agent) run this loop. It's fully autonomous after kickoff.

### Step 1 — Save the plan and init

```bash
node review.js init \
  --plan /path/to/plan.md \
  --mode alternating \
  --model-a "anthropic/claude-opus-4-6" \
  --model-b "openai-codex/gpt-5.3-codex" \
  --project-context "Brief description for reviewer calibration" \
  --out /home/ubuntu/clawd/tasks/reviews
```

Captures workspace path from stdout.

### Step 2 — The autonomous loop

```
while true:
  step = next-step(workspace)

  if step.action == "done":
    break  # APPROVED!

  if step.action == "max-rounds":
    ask user: override or manual fix
    break

  if step.action == "review":
    spawn sub-agent with step.model, step.prompt
    save response to workspace/round-N-response.json
    parse-round(workspace, round, response)
    continue

  if step.action == "revise":
    spawn sub-agent with step.model, step.prompt
    save output plan to temp file
    save-plan(workspace, temp file, version)
    continue
```

### Step 3 — Finalize

When the loop exits with APPROVED:
```bash
node review.js finalize --workspace <workspace>
```

Present: rounds taken, issues found/resolved, rubric scores, plan-final.md location.

---

## CLI Reference

```
Commands:
  init           Create a review workspace
  next-step      Get next action for autonomous loop
  parse-round    Parse a reviewer response, update issue tracker
  save-plan      Save a revised plan version from writer output
  finalize       Generate plan-final.md, changelog.md, summary.json
  status         Print current workspace state

init options:
  --plan <file>            Path to plan file (required)
  --mode <m>               "static" (default) or "alternating"
  --model-a <m>            Model A — writes first (alternating mode, required)
  --model-b <m>            Model B — reviews first (alternating mode, required)
  --reviewer-model <m>     Reviewer model (static mode, required)
  --planner-model <m>      Planner model (static mode, required)
  --project-context <s>    Brief project context for reviewer calibration
  --out <dir>              Output base dir (default: tasks/reviews)
  --max-rounds <n>         Max rounds (default: 5 static, 8 alternating)
  --token-budget <n>       Token budget for context (default: 8000)

next-step options:
  --workspace <dir>        Path to review workspace (required)
  Returns JSON: { action, model, round, prompt, planVersion, saveTo }
  Actions: "review", "revise", "done", "max-rounds"

parse-round options:
  --workspace <dir>        Path to review workspace (required)
  --round <n>              Round number (required)
  --response <file>        Path to raw reviewer response (required)

save-plan options:
  --workspace <dir>        Path to review workspace (required)
  --plan <file>            Path to revised plan markdown (required)
  --version <n>            Plan version number (required)

finalize options:
  --workspace <dir>        Path to review workspace (required)
  --override-reason <s>    Reason for force-approving with open issues
  --ci-force               Required in non-TTY mode when overriding

status options:
  --workspace <dir>        Path to review workspace (required)

Exit codes:
  0   Approved / OK
  1   Revise / max-rounds
  2   Error
```

---

## Detailed Orchestration (for agent implementation)

### Spawning reviewers
```
step = next-step(workspace)  # action: "review"
response = sessions_spawn(model=step.model, task=step.prompt, timeout=120s)
# Save raw response to workspace/round-{step.round}-response.json
parse-round(workspace, step.round, response_file)
```

System instruction for reviewer: "You are a senior engineering reviewer. Output ONLY valid JSON matching the schema. No tool calls. No markdown fences. No preamble."

### Spawning writers
```
step = next-step(workspace)  # action: "revise"
revised_plan = sessions_spawn(model=step.model, task=step.prompt, timeout=300s)
# Save raw output as temp file
save-plan(workspace, temp_file, step.planVersion)
```

System instruction for writer: none needed — the prompt is self-contained.

### Error handling
- Reviewer timeout/failure: retry once, then ask user
- Writer timeout/failure: retry once, then ask user
- Parse error on review JSON: re-prompt reviewer once with "Your response was not valid JSON"
- Max rounds hit: present status to user, ask for override or manual fix

### Convergence
The loop converges when the reviewer says APPROVED with no open CRITICAL/HIGH blockers. The script enforces this — if reviewer says APPROVED but blockers remain, it overrides to REVISE.

---

## Static Mode (v1 — backward compatible)

For static mode, the original orchestration from v1 still works:

### Step 1 — Init
```bash
node review.js init --plan <file> --reviewer-model <m> --planner-model <m>
```

### Step 2 — Manual loop
For each round: build reviewer prompt from template, spawn reviewer, parse-round, revise plan yourself, continue.

### Step 3 — Finalize
Same as alternating mode.

---

## Integration with coding-agent

Before dispatching any plan to coding-agent that:
- Touches auth, payments, or data models
- Has 3+ implementation steps
- The user hasn't already reviewed adversarially

Run cross-model-review first. Only proceed if exit code 0.

---

## Notes
- Workspace persists in `tasks/reviews/` — referenceable later
- `issues.json` tracks full lifecycle of all issues
- `meta.json` stores mode, models, current round, verdict, needsRevision flag
- `next-step` is the state machine — always call it to determine what to do
- Dedup warnings help catch semantic drift across rounds
- Models must be from different provider families (cross-provider enforcement)
- `--project-context` is injected into reviewer prompts for calibration
