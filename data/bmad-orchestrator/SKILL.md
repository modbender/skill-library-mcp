---
name: bmad-orchestrator
description: Orchestrate the full BMAD Method workflow across OpenClaw and Claude Code. Use when starting a new project with BMAD methodology, running BMAD phases (brainstorming, PRD, architecture, implementation), or managing Claude Code agents through BMAD workflows. Handles interactive phases (1-3) with the user and delegates implementation (phase 4) to Claude Code via tmux.
---

# BMAD Orchestrator

Orchestrate the 4-phase BMAD Method (Breakthrough Method of Agile AI Driven Development) across OpenClaw ↔ Claude Code.

## Architecture

- **Phases 1-3 (Interactive)**: Run through OpenClaw chat with the user. You facilitate brainstorming, refine the PRD, debate architecture. The user's ideas matter most here.
- **Party Mode**: At key decision points, suggest running party mode on Claude Code — multiple BMAD agents debate the topic and produce richer output.
- **Phase 4 (Automated)**: Delegate to Claude Code via tmux on the dev VM. Monitor progress, report back.

## Prerequisites

- Claude Code installed on dev VM (accessible via SSH)
- BMAD framework installed in the project (`_bmad/` directory with agents, workflows, commands)
- tmux available on the dev VM

## State Tracking

Track workflow state in `_bmad-output/orchestrator-state.yaml`:

```yaml
project: <name>
vm_host: <ip>
vm_user: <user>
project_path: <path>
tmux_socket: /tmp/openclaw-tmux-sockets/openclaw.sock
tmux_session: bmad-<project>
current_phase: 1|2|3|4
current_workflow: <workflow-name>
artifacts:
  brainstorming_report: null|path
  product_brief: null|path  
  prd: null|path
  ux_spec: null|path
  architecture: null|path
  epics: null|path
  sprint_status: null|path
  project_context: null|path
```

## Phase 1: Analysis (Interactive with User)

### 1.1 Brainstorming (`bmad-brainstorming`)

Run this conversationally with the user in OpenClaw chat:

1. Ask: "What project are we building? Give me the elevator pitch."
2. Explore the problem space — ask about users, pain points, existing solutions
3. Challenge assumptions — play devil's advocate
4. **Suggest Party Mode**: "Want me to run party mode on Claude Code? The BMAD agents (analyst, architect, PM, dev) will debate your idea and surface things we might miss."
5. If party mode → send `/bmad-brainstorming` to Claude Code, capture output, share highlights
6. Synthesize into key decisions and themes
7. Produce: `brainstorming-report.md`

### 1.2 Research (`bmad-bmm-research`) — Optional

If the project needs market/technical/domain validation:

1. Discuss with user what needs validation
2. Send research workflow to Claude Code for heavy lifting
3. Review findings together

### 1.3 Product Brief (`bmad-bmm-create-product-brief`)

1. Start from brainstorming output
2. Walk through with user: vision, target users, success metrics, scope
3. **Suggest Party Mode**: "The PM and analyst agents can stress-test this brief. Run it?"
4. If party mode → send command, capture debate highlights
5. Iterate until user approves
6. Produce: `product-brief.md`

## Phase 2: Planning (Interactive with User)

### 2.1 PRD (`bmad-bmm-create-prd`)

1. Load product brief as context
2. Walk through requirements with user section by section:
   - Functional requirements (FRs)
   - Non-functional requirements (NFRs)
   - User journeys
   - Success metrics
3. **Suggest Party Mode**: "PM + architect + QA can review these requirements together. Good time to catch gaps."
4. If party mode → send command, share findings
5. Iterate until user signs off
6. Produce: `prd.md`

### 2.2 UX Design (`bmad-bmm-create-ux-design`) — If applicable

Only for projects with UI. Skip for backend/infrastructure tools.

## Phase 3: Solutioning (Interactive with User)

### 3.1 Architecture (`bmad-bmm-create-architecture`)

1. Load PRD as context
2. Discuss technical decisions with user:
   - Language/framework choices
   - Deployment model
   - Key patterns and trade-offs
   - ADRs (Architecture Decision Records)
3. **Suggest Party Mode**: "Architect + dev + QA debating the architecture will surface implementation risks early."
4. If party mode → send command, share the debate
5. Iterate with user
6. Produce: `architecture.md` with ADRs

### 3.2 Epics & Stories (`bmad-bmm-create-epics-and-stories`)

1. Load architecture + PRD
2. Present epic breakdown to user for review
3. Discuss story sizing, priorities, dependencies
4. Produce: `epics.md` with stories

### 3.3 Readiness Check (`bmad-bmm-check-implementation-readiness`)

1. Send to Claude Code for automated gate check
2. Share result: PASS / CONCERNS / FAIL
3. If CONCERNS/FAIL → discuss with user, fix gaps
4. Produce: readiness report

### 3.4 Project Context (`bmad-bmm-generate-project-context`)

1. Send to Claude Code after architecture is finalized
2. Review output with user
3. Produce: `project-context.md`

## Phase 4: Implementation (Automated via Claude Code)

### 4.0 Setup

See [references/tmux-setup.md](references/tmux-setup.md) for tmux session initialization.

### 4.1 Sprint Planning

Send to Claude Code:
```
/bmad-bmm-sprint-planning
```
Capture and save `sprint-status.yaml`.

### 4.2 Story Loop (per epic)

For each epic, for each story:

1. **Create Story**: Send `/bmad-bmm-create-story` → produces `story-[slug].md`
2. **Dev Story**: Send `/bmad-bmm-dev-story` → implements code + tests
3. **Code Review**: Send `/bmad-bmm-code-review` → validates quality
4. If review fails → send fixes back, re-review
5. Update sprint status
6. Commit after each story

### 4.3 Epic Completion

After all stories in an epic:
1. Send `/bmad-bmm-retrospective` for lessons learned
2. Optionally run `/bmad-bmm-automate` for E2E test generation
3. Commit and update sprint status

### 4.4 Monitoring

Set up a cron job to monitor Claude Code progress every 15 minutes.
Report status updates to user via chat.

## Party Mode Integration

Party mode simulates a multi-agent discussion in Claude Code. Use it at these moments:

| When | Why | Command |
|------|-----|---------|
| After brainstorming | Surface blind spots | `/bmad-party-mode` with brainstorming context |
| After product brief | Stress-test the vision | `/bmad-party-mode` with brief |
| During PRD review | Catch requirement gaps | `/bmad-party-mode` with PRD draft |
| Architecture decisions | Debate trade-offs | `/bmad-party-mode` with architecture |

To trigger party mode on Claude Code:
```bash
tmux send-keys -l -- "/bmad-party-mode" && sleep 0.3 && tmux send-keys Enter
```
Capture output, extract key insights, present to user.

## Claude Code Commands Reference

See [references/bmad-commands.md](references/bmad-commands.md) for the full command list.

## Quick Flow (Skip Phases 1-3)

For small, well-understood work:
1. `/bmad-bmm-quick-spec` → tech-spec.md
2. `/bmad-bmm-quick-dev` → implementation

Only use when user explicitly says the project is simple and well-understood.

## Sending Commands to Claude Code

See [references/tmux-setup.md](references/tmux-setup.md) for the tmux interaction patterns.

Key rules:
- Split text and Enter with a delay (Claude Code TUI timing)
- Use `capture-pane -S -200` to read output
- Wait for idle prompt before sending next command
- Use `C-c` to interrupt if stuck
