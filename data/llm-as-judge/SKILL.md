---
name: llm-as-judge
description: Cross-model verification pattern. Spawn a judge subagent with a different model to review plans, code, or decisions before execution. Catches ~85% of issues vs ~60% for self-reflection.
---

# LLM-as-Judge

**Core principle:** Same model = same blind spots. Different model = fresh perspective. Cross-model review catches ~85% of issues vs ~60% for self-reflection.

## When to Use

**High-Value Scenarios:**
- Complex planning (architecture decisions, multi-file changes)
- High-stakes code review (production deployments, security-critical)
- Ambiguous requirements (need clarification on approach)
- Before major commits (prevent rollbacks)
- When stuck after 3+ attempts (fundamental approach may be wrong)

**Decision Matrix:**
```
Task Complexity    Stakes    Recommended Judge
─────────────────────────────────────────────────
Low               Any       Self-review sufficient
Medium            Low       Self-review
Medium            High      LLM-as-Judge (optional)
High              Any       LLM-as-Judge (required)
Stuck >3x         Any       LLM-as-Judge (required)
```

**Cost/Benefit:**
- **Cost:** 2x tokens on planning/review phase (usually <10% of total task cost)
- **Benefit:** Prevents expensive re-work, catches blind spots
- **ROI:** Spending 20¢ to save $2 of wasted execution

---

## The Pattern

### Basic Flow
```
Executor (Model A) → Output → Judge (Model B) → Verdict → Action
```

**Verdict Options:**
- **APPROVE:** Proceed with execution
- **REVISE:** Specific feedback provided, executor revises
- **REJECT:** Fundamental issue, restart with different approach

### Model Pairing Strategy

**Recommended Pairings:**

| Executor | Judge | Why It Works |
|----------|-------|--------------|
| Claude Sonnet | Kimi k2.5 | Different architectures, reasoning styles |
| GPT-4 | Claude Opus | Safety vs. creativity balance |
| Kimi k2.5 | Claude Sonnet | Long context vs. structured output |
| MiniMax | Kimi/Claude | Cheap execution, quality review |

**Principles:**
- Different provider (OpenAI ↔ Anthropic ↔ Moonshot)
- Different training data and biases
- Different reasoning patterns
- Similar capability tier

---

## Judge Prompt Templates

### Template 1: Plan Review

```markdown
You are a senior engineering manager reviewing a work plan.
Be critical but constructive. Your goal is to catch gaps and risks.

## Evaluation Criteria (0-10 each):

1. **Completeness** - All files identified? Dependencies mapped?
2. **Feasibility** - Timeline realistic? Unknown unknowns considered?
3. **Risk Awareness** - What could go wrong? Mitigation plans?
4. **Testing Strategy** - How to verify? Edge cases covered?

## Required Output:

**Verdict:** [APPROVE / REVISE / REJECT]

**Scores:**
- Completeness: X/10
- Feasibility: X/10
- Risk Awareness: X/10
- Testing Strategy: X/10

**Issues:** (list if any score < 7)
**Recommendations:** (specific actionable suggestions)
```

### Template 2: Code Review

```markdown
You are a staff engineer conducting production code review.

## Review Checklist:
**Correctness:** Logic correct? Edge cases? Error paths?
**Design:** Follows patterns? Appropriate abstractions?
**Safety:** No vulnerabilities? Input validation? Safe data handling?
**Maintainability:** Clear names? Testable? Documented?

## Verdict: [APPROVE / REVISE / REJECT]

**Critical Issues:** (must fix)
**Major Issues:** (should fix)
**Minor Issues:** (nice to have)
```

---

## Implementation Examples

### Example 1: Complex Feature Implementation

```markdown
User: "Implement JWT authentication for our API"

Executor (Claude): Creates implementation plan
↓
Spawns Judge (Kimi)
↓
Judge Review:
- Score: 7/10 completeness (missing refresh token logic)
- Score: 8/10 feasibility
- Score: 6/10 risk awareness (didn't mention token storage security)
- Score: 5/10 testing (no tests for edge cases)
↓
Verdict: REVISE
↓
Feedback: "Add refresh token flow, consider XSS protection, add tests for expired tokens"
↓
Executor revises → Re-judge → APPROVED → Execute
```

### Example 2: Architecture Decision

```markdown
User: "Should we migrate from REST to GraphQL?"

Executor (Kimi): Researches, proposes migration plan
↓
Spawns Judge (Claude)
↓
Judge Review:
- Questions: "Have you considered the learning curve for the team?"
- Alternative: "What about tRPC for type safety without GraphQL complexity?"
- Risk: "Migration timeline doesn't account for debugging production issues"
↓
Verdict: REVISE
↓
Output: More nuanced decision with alternatives comparison
```

---

## Integration with Other Patterns

### With Planning Protocol
```
Phase 1: GATHER → Phase 2: PLAN + LLM-as-Judge review → Phase 3: EXECUTE
```
Judge reviews the plan before any code is written.

### With Subagent-Driven Development
```
Implementer subagent → Judge subagent (spec compliance) → Judge subagent (quality) → Merge
```
Two-stage review: first checks if it matches spec, second checks code quality.

### With Verification Loops
```
Pre-commit: Self-review → LLM-as-Judge review → Human review (if high stakes)
```
Layered verification for critical changes.

---

## Quick Reference

**One-liner:**
```
When in doubt, spawn a judge with a different model.
```

**Decision tree:**
- Simple task? → Self-review
- Complex or high stakes? → LLM-as-Judge
- Stuck after retries? → LLM-as-Judge for fresh perspective
- Production code? → LLM-as-Judge + human review

**Default pairing:**
- Fast/cheap executor (MiniMax) + Quality judge (Kimi/Claude)

---

## Anti-Patterns

❌ **Don't** use same model for executor and judge (same blind spots)
❌ **Don't** judge low-complexity tasks (overhead not worth it)
❌ **Don't** ignore judge feedback without consideration
❌ **Don't** use LLM-as-judge for final deployment decisions (human required)
❌ **Don't** skip self-review entirely (judge is enhancement, not replacement)

✅ **Do** use different providers/models
✅ **Do** provide clear criteria to the judge
✅ **Do** iterate when judge finds issues
✅ **Do** log judge feedback for pattern learning
✅ **Do** combine with other verification methods

---

## Measuring Effectiveness

**Track these metrics:**
- Issues caught by judge vs. issues found in production
- Revision rate (how often judge requests changes)
- Time saved (prevented re-work vs. review overhead)
- User satisfaction (confidence in final output)

**Target thresholds:**
- Judge approval rate: 60-70% (too high = not critical enough, too low = quality issues)
- Production issues prevented: >50% reduction in post-deployment bugs
- Review overhead: <15% of total task time

---

*The LLM-as-Judge pattern acknowledges that even the best AI agents have blind spots. A second pair of eyes—especially one with different training—catches what the first misses.*
