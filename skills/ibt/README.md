# IBT v2.7.1 — Instinct + Behavior + Trust

Deterministic execution discipline for agents with an **instinct layer** — pre-execution observation, takes, and genuine opinions. v2.7 adds **error resilience** — timeout handling, checkpointing, and decision logging.

## ⚠️ Privacy Note

**All checkpoints and decision logs are stored IN-MEMORY ONLY.**
- Lost immediately when the session ends
- Never persisted to disk
- Never sent to any external service
- Not readable by anyone other than the agent during the session

**Always redact sensitive data before logging:**
- API keys, tokens, passwords → log `[REDACTED]` or hash only
- Personal info → log `[PII]`
- Never log full credentials or raw API responses with secrets

## Why IBT v2.7?

IBT v1 handled reliability. IBT v2 adds agency. IBT v2.2 adds OpenClaw integration. IBT v2.3 adds trust. IBT v2.5 adds human ambiguity handling. IBT v2.7 adds **error resilience** — structured timeout handling, checkpointing for resume, and decision logging for audit.

## What's Included

| File | Description |
|------|-------------|
| SKILL.md | Complete skill definition (v1 + v2 + v2.2 + v2.3 + v2.5 + v2.7) |
| POLICY.md | Instinct layer rules |
| TEMPLATE.md | Full drop-in policy |
| EXAMPLES.md | Before/after demonstrations |

## Core Loop

**Observe → Parse → Plan → Commit → Act → Verify → Update → Stop**

### Quick Reference

1. **Observe** — Pre-execution pause (Notice, Take, Hunch, Suggest)
2. **Parse** — Extract goals, understand WHAT must be true
3. **Plan** — Shortest verifiable path
4. **Commit** — Commit before acting + checkpoint
5. **Act** — Execute with timeout enforcement
6. **Verify** — Evidence-based checks + error classification
7. **Update** — Patch smallest failed step + decision log
8. **Stop** — Stop when done or blocked

### Key Features

- **Human Ambiguity**: When unclear, ask — don't assume
- **Trust Contract**: Define relationship explicitly
- **Session Realignment**: After gaps, summarize where you left off
- **Stop = Stop**: Always halt when asked
- **Error Resilience**: Timeout, checkpoint, decision log (v2.7)

## Error Codes (v2.7)

| Code | Type | Action |
|------|------|--------|
| 1 | TIMEOUT | Retry max 2, then ask human |
| 2 | AUTH | Stop immediately, alert human |
| 3 | RATE | Wait 60s, retry max 2 |
| 4 | PARSE | Retry once, then skip |
| 0 | UNKNOWN | Stop, alert human |

## Install

```bash
clawhub install ibt
```

## License

MIT
