# Memory Setup — Call Center

## Initial Setup

Create directory on first use:
```bash
mkdir -p ~/call-center/scripts
touch ~/call-center/memory.md
touch ~/call-center/escalations.md
touch ~/call-center/metrics.md
```

## memory.md Template

Copy to `~/call-center/memory.md`:

```markdown
# Call Center Memory

## Active Calls
<!-- Current call in progress -->
| Time | Caller | Issue | Status |
|------|--------|-------|--------|

## Recent Interactions
<!-- Last 10 calls for pattern recognition -->
| Date | Caller | Type | Resolution | Duration |
|------|--------|------|------------|----------|

## Open Follow-ups
<!-- Promised callbacks or pending actions -->
| Due | Caller | Promise | Ref# |
|-----|--------|---------|------|

## Known Issues
<!-- Recurring problems to watch for -->
- [Issue]: [Quick resolution or escalation path]

## Caller Preferences
<!-- VIP or frequent callers with notes -->
| Caller | Preference | Notes |
|--------|------------|-------|

---
*Last: YYYY-MM-DD*
```

## escalations.md Template

Copy to `~/call-center/escalations.md`:

```markdown
# Escalation Log

## Pending Escalations
| Date | Caller | Issue | Escalated To | Status |
|------|--------|-------|--------------|--------|

## Escalation Patterns
<!-- Issues that frequently escalate — candidates for process improvement -->
| Issue Type | Frequency | Root Cause | Suggested Fix |
|------------|-----------|------------|---------------|

## Escalation Contacts
| Department | Contact | Hours | Use For |
|------------|---------|-------|---------|
| Supervisor | [Name] | 9-5 | Customer requests, auth issues |
| Technical | [Team] | 24/7 | System outages, bugs |
| Billing | [Team] | 9-6 | Disputes, refunds >$X |
| Legal | [Contact] | By appt | Threats, compliance |

---
*Last: YYYY-MM-DD*
```

## metrics.md Template

Copy to `~/call-center/metrics.md`:

```markdown
# Call Center Metrics

## Daily Stats
| Date | Calls | FCR% | Avg Handle | Escalations | CSAT |
|------|-------|------|------------|-------------|------|

## Weekly Summary
| Week | Total Calls | FCR% | Top Issues | Notes |
|------|-------------|------|------------|-------|

## Issue Categories
| Category | This Week | Trend | Notes |
|----------|-----------|-------|-------|
| Billing | | | |
| Technical | | | |
| Account | | | |
| Product | | | |

---
*Last: YYYY-MM-DD*
```
