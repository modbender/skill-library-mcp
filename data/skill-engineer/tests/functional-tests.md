# Functional Tests for skill-engineer

This file contains functional workflow test scenarios to validate the skill-engineer skill's core workflows.

---

## Test 1: Happy Path (Single Iteration → Ship)

**Scenario:** User requests a simple skill, Designer produces quality artifacts on first try, Reviewer and Tester both pass.

### Setup
- User request: "Create a skill for converting markdown tables to JSON"
- Requirements:
  - Input: markdown table text
  - Output: JSON array
  - No external API calls
  - Should be simple (no subagents)

### Expected Flow
1. **Orchestrator:** Gathers requirements from user
2. **Spawns Designer:** Provides requirements, design principles
3. **Designer produces:**
   - SKILL.md with clear instructions
   - skill.yml with trigger phrases ("convert table to JSON", "markdown table to JSON")
   - README.md with installation/usage
   - tests/test-triggers.json with 10 test queries
   - scripts/validate-json-output.sh (deterministic JSON validation)
4. **Spawns Reviewer:** Evaluates artifacts
5. **Reviewer scores:** 29/33 (Deploy threshold) → PASS
6. **Spawns Tester:** Runs self-play tests
7. **Tester results:** 95% trigger accuracy, all functional tests pass → PASS
8. **Orchestrator:** Adds quality scorecard to README.md, commits, pushes
9. **Output to user:** "Skill shipped successfully (iteration 1, score 29/33)"

### Pass Criteria
- ✅ Completes in 1 iteration
- ✅ Review score ≥28/33
- ✅ No blocking issues from Tester
- ✅ Quality scorecard added to README.md
- ✅ Git commit + push successful

---

## Test 2: Revision Path (Review Issues → Designer Fixes → Ship)

**Scenario:** Designer produces initial artifacts with minor issues, Reviewer catches them, Designer fixes, skill ships on iteration 2.

### Setup
- User request: "Create a skill for competitor website analysis"
- Initial Designer output has issues:
  - Missing edge case handling (what if website is down?)
  - No output format template
  - README references "knowledge repo" (SCOPE-3 violation)

### Expected Flow
1. **Iteration 1:**
   - Designer produces initial artifacts
   - Reviewer scores: 24/33 (Revise threshold) → REVISE
   - Reviewer identifies issues:
     - [SQ-B5] Missing edge case handling
     - [SQ-A5] No output format template
     - [SCOPE-3] README has internal org references
   - Orchestrator feeds issues back to Designer

2. **Iteration 2:**
   - Designer revises based on feedback
   - Adds edge case handling section
   - Adds output template with markdown table format
   - Rewrites README for external audience
   - Reviewer scores: 30/33 → PASS
   - Tester: 92% trigger accuracy, no blocking issues → PASS
   - Orchestrator ships

### Pass Criteria
- ✅ Iteration 1 correctly identified issues
- ✅ Designer addressed all issues in iteration 2
- ✅ Final score ≥28/33
- ✅ Shipped after 2 iterations

---

## Test 3: Max Iteration (3 Rounds → Fail)

**Scenario:** Skill requirements are too complex or ambiguous, Designer cannot reach quality bar after 3 iterations.

### Setup
- User request: "Create a skill that handles everything related to project management"
  - Problem: scope is unbounded, requirements are vague
  - Designer struggles with scope boundaries

### Expected Flow
1. **Iteration 1:**
   - Designer produces overly broad skill (scope violations)
   - Reviewer scores: 15/33 (Redesign) → REVISE
   - Issues: SCOPE-2 violations, includes tracking/deployment concerns

2. **Iteration 2:**
   - Designer narrows scope but still includes too much
   - Reviewer scores: 21/33 (Revise) → REVISE
   - Issues: Still has scope creep, missing clear boundaries

3. **Iteration 3:**
   - Designer makes final attempt
   - Reviewer scores: 25/33 (Revise) → REVISE
   - Issues: Improved but still below Deploy threshold

4. **Orchestrator:**
   - Detects 3 iterations exhausted
   - Invokes Iteration Failure Path:
     - Stops iteration
     - Reports failure to user with all 3 iteration reports
     - Presents options: provide more context, simplify scope, or abandon
   - Does NOT silently fail

### Pass Criteria
- ✅ Stops after exactly 3 iterations
- ✅ Does NOT ship skill below quality bar
- ✅ Reports failure to user with full context
- ✅ Offers user options (retry with better inputs / simplify / abandon)
- ✅ Does NOT continue iterating past 3

---

## Test 4: OPSEC Fail (Hardcoded Paths Caught by Reviewer)

**Scenario:** Designer produces skill with OPSEC violations (hardcoded paths), Reviewer catches it as blocking issue.

### Setup
- User request: "Create a skill for daily report generation"
- Designer produces skill with hardcoded paths (negative test — these are BAD examples):
  - `$HOME/Documents/reports/` ← hardcoded user path (VIOLATION)
  - `https://internal-company-url.com/api` ← internal URL (VIOLATION)
  - Organization name "AcmeCorp" in multiple places (VIOLATION)

### Expected Flow
1. **Iteration 1:**
   - Designer produces initial artifacts
   - Reviewer runs OPSEC scan
   - Reviewer detects violations:
     - [OPSEC-1] Hardcoded username path
     - [OPSEC-1] Internal company URL
     - [OPSEC-1] Organization name in skill
   - Reviewer scores: 18/33 (all OPSEC checks fail) → REVISE
   - Issues marked as "blocking" severity

2. **Iteration 2:**
   - Designer removes all hardcoded paths, replaces with variables
   - Removes internal URLs, uses generic examples
   - Removes organization name
   - Reviewer: OPSEC CLEAN, score 28/33 → PASS
   - Tester: PASS
   - Orchestrator ships

### Pass Criteria
- ✅ OPSEC violations caught in review
- ✅ Issues marked as blocking
- ✅ Designer removes all violations
- ✅ Final artifacts have no hardcoded secrets/paths/org names

---

## Test 5: Single Agent Fallback (All Roles in One Session)

**Scenario:** For a simple skill, orchestrator executes all roles in one session (Option 1: role-based execution).

### Setup
- User request: "Create a skill for word count validation"
- Simple skill: takes text input, counts words, validates against target
- No complex subagent coordination needed

### Expected Flow
1. **Orchestrator announces role transitions clearly:**
   - "[Acting as DESIGNER] Generating skill artifacts..."
   - "[Acting as REVIEWER] Evaluating artifacts against rubric..."
   - "[Acting as TESTER] Running self-play tests..."

2. **All work happens in same session:**
   - Designer creates SKILL.md, skill.yml, README.md, tests/
   - Reviewer evaluates and scores (29/33 → PASS)
   - Tester runs trigger + functional tests (PASS)
   - Orchestrator adds scorecard, commits, pushes

3. **Separation of concerns maintained:**
   - Designer does not evaluate its own work
   - Reviewer does not reference requirements discussion
   - Tester tests independently from Designer context

### Pass Criteria
- ✅ Completes in single session (no separate agent spawns)
- ✅ Role boundaries clearly documented
- ✅ Separation of concerns maintained (build ≠ evaluate)
- ✅ Skill passes all quality gates

---

## Test 6: Tool Selection Error Caught by Tester

**Scenario:** Designer selects wrong tool for input type, Tester catches it during functional testing.

### Setup
- User request: "Create a skill for extracting text from PDF URLs"
- Designer mistakenly uses `web_fetch` for PDF extraction (wrong tool)

### Expected Flow
1. **Iteration 1:**
   - Designer produces skill using `web_fetch` on PDF URLs
   - Reviewer: PASS (no tool selection validation in rubric)
   - Tester runs functional test:
     - Attempts to follow skill instructions
     - Tries `web_fetch` on PDF URL
     - Result: gibberish or error (PDFs are binary, not HTML)
     - Tester marks as blocking issue: "Tool selection error — web_fetch cannot parse PDFs"

2. **Iteration 2:**
   - Designer revises to use browser tool or download + pdftotext
   - Tester: functional tests pass, PDF text extracted correctly → PASS
   - Orchestrator ships

### Pass Criteria
- ✅ Tester catches tool selection error empirically
- ✅ Designer fixes tool choice in revision
- ✅ Final skill uses correct tool for input type

---

## Running These Tests

### Manual Execution
For each test scenario:
1. Set up the scenario (user request + any intentional issues)
2. Execute the skill-engineer workflow
3. Observe actual flow vs. expected flow
4. Verify pass criteria

### Automated Validation (Future Enhancement)
These scenarios could be automated with:
- Mock user requests
- Mock Designer outputs (with/without issues)
- Mock Reviewer scores
- Workflow assertions (iteration count, verdicts, etc.)

---

## Test Coverage Summary

| Test | Workflow Path | Key Validation |
|------|--------------|----------------|
| 1. Happy Path | Designer → Reviewer → Tester → Ship | Single iteration success |
| 2. Revision Path | Designer → Reviewer → Designer → Reviewer → Tester → Ship | Iteration with feedback loop |
| 3. Max Iteration | 3 rounds → Fail | Iteration limit + failure reporting |
| 4. OPSEC Fail | OPSEC violation → Caught by Reviewer | Security checks |
| 5. Single Agent Fallback | All roles in one session | Role-based execution |
| 6. Tool Selection Error | Wrong tool → Caught by Tester | Empirical validation |

**Coverage:** Happy path, revision path, failure path, security checks, role separation, tool validation.
