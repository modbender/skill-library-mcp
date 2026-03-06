# Phased Implementation Pattern

**Use case:** Complex feature development requiring architecture design, implementation, and validation (new skills, system refactors, multi-file changes)

## Core Philosophy

**Separation of Concerns:**
- **Design phase** (architect) - System thinking, trade-off analysis, integration planning
- **Build phase** (coder) - Implementation, testing, documentation
- **Review phase** (reviewer) - Quality audit, security check, behavioral validation

**Why separate?**
- Architects optimize for long-term maintainability (coders might take shortcuts)
- Coders focus on working code (architects might over-engineer)
- Reviewers catch integration issues (fresh perspective)

## Architecture

```
Main Agent (high-level feature request)
    │
    ├─ Phase 1: SystemArchitect
    │       │
    │       ├─ Analyzes requirements
    │       ├─ Designs architecture (files, APIs, integration points)
    │       ├─ Documents trade-offs and alternatives
    │       └─ Delivers: IMPLEMENTATION_PLAN.md
    │
    ├─ Phase 2: CoderAgent
    │       │
    │       ├─ Reads IMPLEMENTATION_PLAN.md
    │       ├─ Implements feature (writes code, tests)
    │       ├─ Verifies integration points
    │       └─ Delivers: Working code + test results
    │
    └─ Phase 3: ReviewerAgent (optional)
            │
            ├─ Code quality audit
            ├─ Security check
            ├─ Behavioral validation (does it match spec?)
            └─ Delivers: Approval or revision requests
```

## Phase 1: SystemArchitect

### Template
```markdown
## SystemArchitect - Feature design and planning

**Created:** YYYY-MM-DD
**Type:** Ephemeral (design phase)
**Model:** Sonnet (system thinking required)

### Task
Design implementation plan for: [feature description]

### Deliverables
**IMPLEMENTATION_PLAN.md with:**
1. **Requirements** (what problem are we solving?)
2. **Architecture** (files to create/modify, data flow)
3. **Integration points** (how it fits into existing system)
4. **Trade-offs** (alternatives considered, why this approach)
5. **Testing strategy** (how to verify it works)
6. **Rollback plan** (how to undo if it fails)
7. **Cost estimate** (development time, ongoing maintenance)

### Constraints
- Respect existing architecture (don't reinvent wheels)
- Prefer boring, proven patterns (no experimental tech)
- Document why, not what (code explains what)
- Plan for failure (what breaks if this fails?)

### Output Format
Structured markdown (IMPLEMENTATION_PLAN.md) in `$WORKSPACE/plans/`
```

### Example Spawn
```javascript
subagent_spawn({
  label: "architect-[feature-name]",
  task: "Design implementation plan for [feature]. Analyze current system, propose architecture, document trade-offs. Deliver IMPLEMENTATION_PLAN.md.",
  model: "sonnet",
  timeout_minutes: 20
})
```

## Phase 2: CoderAgent

### Template
```markdown
## CoderAgent - Implementation from architecture plan

**Created:** YYYY-MM-DD
**Type:** Ephemeral (build phase)
**Model:** Sonnet (Opus for complex refactors)

### Task
Implement feature according to: `$WORKSPACE/plans/IMPLEMENTATION_PLAN.md`

### Workflow
1. **Read plan** - Understand requirements, architecture, constraints
2. **Verify current state** - Check files mentioned in plan exist and are as expected
3. **Implement incrementally** - Small changes, test after each step
4. **Verify integration** - Test that new code works with existing system
5. **Document** - Update relevant files (EVOLOG.md, skill README, etc.)

### Constraints
- **No deviation from plan** without main agent approval
- **Test before commit** - Every change must be verified
- **Rollback strategy ready** - Know how to undo each step
- **Incremental commits** - Small PRs, easy to review/revert

### Deliverables
1. **Working code** (files created/modified per plan)
2. **Test results** (proof it works as specified)
3. **Documentation updates** (README, EVOLOG, etc.)
4. **IMPLEMENTATION_REPORT.md** (what was built, how to use it, known issues)

### Output Format
- Code files in specified locations
- IMPLEMENTATION_REPORT.md in `$WORKSPACE/reports/`
```

### Example Spawn
```javascript
subagent_spawn({
  label: "coder-[feature-name]",
  task: "Implement [feature] per plan in $WORKSPACE/plans/IMPLEMENTATION_PLAN.md. Test thoroughly, document changes, deliver working code.",
  model: "sonnet", // or "opus" for complex work
  timeout_minutes: 30
})
```

## Phase 3: ReviewerAgent (Optional)

### Template
```markdown
## ReviewerAgent - Quality audit and behavioral validation

**Created:** YYYY-MM-DD
**Type:** Ephemeral (review phase)
**Model:** Sonnet

### Task
Review implementation of [feature] against plan and quality standards.

### Review Checklist
- [ ] **Correctness** - Does it solve the stated problem?
- [ ] **Spec compliance** - Matches IMPLEMENTATION_PLAN.md?
- [ ] **Code quality** - Readable, maintainable, follows conventions?
- [ ] **Security** - No obvious vulnerabilities, secrets leakage?
- [ ] **Integration** - Works with existing system, no breaking changes?
- [ ] **Testing** - Adequate test coverage, edge cases handled?
- [ ] **Documentation** - Clear usage examples, limitations noted?
- [ ] **Performance** - No obvious bottlenecks, resource usage acceptable?

### Deliverables
**REVIEW_REPORT.md with:**
- **Approval status** (approved, conditional approval, rejected)
- **Findings** (issues found, severity: critical/major/minor)
- **Recommendations** (fixes required, suggestions for improvement)
- **Test results** (did reviewer's independent tests pass?)

### Output Format
REVIEW_REPORT.md in `$WORKSPACE/reports/`
```

### Example Spawn
```javascript
subagent_spawn({
  label: "reviewer-[feature-name]",
  task: "Review implementation of [feature]. Check against plan, test independently, verify quality. Deliver REVIEW_REPORT.md with approval or revision requests.",
  model: "sonnet",
  timeout_minutes: 15
})
```

## Full Workflow Example

**Feature request:** "Add memory consolidation skill that runs nightly"

### Phase 1: Architecture (15 min, $0.40)
```
SystemArchitect spawned
├─ Analyzes current memory system
├─ Designs consolidation logic (merge similar entries, archive old data)
├─ Plans cron integration (when to run, how to handle failures)
├─ Documents trade-offs (nightly vs on-demand, storage strategy)
└─ Delivers: IMPLEMENTATION_PLAN.md
```

### Phase 2: Implementation (25 min, $0.70)
```
CoderAgent spawned
├─ Reads IMPLEMENTATION_PLAN.md
├─ Creates skills/memory-consolidator/
├─ Implements consolidation logic
├─ Adds cron job configuration
├─ Tests with sample data
├─ Documents in SKILL.md
└─ Delivers: Working skill + test results
```

### Phase 3: Review (10 min, $0.30)
```
ReviewerAgent spawned
├─ Reads plan and implementation
├─ Runs independent tests
├─ Checks for edge cases (empty memory, corrupted data)
├─ Verifies cron integration doesn't break existing jobs
└─ Delivers: REVIEW_REPORT.md (approved with minor suggestions)
```

**Total:** 50 minutes, $1.40, high-quality feature with architectural documentation

## When to Use

**Use phased implementation when:**
- Feature touches 3+ files
- Requires integration with existing systems
- Cost estimate > $1.00 (worth upfront design)
- Failure would be expensive (need rollback plan)
- Long-term maintainability matters (not a throwaway script)

**Skip architecture phase when:**
- Simple script (1 file, no integration)
- Well-understood pattern (copying existing structure)
- Prototype/experiment (might throw away)
- Cost estimate < $0.50

## Cost Optimization

**Reduce costs by:**
- Using **haiku for architect** on simple features (haiku: $0.15 vs sonnet: $0.40)
- Skipping review phase for low-risk changes
- Reusing architecture patterns (template library)
- Caching common designs (e.g., "skill template" → standard structure)

**Typical costs:**
- Simple feature (architect + coder): $0.60-1.20
- Medium feature (+ reviewer): $1.20-2.50
- Complex feature (opus coder, extended review): $3.00-6.00

## Integration

Works with:
- **task-routing** (auto-trigger phased pipeline for "code_gen" tasks with complexity > 60)
- **cost-governor** (require approval for multi-phase projects > $2.00)
- **drift-guard** (reviewer validates behavioral alignment)
- **DevOps** (architect consults DevOps knowledge base for infrastructure decisions)

## Multi-Phase Coordination

Main agent orchestrates phases:

```javascript
// Phase 1: Design
const plan = await subagent_spawn({
  label: "architect-feature-x",
  task: "Design implementation plan...",
  model: "sonnet"
})

// Review plan before proceeding
if (plan.cost_estimate > threshold) {
  await human_approval(plan)
}

// Phase 2: Build
const implementation = await subagent_spawn({
  label: "coder-feature-x",
  task: `Implement per plan: ${plan.path}`,
  model: plan.recommended_model // architect suggests opus if complex
})

// Phase 3: Review (conditional)
if (implementation.risk_level === "high") {
  const review = await subagent_spawn({
    label: "reviewer-feature-x",
    task: `Review implementation: ${implementation.path}`,
    model: "sonnet"
  })
  
  if (!review.approved) {
    // Revise or abort
  }
}
```

## Failure Handling

**If architect fails:**
- Main agent attempts simpler design
- Escalate to human for requirements clarification

**If coder fails:**
- Review plan for unrealistic requirements
- Spawn new coder with adjusted constraints
- Escalate to DevOps for infrastructure issues

**If reviewer rejects:**
- Spawn new coder with review feedback
- Architect reviews plan for design flaws
- Human approval for scope changes
