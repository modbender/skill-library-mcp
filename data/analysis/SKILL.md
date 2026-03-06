---
name: Analysis
description: Run deep system health checks across workspace, config, skills, and integrations with prioritized findings and remediation.
---

## When To Use

Trigger when user says: "check my system", "what's wrong", "health check", "diagnose", "audit", "why is X slow", "something feels off"

This is NOT generic data analysis. This is **system self-diagnosis** — examining the agent's own workspace, configuration, and operational health.

---

## Analysis Modes

| Mode | Scope | When |
|------|-------|------|
| **Quick** | Security + critical operational | "Quick check", default if unspecified |
| **Full** | All categories, all checks | "Full audit", "deep check" |
| **Targeted** | Single category | "Check my memory", "audit cron" |

---

## Priority Order (Always This Sequence)

1. **SECURITY** — Exposed secrets, leaked credentials, permission issues
2. **OPERATIONAL** — Broken crons, dead sessions, unreachable APIs
3. **HYGIENE** — Memory bloat, orphan files, stale entries, inefficiencies

Stop and report critical security findings immediately. Don't bury them in a long list.

---

## Detection Strategy

**Cheap first, expensive only when needed:**
1. File checks (free) — existence, size, age, syntax
2. Local commands (cheap) — process lists, disk usage, git status
3. API calls (expensive) — only when file-level signals warrant

Never hit external APIs speculatively. Validate need from local evidence first.

---

## Findings Format

```
[CRITICAL|WARNING|INFO] category/subcategory: description
  → Action: specific remediation step
  → Auto-fixable: yes/no
```

Group by severity, not by category. User sees worst problems first.

---

## Load Detailed Checks

| Category | Reference |
|----------|-----------|
| All check definitions by category | `checks.md` |
| Remediation actions and auto-fix scripts | `remediation.md` |
| Tracking analysis runs, improvement over time | `tracking.md` |
