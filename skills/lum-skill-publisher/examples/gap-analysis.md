# Gap Analysis Examples

## Real Example: ClawSaver (Feb 2026)

### Draft vs. Final

| Dimension | Draft | Final |
|-----------|-------|-------|
| Description line | Backronym-first, 80+ words | Value-first, ≤160 chars ✅ |
| "When to use" | Missing | Explicit do/don't list ✅ |
| Trigger detection | Missing | Trigger phrases table ✅ |
| Word count | ~800 (too long) | 600 (in range) ✅ |
| Tables vs. prose | Prose-heavy | Table-first ✅ |
| Safety section | Present | Kept + explicit opt-outs added ✅ |
| Version history | Missing | Added ✅ |
| Examples file | None | examples/batch-decisions.md ✅ |
| Attribution | Missing | Footer links added ✅ |

### Key Insight from This Exercise
The original draft led with the backronym (CLAVSAVER: Combines Linked Asks...) in the description. This is a common mistake — clever names belong in the README body, not the description field that appears in search results. Buyers scan descriptions for outcomes ("30% cheaper") not naming patterns.

---

## Scoring Rubric

**5/5 — Publish-ready:**
- Description ≤160 chars, value-first ✅
- "When to use" present ✅
- Tables over prose ✅
- Safety section ✅
- Version history ✅

**4/5 — Minor patches needed:**
- One section missing (usually version history or safety)
- Description slightly long or feature-first

**3/5 — Draft quality:**
- Missing "when to use"
- Prose-heavy, no tables
- No examples

**2/5 — Idea stage:**
- Has a description but little structure
- No commands or trigger detection

**1/5 — Don't publish yet:**
- No clear value proposition
- No "when to use"
- No safety model

---

## Description Line Rewrites

| Before | After | Why |
|--------|-------|-----|
| "ClawSaver — Combines Linked Asks into Well-structured Sets for Affordable, Verified, Efficient Responses" | "Reduce AI costs by batching related asks into fewer responses. ~30–50% fewer API calls, no quality loss." | Value-first, specific, ≤160 chars |
| "Universal LLM Token Manager with proactive monitoring and analytics." | ✅ Already good — describes function clearly | Outcome implied by "Universal" + analytics |
| "First OpenClaw skill where AI agents can autonomously pay for Pro features via x402 protocol." | The x402 angle is the differentiator — keep it, but lead with the problem solved | Feature-first, but the feature IS the story here |
