---
name: sprint-os
description: "5-minute sprint operating system for AI agents. Autonomous execution cycles: ASSESS → PLAN → SCOPE → EXECUTE → MEASURE → ADAPT → LOG → NEXT. Includes optional Convex integration for sprint tracking, metrics, and content deduplication."
requiredEnv:
  - CONVEX_SPRINT_URL  # optional — Convex HTTP API endpoint for sprint logging
permissions:
  - network: Makes HTTP requests to Convex endpoint (optional) and any resources needed for sprint work
  - filesystem: Reads/writes sprint logs to working directory
source:
  url: https://github.com/Batsirai/carson-skills
  author: Carson Jarvis (@CarsonJarvisAI)
  github: https://github.com/Batsirai/carson-skills
  verified: true
security:
  note: The Convex endpoint URL is safe to store in env. No credentials are embedded in the skill itself.
---

# Sprint OS — 5-Minute Sprint Operating System

> Built for AI agents that ship. Every sprint produces one shippable artifact — not a plan, not a summary. A real thing.

---

## What This Is

Sprint OS is an operating discipline for AI agents (and humans) who need to stay in execution mode. You work in continuous 5-minute sprints. Each sprint follows the same 8-step loop. Every sprint is logged. Nothing gets batched, buried, or lost.

**When to load this skill:**
- User asks the agent to "operate in sprint mode" or "use Sprint OS"
- Starting a new project or work session and wanting structure
- Needing autonomous task execution with momentum tracking
- Wanting to log work to a Convex backend for tracking and deduplication

---

## The Sprint Loop

Every sprint follows this exact sequence:

### 1. ASSESS
> What is the current state? What is the gap to the target outcome?

- Read the active task list, relevant files, and recent sprint log
- Identify where things stand right now
- Name the gap: what's missing between current state and the outcome?

### 2. PLAN
> What is the single highest-leverage action available right now?

- Pick ONE thing to do in this sprint
- Apply the prioritization hierarchy (see below)
- Do not batch or multi-task

### 3. SCOPE
> Define "done" in ≤5 minutes.

- Name the specific artifact this sprint will produce
- If it can't be done in 5 minutes, break it into a smaller sprint
- No sprint ends without a concrete output

### 4. EXECUTE
> Do the work. Produce the artifact.

- Execute the scoped task
- Focus entirely on the output — no scope creep
- If you discover the scope was wrong, stop, re-scope, and continue

### 5. MEASURE
> Did it move the metric? What changed?

- State the concrete result: what artifact was produced
- Name the relevant metric and whether it moved
- Be honest: "completed" vs "partially completed" vs "blocked"

### 6. ADAPT
> Reprioritize. Kill what's not working.

- Based on the result, what should the NEXT sprint be?
- If 3 consecutive sprints produced no measurable movement: switch workstream or angle
- Never keep grinding on a dead approach — adapt immediately

### 7. LOG
> Record to sprint log + (if configured) Convex.

Write a sprint log entry (see format below) to the sprint log file, and optionally POST to the Convex endpoint.

### 8. NEXT
> Immediately begin the next sprint.

No gaps. No reflection breaks longer than 30 seconds. Momentum is the goal.

---

## Sprint Rules

- Every sprint MUST produce a shippable artifact
- If >5 minutes, break into smaller sprints
- Never batch-plan more than 3 sprints ahead
- Bias toward momentum over perfection
- Every sprint must connect to an active outcome
- If blocked, log the blocker and skip to the next available sprint — never idle

---

## Prioritization Hierarchy

Before every sprint, ask:
> "If I could only do ONE thing in the next 5 minutes to move closer to the outcome, what would it be?"

1. **Fix what's broken** → Actively losing money or trust? Fix it first.
2. **Optimize what's working** → Something converting? Double down before exploring new.
3. **Test new angles** → Small experiments to find the next lever.
4. **Build infrastructure** → Only when 1–3 are humming.

---

## Pivot Triggers

Stop the current workstream and pivot when:
- **3 consecutive sprints** with no measurable movement → switch workstream or angle
- **Channel hitting diminishing returns** → reduce allocation, test alternatives
- **Unexpected win** (viral, press, referral spike) → drop lower-priority, capitalize immediately
- **Customer feedback pattern emerging** → elevate to top of sprint queue

---

## Sprint Log Format

Write one entry per sprint to `sprint-log.md` in the working directory:

```markdown
## Sprint [N] — [YYYY-MM-DD HH:MM]

**Project:** [project name]
**Workstream:** [marketing / development / content / research / etc.]
**Task:** [what you did]
**Artifact:** [what was produced — link or one-line description]
**Metric:** [what moved, or "no movement"]
**Status:** completed | partial | blocked
**Blocker:** [only if blocked — what's stopping you]
**Next sprint:** [what comes next]
```

---

## Convex Integration (Optional)

If `CONVEX_SPRINT_URL` is set, POST every sprint log entry to the Convex HTTP endpoint. This enables:
- Sprint history across sessions
- Workstream breakdown reports
- Content deduplication (check before creating)
- Metric trend tracking

### Setup

1. Deploy the Convex backend in `scripts/convex-setup.md`
2. Set `CONVEX_SPRINT_URL` to your Convex HTTP site URL (e.g., `https://your-deployment.convex.site`)
3. Sprints will auto-log on step 7 of each loop

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/sprints/log` | Log a completed sprint |
| GET | `/sprints/recent?project=X&limit=N` | Recent sprint history |
| GET | `/sprints/stats?project=X&days=N` | Workstream breakdown |
| POST | `/metrics/record` | Record a metric value |
| GET | `/metrics/latest?metric=X` | Current metric value |
| GET | `/metrics/trend?metric=X&days=N` | Metric over time |
| POST | `/content/log` | Log content creation |
| GET | `/content/search?query=X` | Deduplication check |

### Sprint Log Payload

```bash
curl -X POST $CONVEX_SPRINT_URL/sprints/log \
  -H "Content-Type: application/json" \
  -d '{
    "sprintId": 1,
    "project": "my-project",
    "workstream": "marketing",
    "task": "Write homepage headline variants",
    "artifact": "3 headline variants in headlines.md",
    "metric": "no movement yet",
    "status": "completed",
    "owner": "agent",
    "timestamp": 1740000000000
  }'
```

### Script

Use `scripts/log-sprint.sh` for quick CLI logging:

```bash
./scripts/log-sprint.sh \
  --project "my-project" \
  --workstream "development" \
  --task "Fix checkout redirect bug" \
  --artifact "PR #42 opened" \
  --metric "checkout CVR: TBD pending deploy" \
  --status "completed"
```

---

## Daily Rhythm

### Morning
- Read active task list
- ASSESS the current state of all outcomes
- Set today's #1 priority
- Begin sprint 1

### Continuous
- Sprint back-to-back, 5 minutes each
- Log every sprint (file + Convex if configured)
- Spawn sub-agents for heavy execution work
- Never stop between sprints for more than 30 seconds

### End of Day
- Complete the sprint log
- Update active task list with what moved
- Set tomorrow's #1 priority
- Run `scripts/log-sprint.sh --daily-summary` if Convex is configured

### Weekly (Friday)
- Review: which workstream had the most impact?
- Which sprints were wasted? Why?
- Biggest bottleneck assessment
- Restack priorities for next week

---

## Reporting Formats

### Daily Status
```
📊 DAY [X] — [DATE]
SPRINTS: [completed today] | TOP WIN: [best result]
BLOCKER: [biggest obstacle]
METRICS: [key metric] → [current value]
TOMORROW: [1–2 sentences]
```

### Weekly Review
```
📈 WEEK [X] — [DATE RANGE]
SPRINTS: [total] (by workstream breakdown)
WINS: [top 3 with metrics]
MISSES: [top 3 with root cause]
LESSONS: [top 3]
NEXT WEEK: [top 3 priorities]
ESCALATIONS: [decisions needed from human]
```

---

## Usage Examples

```
# Start sprint operating mode
"Enter sprint mode. My project is [X]. Target outcome: [Y]."

# Run a sprint
"Run sprint on: write 3 email subject line variants for the welcome sequence."

# Review recent sprints
"Show my sprint log for today."

# Weekly review
"Generate weekly sprint review."

# With Convex logging
"Log sprint: task=wrote homepage copy, artifact=homepage-v2.md, metric=awaiting test, status=completed"
```

---

## File Structure

```
sprint-os/
├── SKILL.md                    ← This file
├── README.md                   ← Human-readable overview
└── scripts/
    ├── log-sprint.sh           ← CLI sprint logger (Convex optional)
    └── convex-setup.md         ← Instructions for Convex backend setup
```

---

*Sprint OS v1.0 — February 2026*
*A product by Carson Jarvis (@CarsonJarvisAI)*
