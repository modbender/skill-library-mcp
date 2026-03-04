# Claude Code Agent Teams Skill - Research Synthesis

**Date:** 2026-02-16  
**Purpose:** Design an OpenClaw skill for managing Claude Code agent teams

---

## Gap Analysis

### What Exists
1. **`coding-agent` skill (installed)** - Runs Claude Code/Codex via PTY, background mode, process control
2. **`agent-team-orchestration`** (ClawHub) - General multi-agent coordination patterns (not Claude Code specific)
3. **`agent-team-kit`** (ClawHub) - Heartbeat-driven self-managing teams (not Claude Code specific)
4. **`claude-code-supervisor`** (ClawHub) - Monitors Claude Code sessions in tmux, detects errors

### What's Missing
**No skill that leverages Claude Code's native agent teams feature.**

Current skills either:
- Run Claude Code as single sessions (coding-agent)
- Provide generic agent orchestration (not Claude Code specific)
- Monitor sessions (supervisor) but don't create/manage teams

### The Opportunity
Claude Code's native agent teams feature provides:
- Built-in team coordination (shared task list, mailbox)
- Inter-agent messaging (teammates communicate directly)
- Split-pane or in-process display modes
- Delegate mode (lead coordinates, doesn't implement)
- Plan approval gates (teammates plan before implementing)

**None of the existing skills integrate with these features.**

---

## Core Capabilities Needed

### 1. Team Lifecycle Management
- **Create teams** with proper config (display mode, permissions, model selection)
- **Spawn teammates** with well-crafted prompts
- **Monitor progress** via task list and teammate status
- **Shut down gracefully** (teammates first, then cleanup)

### 2. Prompt Engineering
- **Battle-tested templates** for common scenarios:
  - Parallel code review (multi-lens)
  - Debugging with competing hypotheses
  - Full-stack feature (frontend/backend/tests)
  - Architecture decision records (debate pattern)
  - Bottleneck analysis (cross-domain)
  - Inventory classification (data-parallel)

### 3. Task Coordination
- **Define clear boundaries** (file ownership, directory scope)
- **Size tasks appropriately** (5-6 per teammate)
- **Manage dependencies** (task A blocks task B until complete)
- **Track status** (pending → in progress → complete)

### 4. Quality Gates
- **Require plan approval** for risky changes
- **Hook integration** (TeammateIdle, TaskCompleted)
- **Review protocols** (builders review specs, reviewers check builds)

### 5. Cost Management
- **Model mixing** (Opus for lead, Sonnet for teammates)
- **Minimize broadcasts** (prefer direct messages)
- **Right-size teams** (3 teammates often better than 6)

---

## Design Principles (from Research)

### From Claude Code Official Docs
1. **Give teammates enough context** - Include task details in spawn prompt
2. **Avoid file conflicts** - Each teammate owns different files
3. **Use delegate mode by default** - Lead coordinates, teammates implement
4. **Wait for teammates to finish** - Don't let lead race ahead
5. **Start with research/review** - Build intuition before implementation

### From ClaudeFast Best Practices
1. **Size tasks appropriately** - Self-contained units with clear deliverables
2. **Monitor and steer** - Check progress, redirect off-track work
3. **Battle-test prompts** - Use proven patterns, not ad-hoc prompts
4. **Enforce quality gates** - Reviews prevent quality drift

### From agent-team-orchestration Skill
1. **Clear roles** - Every agent has one primary role (overlap causes confusion)
2. **Defined state transitions** - Orchestrator owns state changes
3. **Handoff protocols** - What was done, where artifacts are, how to verify
4. **Cross-role reviews** - Builders review specs, reviewers check builds

---

## Skill Architecture

### File Structure
```
claude-code-teams/
├── SKILL.md                          # Main skill documentation
├── README.md                         # GitHub readme (usage guide)
├── package.json                      # Metadata, dependencies
├── scripts/
│   ├── team-create.sh                # Create team with config
│   ├── team-monitor.sh               # Monitor task list + teammates
│   ├── team-cleanup.sh               # Graceful shutdown
│   └── validate-setup.sh             # Check env var, tmux, etc.
├── templates/
│   ├── parallel-review.md            # Code review template
│   ├── competing-hypotheses.md       # Debug with debate
│   ├── fullstack-feature.md          # Frontend/backend/tests
│   ├── architecture-decision.md      # ADR with debate
│   ├── bottleneck-analysis.md        # Cross-domain investigation
│   └── inventory-classification.md   # Data-parallel work
├── hooks/
│   ├── TeammateIdle.sh               # Auto-assign follow-up tasks
│   └── TaskCompleted.sh              # Enforce quality gates
├── references/
│   ├── best-practices.md             # When to use teams, pitfalls
│   ├── cost-management.md            # Token optimization strategies
│   ├── troubleshooting.md            # Common issues + solutions
│   └── prompting-guide.md            # How to craft effective prompts
└── examples/
    ├── pr-review-example.md          # Real-world PR review
    ├── bug-hunt-example.md           # Competing hypotheses in action
    └── feature-build-example.md      # Full-stack coordination
```

### SKILL.md Structure
```markdown
# Claude Code Agent Teams

Production skill for orchestrating Claude Code's native agent teams feature.

## When to Use This Skill
- Multi-lens code reviews (security, performance, test coverage)
- Debugging with competing hypotheses
- Full-stack features (frontend/backend/tests)
- Architecture decisions requiring debate
- Cross-domain investigations (bottleneck analysis)

## When NOT to Use This Skill
- Single session is sufficient
- Sequential work with tight dependencies
- Same-file edits (conflict risk)
- Simple tasks where coordination overhead > benefit

## Quick Start
[Step-by-step: enable feature → spawn team → monitor → cleanup]

## Templates
[Link to 6 battle-tested templates with usage guidance]

## Best Practices
[Core principles with examples]

## Troubleshooting
[Common issues from docs + ClaudeFast guide]

## Cost Management
[Model mixing, broadcast minimization, team sizing]

## References
[Links to reference docs]
```

---

## Key Decisions

### 1. PTY-First Approach
Agent teams are interactive CLIs → always use `pty:true` (lesson from coding-agent skill)

### 2. Template-Driven
Provide 6 proven templates, not generic "figure it out" guidance:
- Parallel review
- Competing hypotheses
- Fullstack feature
- Architecture decision
- Bottleneck analysis
- Inventory classification

### 3. Hooks for Automation
Include example hooks for:
- TeammateIdle → auto-assign follow-up
- TaskCompleted → enforce quality gates (tests pass, review done)

### 4. Delegate Mode Default
Recommend starting with delegate mode to prevent lead from doing implementation work

### 5. Cost-Conscious
Provide concrete guidance on:
- Model mixing (when to use Opus vs Sonnet)
- Broadcast vs direct message
- Team sizing (3 vs 6 teammates)

---

## Differentiation from Existing Skills

| Skill | Focus | Gap This Fills |
|-------|-------|----------------|
| coding-agent | Run Claude Code as single session | No team coordination |
| agent-team-orchestration | Generic multi-agent patterns | Not Claude Code specific |
| agent-team-kit | Heartbeat-driven self-management | Not Claude Code specific |
| claude-code-supervisor | Monitor sessions for errors | Doesn't create/manage teams |
| **claude-code-teams** (ours) | **Claude Code native teams** | **Leverage built-in features** |

---

## Success Criteria

### For Developers
1. Can spawn a team in <5 minutes using templates
2. Understands when teams add value vs overhead
3. Can troubleshoot common issues without docs
4. Knows how to optimize costs (model mixing, sizing)

### For ClawHub
1. High-quality skill (documentation, examples, best practices)
2. Solves real problem (gap in ecosystem)
3. Battle-tested patterns (not theoretical)
4. Clear when to use / when not to use

### For Matt's LinkedIn Campaign
1. Concrete example of building with OpenClaw
2. Shows deep understanding of agent orchestration
3. Contributes back to community (like office365-connector multi-account)
4. Positions Matt as AI architecture expert

---

## Next Steps

### Phase 1: Core Skill (MVP)
1. Create skill structure (SKILL.md, templates, scripts)
2. Write 6 battle-tested prompt templates
3. Add validation script (check env var, tmux)
4. Write best practices + troubleshooting docs

### Phase 2: Automation
1. Create example hooks (TeammateIdle, TaskCompleted)
2. Add team-monitor.sh script (task list + teammate status)
3. Add team-cleanup.sh (graceful shutdown automation)

### Phase 3: Polish
1. Real-world examples (PR review, bug hunt, feature build)
2. Cost optimization calculator (estimate tokens for team size/duration)
3. Video walkthrough (if desired)

### Phase 4: Publication
1. GitHub repo (openclaw/claude-code-teams or matt's personal)
2. ClawHub publication
3. LinkedIn post (if part of campaign)

---

## Questions for Matt

1. **Scope:** Start with MVP (Phase 1) or go straight to Phase 2 with automation?
2. **GitHub repo:** Your personal GitHub or openclaw org? (need write access if openclaw)
3. **LinkedIn tie-in:** Use this as content for the campaign? (Could be Post 2 or 3)
4. **Name:** `claude-code-teams` or something catchier? (`team-conductor`, `agent-orchestra`, `code-swarm`)
5. **Spawn approach:** Build it together now, or spawn a sub-agent to draft it?

---

## Estimated Effort

### If Building Together (Scout + Matt)
- **Phase 1 (MVP):** 2-3 hours (SKILL.md + 6 templates + validation)
- **Phase 2 (Automation):** 1-2 hours (hooks + monitoring scripts)
- **Phase 3 (Polish):** 1-2 hours (examples + cost calc)
- **Phase 4 (Publication):** 30 min (ClawHub publish)

**Total:** 4-7 hours

### If Spawning Sub-Agent
- **Research synthesis:** Done ✅
- **Sub-agent drafts:** 1-2 hours (creates skeleton)
- **Matt + Scout review/refine:** 1-2 hours
- **Publication:** 30 min

**Total:** 2-4 hours

---

## Recommendation

**Spawn a sub-agent** to create the initial structure + templates + docs, then we review/refine together.

**Why:**
1. Research is done (this synthesis doc)
2. Sub-agent can draft in parallel while you work on other things
3. We review together, catch any gaps
4. Faster to MVP (can publish today/tomorrow)

**Sub-agent task:**
```
Create a production-ready OpenClaw skill for Claude Code agent teams.

Context: Research synthesis at /projects/claude-code-teams-skill/RESEARCH-SYNTHESIS.md

Deliverables:
1. Complete skill structure (SKILL.md + templates + scripts + references)
2. 6 battle-tested prompt templates (from ClaudeFast patterns)
3. Best practices + troubleshooting docs
4. README.md for GitHub
5. package.json with metadata

Requirements:
- Follow OpenClaw skill conventions (see installed skills for examples)
- Make it production-ready (not a prototype)
- Include real-world examples
- Clear when to use / when not to use
- Cost-conscious (model mixing, team sizing)

Output location: /projects/claude-code-teams-skill/
```

Shall I spawn the sub-agent, or do you want to build it together in this session?
