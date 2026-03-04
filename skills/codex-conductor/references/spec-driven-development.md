# Spec-Driven Development (Non-Negotiable)

This is the governing principle of the orchestrator: **no code without a spec**.

## Core Rule

The coding agent MUST NOT write implementation code until a written, approved spec exists for what it is about to build. This prevents:

- Guessing at requirements
- Making assumptions about behavior
- Building features the user didn't ask for
- Architectural drift from undocumented decisions

## What Counts as a Spec

A spec is a written document (in `docs/` or inline in a task file) that includes:

1. **What** is being built (feature/component/fix)
2. **Why** it's needed (user story, problem statement)
3. **Acceptance criteria** (testable conditions for "done")
4. **Constraints** (tech stack, performance, security, compatibility)
5. **Out of scope** (what this does NOT do)

Minimum viable spec for a single task:
```markdown
## Task: [Name]
**Goal:** [One sentence]
**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
**Constraints:** [Any limits]
**Out of Scope:** [What we're not doing]
```

## Spec Lifecycle

### 1. Spec Creation (Before G2)
- Orchestrator (or user) writes the spec
- Spec is stored in `docs/specs/` or embedded in `docs/requirements.md`
- For brownfield: existing behavior must be documented first

### 2. Spec Approval (Before Implementation)
- User reviews and approves (in gated mode)
- Or orchestrator validates completeness (in autonomous mode)
- Spec is marked APPROVED in `docs/specs/` or status.json

### 3. Spec → Task Mapping (G3/G4)
- Each task in `docs/g4-task-plan.md` MUST reference a spec section
- Format: `Spec: requirements.md#feature-name` or `Spec: specs/auth.md`
- Tasks without spec references are BLOCKED

### 4. Implementation (Coding Agent)
- Agent receives: spec + task description + context
- Agent MUST NOT invent features not in spec
- Agent MUST flag spec gaps and request clarification (not guess)

### 5. Verification Against Spec
- Orchestrator checks implementation against acceptance criteria
- Deviation from spec = FAIL (not creative license)

## Enforcement Points

### Gate G1 (Planning Approved)
- `docs/requirements.md` must exist with testable requirements
- Acceptance criteria must be explicit, not vague

### Gate G2 (Architecture Approved)
- `docs/specs/` directory must exist with at least one spec file
- Or `docs/requirements.md` must have spec-level detail for v1 features
- ADR references must point to spec decisions

### Gate G3/G4 (Build)
- Each task prompt MUST include:
  - Spec reference
  - Acceptance criteria from spec
  - Explicit boundaries
- `run_gate.py` blocks tasks without `--spec-ref` argument

### Coding Agent Prompt Template
All coding agent prompts MUST include this preamble:

```
## SPEC-DRIVEN RULES
1. You are implementing ONLY what is specified below.
2. Do NOT add features, abstractions, or "improvements" not in spec.
3. If the spec is unclear or incomplete, STOP and ask for clarification.
4. Do NOT guess at requirements. Ever.
5. Your output will be verified against the acceptance criteria below.

## SPEC
[Insert spec section here]

## ACCEPTANCE CRITERIA
[Insert criteria here]

## TASK
[Insert specific task]
```

## Red Flags (Auto-Fail)

The following trigger automatic gate failure:

- Task executed without spec reference
- Coding agent added unrequested features
- Acceptance criteria missing or vague ("should work well")
- Implementation diverged from spec without change request
- Assumptions documented as facts

## Change Requests

If requirements change mid-build:

1. Run `change_impact.py` to assess impact
2. Update spec documents
3. Re-approve affected specs
4. Update traceability matrix
5. Only then resume implementation

No "I'll just add this quickly" — all changes go through spec update.

## Spec Templates

### Feature Spec (`docs/specs/feature-name.md`)
```markdown
# Feature: [Name]

## Overview
[1-2 sentences]

## User Story
As a [user type], I want [goal] so that [benefit].

## Acceptance Criteria
- AC-1: Given [context], when [action], then [result]
- AC-2: Given [context], when [action], then [result]

## Allowed Scope Files
- src/path/to/feature/**
- tests/path/to/feature/**

## Technical Constraints
- [Stack/performance/security constraints]

## Dependencies
- [Other features, APIs, services]

## Out of Scope
- [What this feature explicitly does NOT do]

## Open Questions
- [Anything needing clarification before implementation]
```

### API Endpoint Spec
```markdown
# Endpoint: [Method] [Path]

## Purpose
[What this endpoint does]

## Request
- Method: [GET/POST/etc]
- Path: [/api/v1/resource]
- Auth: [Required/None/Scope]
- Body: [Schema or example]

## Response
- Success: [Status + schema]
- Errors: [Status codes + meanings]

## Validation Rules
- [Field validations]

## Side Effects
- [Database changes, events emitted, etc]
```

## Summary

**Spec → Approve → Implement → Verify**

No shortcuts. No guessing. No "I assumed you wanted..."

The spec is the contract. Deviate = Fail.
