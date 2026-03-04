# Memory Template — Groq API Inference

Create `~/groq-api/memory.md` with this structure:

```markdown
# Groq API Inference Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined
credentials_verified: no | yes

## Context
<!-- What the user is building and why -->
<!-- Example: Building low-latency support chat with strict JSON output -->

## Defaults
<!-- Preferred model routing and request profile -->
<!-- Example: Route interactive chat to fast profile, heavy reasoning to quality profile -->

## Reliability
<!-- Retries, timeout limits, fallback model choices -->
<!-- Example: max_retries 3, fallback enabled, timeout 30s -->

## Notes
<!-- Observations from real usage -->
<!-- Example: 429 spikes during peak traffic; add jitter to retries -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning usage patterns | Keep refining defaults |
| `complete` | Stable workflow configured | Execute with minimal questions |
| `paused` | User said not now | Avoid setup questions |
| `never_ask` | User rejected setup | Never request new setup details |

## Credentials States

| Value | Meaning | Action |
|-------|---------|--------|
| `no` | Not yet validated | Verify with `/models` request |
| `yes` | Verified and working | Proceed with normal operations |

## Key Principles

- Keep secrets in environment variables only.
- Record routing logic, not private payloads.
- Update `last` on each meaningful Groq session.
- Prefer short notes that improve future decisions.
