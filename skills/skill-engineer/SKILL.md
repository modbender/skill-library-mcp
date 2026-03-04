---
name: skill-engineer
description: Design, test, review, and maintain agent skills for OpenClaw systems using multi-agent iterative refinement. Orchestrates Designer, Reviewer, and Tester subagents for quality-gated skill development. Use when user asks to "design skill", "review skill", "test skill", "audit skills", "refactor skill", or mentions "agent kit quality".
metadata:
  author: skill-engineer
  version: 3.1.0
  owner: main agent (or any agent in the kit requiring skill development capability)
  based_on: Anthropic Complete Guide to Building Skills for Claude (2026-01)
---

# Skill Engineer

Own the full lifecycle of agent skills in your OpenClaw agent kit. The entire multi-agent workflow depends on skill quality — a weak skill produces weak results across every run.

**Core principle:** Builders don't evaluate their own work. This skill enforces separation of concerns through a multi-agent architecture where design, review, and testing are performed by independent subagents.

---

## Scope & Boundaries

### What This Skill Handles
- Skill design: SKILL.md, skill.yml, README.md, tests, scripts, references
- Skill review: quality evaluation, rubric scoring, gap analysis
- Skill testing: self-play validation, trigger testing, functional testing
- Skill maintenance: iteration based on feedback, refactoring
- Agent kit audit: inventory, consistency, quality scoring across all skills

### What This Skill Does NOT Handle
- **Release pipeline** — publishing, versioning, changelogs belong to release processes
- **Repository management** — git submodules, repo creation, branch strategy belong to your VCS workflow
- **Deployment** — installing skills to agents, configuration management
- **Tracking** — progress tracking, task management, project boards
- **Infrastructure** — MCP servers, API keys, environment setup

### Where This Skill Ends
This skill produces **validated skill artifacts** (SKILL.md, skill.yml, README.md, tests, scripts). Once artifacts pass quality gates, responsibility transfers to whatever system handles publishing and deployment.

### Success Criteria

A skill development cycle is considered successful when:

1. **Quality gates passed** — Reviewer scores ≥28/33 (Deploy threshold)
2. **No blocking issues** — Tester reports no issues marked as "blocking"
3. **All artifacts generated** — SKILL.md, skill.yml, README.md, tests/, scripts/ (if needed), references/ (if needed)
4. **OPSEC clean** — No hardcoded secrets, paths, org names, or private URLs
5. **Scripts validated** — All deterministic validation scripts execute successfully on target platform(s)
6. **Trigger accuracy** — Tester reports ≥90% trigger accuracy (true positives + true negatives)

If any criterion fails, the skill returns to the Designer for revision.

### Inputs

When invoking this skill, the orchestrator must gather:

| Input | Description | Required | Source |
|-------|-------------|----------|--------|
| **Problem description** | What capability or workflow needs to be enabled | Yes | User conversation |
| **Target audience** | Which agent(s) will use this skill | Yes | User or inferred |
| **Expected interactions** | With users, APIs, files, MCP servers, other skills | Yes | Requirements discussion |
| **Inputs/Outputs** | What data the skill receives and produces | Yes | Requirements discussion |
| **Constraints** | Performance limits, security requirements, dependencies | No | User or system |
| **Prior feedback** | Review or test reports from previous iterations | No | Previous Reviewer/Tester |
| **Existing artifacts** | If refactoring/maintaining an existing skill | No | File system |

**Example requirements gathering:**
```
User: "I need a skill for analyzing competitor websites"

Orchestrator gathers:
- Problem: Automate competitor analysis with structured output
- Audience: research-agent
- Interactions: web_fetch, browser tool, writes markdown reports
- Inputs: competitor URLs, analysis criteria
- Outputs: comparison table, insights markdown
- Constraints: must complete in <60s per site
```

These inputs are then passed to the Designer to begin the design process.

---

## Architecture Overview

The skill-engineer uses a three-role iterative architecture. The orchestrator (you, the main agent) spawns subagents for each role and never does creative or evaluation work directly.

```
Orchestrator (main agent)
    │
    ├─ Spawn ──→ Designer (creative subagent)
    │                │
    │                ▼ produces skill artifacts
    │
    ├─ Spawn ──→ Reviewer (critical subagent)
    │                │
    │                ▼ scores, identifies issues
    │
    ├─ Spawn ──→ Tester (empirical subagent)
    │                │
    │                ▼ runs self-play, reports results
    │
    └─ Decision: Ship / Revise / Fail
```

### Iteration Loop

```
Designer → Reviewer ──pass──→ Tester ──pass──→ Ship
              │                  │
              fail               fail
              │                  │
              ▼                  ▼
         Designer revises   Designer revises
              │                  │
              ▼                  ▼
           Reviewer          Reviewer + Tester
              │
           (max 3 iterations, then fail)
```

**Exit conditions:**
- **Ship:** Reviewer scores ≥ 28/33 (85%+) AND Tester reports no blocking issues
- **Revise:** Reviewer or Tester found fixable issues (iterate)
- **Fail:** 3 iterations exhausted and still below quality bar

### Iteration Failure Path

After 3 failed iterations, the orchestrator must:

1. **Stop iteration** — do not continue trying
2. **Report failure to user** with:
   - Summary: "Skill development failed after 3 iterations"
   - All 3 iteration reports (Reviewer + Tester feedback)
   - Final quality score
   - List of unresolved blocking issues
3. **Present options to user:**
   - Provide more context or clarify requirements (restart with better inputs)
   - Simplify scope (reduce skill complexity and retry)
   - Abandon this skill (requirements may be infeasible)
4. **Do NOT silently fail** — always report to user and await decision

**Never:** Continue past 3 iterations or ship a skill that hasn't passed quality gates.

### Subagent Spawning Mechanism

"Spawning" a subagent means creating a distinct execution context for each role. In OpenClaw:

**Option 1: Role-Based Execution (Recommended for most cases)**
The orchestrator executes each role sequentially in the same session but with clear role boundaries:
```
[Acting as DESIGNER] ...generate artifacts...
[Acting as REVIEWER] ...evaluate artifacts...
[Acting as TESTER] ...validate artifacts...
```

Document which role is active at each step. This maintains separation of concerns without multi-session overhead.

**Option 2: Separate Agent Sessions (For complex workflows)**
Use `openclaw agent --message "..." --session-id <unique-id>` to create isolated sessions:
```bash
# Spawn Designer
openclaw agent --session-id "skill-v1-designer" \
  --message "Act as Designer. Requirements: [...]"

# Spawn Reviewer
openclaw agent --session-id "skill-v1-reviewer" \
  --message "Act as Reviewer. Artifacts: [path]. Rubric: [...]"
```

This provides true isolation but increases token cost and coordination complexity.

**Which to use:**
- Use Option 1 (role-based) for routine skill work
- Use Option 2 (separate sessions) when parallelization is needed or when Designer work is extremely complex (1000+ line skills)

**Critical:** Regardless of method, the orchestrator must never perform creative (Designer) or evaluation (Reviewer/Tester) work itself. It only coordinates.

---

## Orchestrator Responsibilities

The orchestrator coordinates the loop. It does NOT write skill content or evaluate quality.

1. **Gather requirements** from the user (problem, audience, inputs/outputs, interactions)
2. **Spawn Designer** with requirements and any prior feedback
3. **Collect Designer output** (skill artifacts)
4. **Spawn Reviewer** with artifacts and the quality rubric
5. **Collect Reviewer feedback** (scores + structured issues)
6. **If issues:** feed feedback back to Designer (go to step 2, increment iteration)
7. **If passing review:** Spawn Tester with artifacts
8. **Collect Tester results** (pass/fail + structured report)
9. **If issues:** feed test results back to Designer (go to step 2)
10. **If all pass:** add final review scores table to README.md, then deliver artifacts to user
11. **Track iteration count** — fail after 3 iterations (see Iteration Failure Path)

### Final Review Scores in README

Every shipped skill must include a quality scorecard in its README.md. This is the Reviewer's final scores, added by the Orchestrator before delivery:

```markdown
## Quality Scorecard

| Category | Score | Details |
|----------|-------|---------|
| Completeness (SQ-A) | 7/7 | All checks pass |
| Clarity (SQ-B) | 4/5 | Minor ambiguity in edge case handling |
| Balance (SQ-C) | 4/4 | AI/script split appropriate |
| Integration (SQ-D) | 4/4 | Compatible with standard agent kit |
| Scope (SCOPE) | 3/3 | Clean boundaries, no leaks |
| OPSEC | 2/2 | No violations |
| References (REF) | 3/3 | All sources cited |
| Architecture (ARCH) | 2/2 | Separation of concerns maintained |
| **Total** | **29/30** | |

*Scored by skill-engineer Reviewer (iteration 2)*
```

This scorecard serves as a quality certificate. Users can assess skill quality before installing.

### Version Control

The orchestrator manages git commits throughout the workflow:

**When to commit:**
- After Designer produces initial artifacts (iteration 1): `git add . && git commit -m "feat: initial design for <skill-name>"`
- After Designer revisions (iteration 2+): `git add . && git commit -m "fix: address review issues (iteration N)"`
- After Tester passes and before ship: `git add README.md && git commit -m "docs: add quality scorecard for <skill-name>"`

**When to push:**
- After final ship (all gates passed): `git push origin main`
- Do NOT push intermediate iterations — only ship-ready artifacts

**Branch strategy:**
- Work in main branch for routine skill development
- Use feature branches for experimental or breaking changes

### Error Handling

The orchestrator must handle technical failures gracefully:

| Failure Type | Detection | Response |
|--------------|-----------|----------|
| **Git push fails** | Exit code ≠ 0 | Retry once. If fails again, report to user: "Cannot push to remote. Check network/permissions." |
| **OPSEC scan script missing** | File not found | Skip OPSEC automated check, but flag in review: "Manual OPSEC review required — script not found." |
| **File write errors** | Permission denied | Report: "Cannot write to [path]. Check file permissions." Fail workflow. |
| **Subagent crashes** | Timeout or error | Log the error, attempt retry once. If fails again, report: "Subagent failed. Manual intervention required." |
| **Review score = 0** | All checks fail | Report: "Skill failed all quality checks. Requirements may be unclear or skill design is fundamentally flawed. Recommend starting over." |

**Retry logic:**
- Git operations: 1 retry after 5s delay
- File operations: 1 retry after 2s delay
- Subagent spawns: 1 retry with fresh context

**Fail-fast rules:**
- If iteration count exceeds 3, fail immediately (no further retries)
- If OPSEC violations found, fail immediately (no iteration)
- If required files cannot be written, fail immediately

### Performance Notes

**Orchestrator workload:** Coordinating Designer/Reviewer/Tester across 1-3 iterations can be complex, especially for large skills (1000+ lines). The orchestrator manages:
- Requirements gathering
- Subagent coordination (3-9 spawns in typical workflow)
- Feedback routing between roles
- Iteration tracking
- Final scorecard assembly
- Git operations

**Token considerations:** A full 3-iteration cycle can consume 50k-150k tokens depending on skill complexity. For extremely complex skills, consider:
- Breaking into sub-skills (each with simpler scope)
- Using separate agent sessions (Option 2 spawning) to isolate token contexts
- Simplifying requirements before starting iteration

**If orchestrator feels overwhelmed:** This is a signal that the skill being designed may be too complex. Revisit the scope definition and consider decomposition.

### Spawning Context

Each subagent receives only what it needs:

| Role | Receives | Does NOT Receive |
|------|----------|------------------|
| Designer | Requirements, prior feedback (if any), design principles | Reviewer rubric internals |
| Reviewer | Skill artifacts, quality rubric, scope boundaries | Requirements discussion |
| Tester | Skill artifacts, test protocol | Review scores |

---

## Designer Role

**Purpose:** Generate and revise skill content.

**For complete Designer instructions, see:** `references/designer-guide.md`

### Quick Reference

**Inputs:** Requirements, design principles, feedback (on iterations 2+)

**Outputs:** SKILL.md, skill.yml, README.md, tests/, scripts/, references/

**Naming step (mandatory):** Before writing artifacts, present 3-5 name candidates to the user with rationale. See `references/designer-guide.md` Step 2 for criteria and process.

**Key constraints:**
- Apply progressive disclosure (frontmatter → body → linked files)
- Apply scoping rules (explicit boundaries, no scope creep)
- Apply tool selection guardrails (validate before execution)
- README for strangers only (no internal org details)
- Follow AI vs. Script decision framework

**Design principles:**
- Progressive disclosure (3-level system)
- Composability (works alongside other skills)
- Portability (same skill works across Claude.ai, Claude Code, API)

---

## Reviewer Role

**Purpose:** Independent quality evaluation. The Reviewer has never seen the requirements discussion — it evaluates artifacts on their own merits.

**For complete Reviewer rubric and scoring guide, see:** `references/reviewer-rubric.md`

### Quick Reference

**Inputs:** Skill artifacts, quality rubric, scope boundaries

**Outputs:** Review report with scores, verdict (PASS/REVISE/FAIL), issues, strengths

**Quality rubric (33 checks total):**
- SQ-A: Completeness (8 checks)
- SQ-B: Clarity (5 checks)
- SQ-C: Balance (5 checks)
- SQ-D: Integration (5 checks)
- SCOPE: Boundaries (3 checks)
- OPSEC: Security (2 checks)
- REF: References (3 checks)
- ARCH: Architecture (2 checks)

**Scoring thresholds:**
- 28-33 pass → Deploy (PASS verdict)
- 20-27 pass → Revise (fixable issues)
- 10-19 pass → Redesign (major rework)
- 0-9 pass → Reject (fundamentally flawed)

**Pre-review:** Run deterministic validation scripts before manual evaluation

---

## Tester Role

**Purpose:** Empirical validation via self-play. The Tester loads the skill and attempts realistic tasks.

**For complete Tester protocol, see:** `references/tester-protocol.md`

### Quick Reference

**Inputs:** Skill artifacts, test protocol

**Outputs:** Test report with trigger accuracy, functional test results, edge cases, blocking/non-blocking issues, verdict (PASS/FAIL)

**Test protocol:**
1. **Trigger tests** — verify skill loads correctly (≥90% accuracy threshold)
2. **Functional tests** — execute 2-3 realistic tasks, note confusion points
3. **Edge case tests** — missing inputs, ambiguous requirements, boundary cases

**Issue classification:**
- **Blocking:** Prevents skill from functioning (must fix before ship)
- **Non-blocking:** Impacts quality but doesn't break core functionality

**Pass criteria:** No blocking issues + ≥90% trigger accuracy

---

## Agent Kit Audit Protocol

Periodic full audit of the agent kit:

1. **Inventory all skills** — list every SKILL.md with owner agent
2. **Check for orphans** — skills that no agent uses
3. **Check for duplicates** — overlapping functionality
4. **Check for gaps** — workflow steps that have no skill
5. **Check balance** — are some agents overloaded while others idle?
6. **Check consistency** — naming conventions, output formats
7. **Run quality score** on each skill (SQ-A through SQ-D)
8. **Produce audit report** with scores and recommendations

### Audit Output Template

```markdown
# Agent Kit Audit Report

**Date:** [date]
**Skills audited:** [count]

## Skill Inventory

| # | Skill | Agent | Quality Score | Status |
|---|-------|-------|--------------|--------|
| 1 | [name] | [agent] | X/33 | Deploy/Revise/Redesign |

## Issues Found
1. ...

## Recommendations
1. ...

## Action Items
| # | Action | Priority | Owner |
|---|--------|----------|-------|
```

---

## Skill Interaction Map

Maintain a map of how skills interact:

```
orchestrator-agent (coordinates workflow)
    ├── content-creator (writes content)
    │   └── consumes: research outputs, review feedback
    ├── content-reviewer (reviews content)
    │   └── produces: review reports
    ├── research-analyst (researches topics)
    │   └── produces: research consumed by content-creator
    ├── validator (validates outputs)
    └── skill-engineer (this skill — meta)
        └── consumes: all skills for audit
```

Adapt this to your specific agent architecture.
