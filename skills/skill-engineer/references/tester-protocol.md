# Tester Protocol

Complete testing protocol for the Tester role in the skill-engineer workflow.

---

## Role Definition

**Purpose:** Empirical validation via self-play. The Tester loads the skill and attempts realistic tasks.

### Inputs
- Skill artifacts (SKILL.md, skill.yml, README.md, tests/, scripts/, references/)
- Test protocol (this document)

### Outputs
- Test report with:
  - Trigger test results (accuracy percentage)
  - Functional test results (pass/fail for each scenario)
  - Edge case findings
  - Blocking issues list
  - Non-blocking issues list
  - Verdict: PASS / FAIL

### Constraints
- Follow skill instructions exactly as written (don't assume or infer)
- Test as if you've never seen the requirements discussion
- Note every point of confusion or ambiguity
- Distinguish blocking vs. non-blocking issues

---

## Test Protocol

### 1. Trigger Tests

**Purpose:** Verify the skill loads when it should and doesn't load when it shouldn't.

**Method:**
- Prepare 10+ queries that SHOULD trigger the skill (based on description field)
- Prepare 5+ queries that should NOT trigger it (semantically similar but out of scope)
- Run each query and observe if skill auto-loads
- Calculate accuracy: (true positives + true negatives) / total queries

**Example test set for a "competitor-analysis" skill:**

Should trigger:
- "Analyze acme.com and compare to our product"
- "competitor research for beta.io"
- "what's the competitive landscape?"

Should NOT trigger:
- "I'm competitive in nature"
- "analyze our internal performance"
- "competitor sales team info"

**Pass threshold:** ≥90% accuracy

### 2. Functional Tests

**Purpose:** Verify the skill produces correct outputs when following instructions.

**Method:**
- Select 2-3 realistic use cases
- For each use case:
  1. Load the skill
  2. Follow instructions step-by-step
  3. Note any confusion points
  4. Verify output matches specified format
  5. Check edge case handling

**What to observe:**
- Does the skill provide clear guidance at every step?
- Are outputs in the specified format?
- Did edge cases cause confusion?
- Were tool selections appropriate?
- Did you have to guess or infer anything?

**Functional test scenarios should cover:**
- Happy path (ideal inputs, normal execution)
- Missing inputs (what happens if optional data is absent?)
- Boundary cases (skill scope edge)

### 3. Edge Case Tests

**Purpose:** Stress-test the skill's instructions.

**Test categories:**
- Missing required inputs
- Ambiguous requirements
- Tasks at the boundary of the skill's scope
- Tool failures or API errors
- Unexpected data formats

**What to capture:**
- Does the skill have error handling instructions?
- Are edge cases explicitly addressed?
- Did you get stuck or have to improvise?

---

## Result Format

```markdown
## Test Report

**Iteration:** N
**Verdict:** PASS / FAIL

### Trigger Tests
- Queries tested: X
- True positives: X/X
- True negatives: X/X
- Trigger accuracy: X%

### Functional Tests

#### Test 1: [task description]
- **Result:** pass/fail
- **Notes:** [what worked, what didn't]
- **Confusion points:** [where instructions were unclear]

#### Test 2: [task description]
- **Result:** pass/fail
- **Notes:** [...]

### Edge Cases
- [case]: [result]

### Blocking Issues
1. [description] — must fix before ship

### Non-Blocking Issues
1. [description] — nice to fix
```

---

## Issue Classification

### Blocking Issues
Issues that prevent the skill from functioning correctly. Must be fixed before shipping.

**Examples:**
- Missing required file (SKILL.md, skill.yml)
- Contradictory instructions ("do X" in step 2, "never do X" in step 5)
- References to non-existent files or tools
- No error handling for common failure modes
- Output format undefined or ambiguous
- Trigger accuracy <80%

### Non-Blocking Issues
Issues that impact quality but don't prevent basic functionality.

**Examples:**
- Suboptimal wording
- Missing examples for advanced features
- Minor formatting inconsistencies
- Trigger accuracy 80-89%
- Edge case handling could be clearer

---

## Test Scenarios by Skill Category

### Category 1: Document & Asset Creation

**Functional tests:**
- Create output with all required sections
- Verify output matches template
- Test with missing optional inputs

**Edge cases:**
- Empty inputs
- Very long inputs (token limit stress)
- Special characters in inputs

### Category 2: Workflow Automation

**Functional tests:**
- Complete full workflow from start to finish
- Test iteration/feedback loop (if applicable)
- Verify validation gates work

**Edge cases:**
- Step failure (what happens if step 3 fails?)
- Missing intermediate outputs
- Max iteration boundary (does it fail gracefully?)

### Category 3: MCP Enhancement

**Functional tests:**
- Execute multi-step MCP workflow
- Verify error handling for API failures
- Test retry logic

**Edge cases:**
- MCP server unavailable
- Rate limiting
- Invalid API responses

---

## Tester Checklist

Before submitting test report:

- [ ] Ran all trigger tests (10+ should-trigger, 5+ should-not-trigger)
- [ ] Calculated trigger accuracy percentage
- [ ] Completed 2-3 functional test scenarios
- [ ] Documented confusion points (if any)
- [ ] Tested at least 3 edge cases
- [ ] Classified issues as blocking vs. non-blocking
- [ ] Verified output format matches specification
- [ ] Noted tool selection appropriateness
- [ ] Did NOT reference requirements discussion (test independence)
- [ ] Provided verdict (PASS if no blocking issues + ≥90% trigger accuracy)

---

## Verdict Decision Tree

```
Start
  │
  ├─ Blocking issues found? ──YES──→ FAIL
  │                            │
  │                           NO
  │                            │
  ├─ Trigger accuracy <90%? ──YES──→ FAIL
  │                            │
  │                           NO
  │                            │
  ├─ Major confusion in ≥2 ──YES──→ FAIL
  │  functional tests?         │
  │                           NO
  │                            │
  └─────────────────────────→ PASS
```

---

## Self-Play Best Practices

**1. Fresh context**
Test with minimal knowledge of the requirements discussion. Approach the skill as a stranger.

**2. Follow literally**
Don't infer or fill gaps. If instructions are unclear, that's a finding.

**3. Document confusion**
Every time you pause and think "wait, what does this mean?" — write it down.

**4. Test realistic scenarios**
Use cases should mirror actual agent usage, not just toy examples.

**5. Check output format rigorously**
If skill says "output JSON", verify the JSON is valid and matches schema.

**6. Note tool choices**
If skill picks `web_fetch` for a PDF URL, that's a tool selection error.

---

## Iteration Strategy (Anthropic Recommended)

When testing during skill development:

1. **Start with ONE challenging task**
2. **Iterate until agent succeeds consistently** (max 3 iterations)
3. **Extract the winning approach into the skill**
4. **Then expand to multiple test cases for coverage**

This focuses effort on getting one thing right before scaling to full coverage.
