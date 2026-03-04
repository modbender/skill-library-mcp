# Sub-Agent Performance Log

## How to Use
- **Before delegating:** Check if this agent has failed on similar tasks
- **After delegating:** Log outcome, quality score, lessons learned

## Scoring
- **Quality:** 1-5 (did output meet expectations?)
- **Outcome:** SUCCESS | PARTIAL | FAILED | CRASHED

---

## Agent: [Name] — [Cost Tier]

### Performance Summary
| Metric | Value |
|--------|-------|
| Tasks | 0 |
| Success Rate | — |
| Avg Quality | — |
| Best For | ... |
| Avoid For | ... |

### Task History

#### YYYY-MM-DD | task-name | OUTCOME
- **Task:** Description
- **Outcome:** What happened
- **Quality:** X/5
- **Lesson:** What to remember

---

## Decision Heuristics

### When to delegate vs. do it yourself:
- **< 2 steps** → Do it yourself
- **Large data processing** → Write a script, don't delegate to LLM
- **Web research** → Balanced-tier agent
- **Code/apps** → Capable-tier agent
- **Quick checks** → Cheap-tier agent

### Known Failure Modes:
1. Large context (>100K tokens) crashes most agents → use scripts
2. Sub-agents can't always write files → verify output exists
3. Sub-agents don't push-notify → always schedule follow-up checks

### Trust Tiers:
- **High Trust:** Auto-accept output (simple, well-understood tasks)
- **Medium Trust:** Spot-check output (standard tasks)
- **Low Trust:** Always verify (novel tasks, sensitive data)
