# 🛡️ Skill Shield Report: skill

**Scanner:** skill-shield v0.2.0 (65 patterns)
**Scan time:** 2026-02-20T17:11:46.951721+00:00
**Path:** `/home/lyall/.openclaw/workspace/agents-workspace/skill-shield/skill`

## Rating: 🟠 D

> High risk — critical patterns detected, manual review required

## Permission Audit

**Declared in SKILL.md:** exec, process
**Found in code:** browser, canvas, cron, edit, exec, gateway, memory_get, memory_search, message, nodes, process, read, sessions_history, sessions_list, sessions_send, sessions_spawn, subagents, tts, web_fetch, web_search, write
**Declaration coverage:** 2/21

### ⚠️ Undeclared Permissions

| Tool | Sensitivity | Recommendation |
|------|------------|----------------|
| browser | 🔴🔴🔴🔴 (4/5) | ⚠️ High-sensitivity tool 'browser' used but not declared — requires justification |
| canvas | 🔴🔴 (2/5) | Add 'canvas' to SKILL.md permissions |
| cron | 🔴🔴🔴 (3/5) | Add 'cron' to SKILL.md permissions |
| edit | 🔴🔴🔴🔴 (4/5) | ⚠️ High-sensitivity tool 'edit' used but not declared — requires justification |
| gateway | 🔴🔴🔴🔴🔴 (5/5) | ⚠️ High-sensitivity tool 'gateway' used but not declared — requires justification |
| memory_get | 🔴🔴 (2/5) | Add 'memory_get' to SKILL.md permissions |
| memory_search | 🔴🔴 (2/5) | Add 'memory_search' to SKILL.md permissions |
| message | 🔴🔴🔴 (3/5) | Add 'message' to SKILL.md permissions |
| nodes | 🔴🔴🔴🔴 (4/5) | ⚠️ High-sensitivity tool 'nodes' used but not declared — requires justification |
| read | 🔴🔴 (2/5) | Add 'read' to SKILL.md permissions |
| sessions_history | 🔴🔴 (2/5) | Add 'sessions_history' to SKILL.md permissions |
| sessions_list | 🔴🔴 (2/5) | Add 'sessions_list' to SKILL.md permissions |
| sessions_send | 🔴🔴🔴 (3/5) | Add 'sessions_send' to SKILL.md permissions |
| sessions_spawn | 🔴🔴🔴 (3/5) | Add 'sessions_spawn' to SKILL.md permissions |
| subagents | 🔴🔴🔴 (3/5) | Add 'subagents' to SKILL.md permissions |
| tts | 🔴 (1/5) | Add 'tts' to SKILL.md permissions |
| web_fetch | 🔴🔴🔴 (3/5) | Add 'web_fetch' to SKILL.md permissions |
| web_search | 🔴🔴 (2/5) | Add 'web_search' to SKILL.md permissions |
| write | 🔴🔴🔴🔴 (4/5) | ⚠️ High-sensitivity tool 'write' used but not declared — requires justification |

**Undeclared risk score:** 54

## Findings (1 total)

| Severity | Pattern | CWE | File | Line | Context |
|----------|---------|-----|------|------|---------|
| Medium (3) | base64 decode call | CWE-116 | scan.py | 253 | `decoded = base64.b64decode(candidate).decode("utf-8", errors="replace"` |

## CWE References

- [CWE-116](https://cwe.mitre.org/data/definitions/116.html)

## Summary by Category

- **obfuscation**: 1
