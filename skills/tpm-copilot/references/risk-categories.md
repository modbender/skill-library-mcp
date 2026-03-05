# Risk Categories & Severity

## Severity Levels

### 🔴 Critical
- Program timeline at immediate risk
- Blocking multiple teams
- Requires executive escalation
- Examples: key person departure, critical dependency failure, security incident

### 🟠 High
- Likely to cause delay if not addressed within 1-2 days
- Blocking at least one team member
- Examples: blocked tickets, CI failures on main, missed sprint commitments

### 🟡 Medium
- Could cause delay if not addressed within a sprint
- Quality or velocity concern
- Examples: stale tickets, PR review bottlenecks, scope creep

### 🔵 Low
- Informational, worth tracking
- No immediate impact
- Examples: tech debt accumulation, minor process gaps

## Auto-Detected Risk Categories

| Category | Source | Default Severity | Trigger |
|----------|--------|-----------------|---------|
| `blocker` | Jira/Linear | High | Ticket status = Blocked |
| `delivery` | Jira/Linear | Medium | N+ stale tickets in sprint |
| `scope` | Jira/Linear | Medium | 5+ tickets added mid-sprint |
| `review_bottleneck` | GitHub | Medium | PRs open > threshold hours |
| `ci` | GitHub | High | 2+ consecutive CI failures on main |
| `dependency` | Jira links | High | Upstream dependency not complete |

## Manual Risk Entry

Add to `programs/<name>/risks/register.json`:
```json
{
  "id": "RISK-MANUAL-001",
  "severity": "high",
  "category": "resource",
  "title": "Senior engineer on PTO weeks 10-11, no backup for auth service",
  "detected_at": "2026-02-24",
  "source": "manual",
  "status": "open",
  "mitigation": "Cross-training session scheduled for week 9",
  "owner": "Alice"
}
```

## Risk Lifecycle
1. **Detected** — auto-scan or manual entry
2. **Open** — actively being tracked
3. **Mitigated** — mitigation in place, monitoring
4. **Resolved** — no longer a risk
5. **Accepted** — acknowledged, no action planned
