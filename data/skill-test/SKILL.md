---
name: "Skill Test"
description: "Test skills before using or publishing. Trial, compare, evaluate in isolation without affecting your environment."
---

## Test Skills Safely

Two use cases:
1. **Try before commit** — Test drive skills before installing
2. **Evaluate before publish** — Verify quality before publishing

**Key principle:** Test in isolation. Never affect user's environment.

**References:**
- Read `sandbox.md` — Isolated testing environment
- Read `compare.md` — A/B comparison between skills
- Read `evaluate.md` — Multi-agent quality evaluation

---

### Quick Start

**Trial a skill:**
```
sessions_spawn(
  task="Test skill X: Load ONLY its SKILL.md, run [sample task], report quality",
  model="anthropic/claude-haiku"
)
```

**Compare two skills:**
1. Run same task through each (separate sub-agents)
2. Present outputs side-by-side
3. Ask: "Which works better? Why?"

---

### Test Modes

**Trial Mode** — Before installing
- Spawn sub-agent with ONLY the test skill
- Run 2-3 representative tasks
- Evaluate: Does it help? Clear instructions?
- Decision: keep, pass, or try another

**Evaluation Mode** — Before publishing
- Spawn specialized reviewers (see `evaluate.md`)
- Check structure, safety, usefulness
- Synthesize findings
- Recommend improvements

---

### Sandbox Isolation

⚠️ Never load test skill into your main context.

**Sub-agent approach (recommended):**
```
sessions_spawn(
  task="You have ONE skill loaded: [skill content]. Test by doing: [task]",
  model="anthropic/claude-haiku"
)
```
- Complete isolation — main session unaffected
- Natural cleanup — sub-agent terminates, done
- Cheap testing — use Haiku

**What to check:**
- Does it activate correctly?
- Are instructions clear?
- Token cost reasonable?
- Output quality acceptable?

---

### Edge Cases

**Skill requires credentials:** Ask user for test credentials or skip auth-dependent features.

**Skill not found:** Verify slug with `npx clawhub info <slug>` before testing.

**Test fails mid-way:** Sub-agent terminates cleanly. Review logs, adjust test task, retry.

**Skill has many auxiliary files:** Load SKILL.md first, reference others only if needed during test.

---

*Test thoroughly. Install only after explicit user approval.*
