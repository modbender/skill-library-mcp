# Token Saver 75+ (OpenClaw Skill)

Cut token usage **75%+** while preserving high intelligence.

This skill is a **behavioral protocol**: it forces concise, high-signal outputs, reduces unnecessary tool calls, and prunes context usage. It's designed for *always-on* use.

---

## What it does

- **Auto-classifies requests** into tiers (T1-T4) and applies the tightest output budget that still preserves correctness.
- **Routes execution** to the cheapest capable model via `sessions_spawn` (e.g., free Groq for bulk, Codex for code, Opus only for T4 strategy).
- Enforces **dense output templates** (STATUS / CHOICE / CAUSE->FIX->VERIFY / RESULT).
- Adds **tool gating** to prevent "just in case" tool calls.
- Adds **context pruning rules** to avoid re-reading and to prefer partial reads.
- Preserves intelligence via **explicit escalation** when depth is required.

---

## Install

```bash
npx clawhub install token-saver-75plus
```

Then reference it in your `AGENTS.md` or system prompt:

```markdown
## Mandatory: Token Optimization
Every session, read `skills/token-saver-75plus/SKILL.md` and follow its tier classification (T1-T4) for every request.
```

---

## Use

You don't need a special command. The skill is meant to be **always-on** once installed.

Recommended trigger phrases (optional):
- "Optimize for token efficiency."
- "Be dense."
- "No fluff."
- "Give me the minimal correct answer."

---

## Request tiers (silent)

| Tier | Typical requests | Output budget |
|---|---|---|
| **T1** | yes/no, tiny status, trivial facts | 1-3 lines |
| **T2** | summaries, how-to, small decisions | 5-15 bullets |
| **T3** | debugging, strategy, multi-step analysis | structured sections, <400 words |
| **T4** | creative/longform/deep research | longer allowed, still dense |

If the user says **"why / explain / go deep"**, the skill temporarily relaxes compression for that response.

---

## Model routing

The skill includes an opinionated routing table. Adapt the model IDs to your setup:

| Role | Default model | Cost |
|---|---|---|
| Bulk/formatting | `groq/llama-3.1-8b-instant` | FREE |
| Code generation | `openai/gpt-5.3-codex` | $$$ |
| Structured analysis | `openai/gpt-5.2` | $$$ |
| Strategy/T4 only | `anthropic/claude-opus-4-6` | $$$$ |

**Rule:** Never retry the same model on failure. Escalate to the next tier.

---

## Output templates

Use these to stay concise:

- **STATUS:** `OK/WARN/FAIL` one-liner
- **CHOICE:** `A vs B -> Recommend: X` (1 line)
- **CAUSE->FIX->VERIFY** (3 bullets max)
- **RESULT:** output/data directly (no wrap-up)

---

## Tool gating rules

Before any tool call:
1. **Already known?** No tool.
2. **Batchable?** Parallelize.
3. **Cheapest?** `memory_search > partial read > full read > web`
4. **Needed?** Don't fetch "just in case."

---

## Measurement

Only when explicitly testing, append:

```
[~X tokens | Tier: Tn | Savings: High]
```

---

## License

MIT
