# Severity & Triage Reference

## Triage Priority

1. **CRITICAL + VERIFIED** — Fix immediately, confirmed exploitable
2. **HIGH + VERIFIED/LIKELY** — Fix before deployment
3. **Any + PATTERN_MATCH** — Verify manually (keyword matches, may be false positives)
4. **NEEDS_REVIEW** — Low priority, check when time permits

## Confidence Levels

| Level | Meaning | Action |
|-------|---------|--------|
| VERIFIED | Confirmed with code reading, multiple evidence, or PoC | Report as finding |
| LIKELY | Strong code evidence, no PoC | Report as finding |
| PATTERN_MATCH | Keyword/regex match only | Flag for human review |
| NEEDS_REVIEW | Inconclusive | Low priority review |

## Severity Definitions

| Level | CVSS | Response |
|-------|------|----------|
| CRITICAL | 9.0-10.0 | Stop and fix immediately |
| HIGH | 7.0-8.9 | Fix before deployment |
| MEDIUM | 4.0-6.9 | Schedule fix this week |
| LOW | 0.1-3.9 | Note for later |
| INFO | 0.0 | Best practice, optional |

## Identifying False Positives

- **Library-handled:** JWT/crypto flagged but jose/bcrypt/passport handles it correctly
- **Environment-gated:** Dev-only issue flagged as production risk
- **Database-protected:** Race condition flagged but UNIQUE constraints prevent it
- **Pattern match only:** Keyword like "eval" or "exec" but usage is safe
