# Reviewer Rubric

Complete evaluation rubric and scoring guide for the Reviewer role in the skill-engineer workflow.

---

## Role Definition

**Purpose:** Independent quality evaluation. The Reviewer has never seen the requirements discussion — it evaluates artifacts on their own merits.

### Inputs
- Skill artifacts (SKILL.md, skill.yml, README.md, tests/, scripts/, references/)
- Quality rubric (this document)
- Scope boundaries (from skill-engineer SKILL.md)

### Outputs
- Review report with:
  - Quality scores (SQ-A through SQ-D, SCOPE, OPSEC, REF, ARCH)
  - Verdict: PASS / REVISE / FAIL
  - Structured issues list (if REVISE)
  - Strengths list

### Constraints
- Never refer to requirements discussion (you haven't seen it)
- Evaluate artifacts on their own merits
- Run deterministic validation scripts before manual review
- Be specific in issue location and severity

---

## Pre-Review Validation Scripts

Before manual evaluation, the Reviewer must run deterministic validation scripts to catch mechanical errors:

```bash
# 1. Verify all required files exist
bash scripts/check-completeness.sh /path/to/skill/

# 2. Count rubric checks (for skill-engineer itself)
bash scripts/count-rubric-checks.sh /path/to/skill/SKILL.md

# 3. Validate scorecard math (after Orchestrator adds scores)
bash scripts/validate-scorecard.sh /path/to/skill/README.md
```

Scripts are located in `/tmp/openclaw-skill-skill-engineer/scripts/` (or local installation path). If scripts fail, record the failure in the review report.

**Why scripts first:** Deterministic checks (file existence, math validation, counting) should never be manual work. Run scripts to catch obvious errors, then focus human/AI review on judgment tasks (clarity, design quality, edge cases).

---

## Quality Rubric

### SQ-A. Completeness Checklist (8 checks)

| # | Requirement | Pass/Fail |
|---|------------|-----------|
| SQ-A1 | Has clear description and trigger words | |
| SQ-A2 | Defines inputs (what the agent receives) | |
| SQ-A3 | Defines outputs (files, formats, locations) | |
| SQ-A4 | Has step-by-step workflow (not just goals) | |
| SQ-A5 | Includes output format templates | |
| SQ-A6 | Has version control conventions documented (if applicable) | |
| SQ-A7 | Specifies which agent owns this skill | |
| SQ-A8 | Defines success criteria (how to know it worked) | |

### SQ-B. Clarity Test (5 checks)

| # | Requirement | Pass/Fail |
|---|------------|-----------|
| SQ-B1 | A new agent reading this skill for the first time can execute it without ambiguity | |
| SQ-B2 | No contradictions between sections | |
| SQ-B3 | Technical terms are defined or obvious from context | |
| SQ-B4 | Examples are provided for complex outputs | |
| SQ-B5 | Edge cases are addressed (what if data is missing? what if search fails?) | |

### SQ-C. Balance Test (5 checks)

| # | Requirement | Pass/Fail |
|---|------------|-----------|
| SQ-C1 | Workload is appropriate for a single sub-agent run | |
| SQ-C2 | If multiple sub-agents are involved, workload is balanced | |
| SQ-C3 | No sub-agent is both producer AND evaluator of the same output | |
| SQ-C4 | Orchestrator agent does orchestration only, not direct work | |
| SQ-C5 | Deterministic tasks use scripts; judgment tasks use AI agents | |

### SQ-D. Integration Test (5 checks)

| # | Requirement | Pass/Fail |
|---|------------|-----------|
| SQ-D1 | Outputs are compatible with downstream skills that consume them | |
| SQ-D2 | File paths and naming conventions are consistent across skills | |
| SQ-D3 | Version control conventions match other skills (if applicable) | |
| SQ-D4 | No orphan skills (every skill is used by at least one agent/workflow) | |
| SQ-D5 | No duplicate functionality across skills | |

**Total SQ checks: 23**

### SCOPE Checks (3 checks)

| Check | Description |
|-------|-------------|
| SCOPE-1 | Skill has explicit "Scope & Boundaries" section |
| SCOPE-2 | No content that belongs to adjacent systems (repo mgmt, deployment, tracking) |
| SCOPE-3 | README contains no internal organization references |

### OPSEC Checks (2 checks)

| Check | Description |
|-------|-------------|
| OPSEC-1 | No hardcoded paths, usernames, org names, or private URLs |
| OPSEC-2 | No secrets, tokens, or credentials |

### REF Checks (3 checks)

| Check | Description |
|-------|-------------|
| REF-1 | All external sources cited in SKILL.md are listed in references/ with URLs |
| REF-2 | Key methodologies or frameworks have traceable origins (paper, guide, blog post) |
| REF-3 | No orphaned claims — if the skill says "based on X," X must be findable in references/ |

### ARCH Checks (2 checks)

| Check | Description |
|-------|-------------|
| ARCH-1 | Separation of concerns maintained (builders ≠ evaluators) |
| ARCH-2 | Deterministic tasks use scripts, judgment tasks use AI |

**Total checks: 33**

---

## Scoring Thresholds

| Rating | Score | Criteria |
|--------|-------|----------|
| **Deploy** | 28-33 pass | Ready for production use |
| **Revise** | 20-27 pass | Minor fixes needed, fundamentals sound |
| **Redesign** | 10-19 pass | Major issues, needs rethinking |
| **Reject** | 0-9 pass | Fundamental problems, start over |

**Verdict mapping:**
- 28+ → PASS (ship to Tester)
- 20-27 → REVISE (fixable issues, return to Designer)
- 10-19 → REVISE (major rework needed)
- 0-9 → FAIL (fundamentally flawed, abandon or restart)

---

## Feedback Format

```markdown
## Review Report

**Iteration:** N
**Quality Score:** X/33 (total checks: SQ + SCOPE + OPSEC + REF + ARCH)
**Scope Score:** X/3 (SCOPE checks)
**OPSEC:** CLEAN / VIOLATION (list)
**Architecture:** X/2 (ARCH checks)
**References:** X/3 (REF checks)

**Verdict:** PASS / REVISE / FAIL

### Issues (if REVISE)
1. [SQ-A3] Missing output format specification
   - Location: SKILL.md § Workflow
   - Severity: minor/major/blocking
   - Suggestion: Add output template after step 3

2. [SCOPE-2] Contains git submodule workflow
   - Location: SKILL.md § Publishing
   - Severity: major
   - Suggestion: Remove; this belongs to repo management

### Strengths
- Clear progressive disclosure structure
- Good trigger phrase coverage
```

---

## Issue Severity Guidelines

| Severity | Definition | Examples |
|----------|------------|----------|
| **blocking** | Skill cannot function correctly; must fix before ship | Missing required files, contradictory instructions, OPSEC violations |
| **major** | Skill might work but has significant design flaws | Scope violations, missing error handling, poor trigger accuracy |
| **minor** | Skill works but has polish issues | Typos, missing examples, suboptimal formatting |

---

## Common Review Patterns

### Pattern 1: Scope Creep
**Symptom:** Skill includes content about deployment, tracking, repo management
**Fix:** Move out-of-scope content to appropriate systems
**Check:** SCOPE-2

### Pattern 2: Missing Progressive Disclosure
**Symptom:** SKILL.md is >600 lines with everything inline
**Fix:** Extract detailed docs to references/
**Check:** Implied in SQ-B1 (clarity)

### Pattern 3: README Leaks Internal Details
**Symptom:** README mentions "knowledge repo", "submodules", "tracking system"
**Fix:** Rewrite README for external audience (strangers)
**Check:** SCOPE-3

### Pattern 4: Builder = Evaluator
**Symptom:** Same subagent creates and evaluates its own work
**Fix:** Split into separate roles
**Check:** ARCH-1

### Pattern 5: AI Doing Math
**Symptom:** AI agent calculates scores, counts items, validates totals
**Fix:** Replace with deterministic scripts
**Check:** ARCH-2

---

## Review Checklist

Before submitting review report:

- [ ] Ran all validation scripts (check-completeness.sh, etc.)
- [ ] Counted all 33 rubric items and recorded pass/fail
- [ ] Identified severity for each issue (blocking/major/minor)
- [ ] Provided specific location for each issue (file + section)
- [ ] Suggested concrete fix for each issue
- [ ] Listed at least 2 strengths (if any exist)
- [ ] Verdict matches score threshold (28+ = PASS, <28 = REVISE)
- [ ] Did NOT reference requirements discussion (stay independent)
