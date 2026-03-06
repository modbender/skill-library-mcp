# Analysis Tracking & Self-Improvement

## Run History

Track each analysis run to identify patterns:

```
analysis-log.json:
{
  "runs": [
    {
      "timestamp": "2026-02-12T10:00:00Z",
      "mode": "quick|full|targeted",
      "duration_seconds": 45,
      "findings": {
        "critical": 0,
        "warning": 2,
        "info": 5
      },
      "categories_checked": ["workspace", "config"],
      "auto_fixed": 1,
      "user_action_required": 2
    }
  ]
}
```

---

## Pattern Detection

After 5+ runs, analyze patterns:

### Recurring Issues
- Same warning appearing in >50% of runs → systemic problem, needs architectural fix
- Same critical appearing twice → immediate escalation, something isn't getting fixed

### Improvement Signals
- Issue count trending down → system getting healthier
- Same category always clean → reduce check frequency for it
- Specific check always passes → consider removing (noise)

### Cost Efficiency
- Track which checks take longest
- Track which checks find issues most often
- Prioritize high-value checks, deprioritize expensive+low-yield

---

## Feedback Integration

When user provides feedback on findings:

### False Positives
- User says "that's not actually a problem"
- Action: Add exception rule for that specific case
- Example: "Large memory/ is intentional" → skip size warning for this workspace

### Missed Issues
- User found problem that analysis didn't catch
- Action: Add new check to `checks.md`
- Example: "You didn't notice my Cloudflare token expired" → add token expiry check

### Priority Disagreement
- User says "that's not critical, it's just a warning"
- Action: Adjust severity in check definition
- Example: "Zombie sessions aren't urgent for me" → downgrade to WARNING

---

## Scheduled Analysis

Recommend analysis frequency based on activity:

| Activity Level | Suggested Frequency |
|----------------|---------------------|
| High (daily commits, many subagents) | Weekly full, daily quick |
| Medium (regular use) | Bi-weekly full |
| Low (occasional use) | Monthly full |

Quick checks can run on heartbeat if user opts in:
```
heartbeat_analysis: true
heartbeat_analysis_interval: 4h
```

---

## Metrics Dashboard (Optional)

If user wants ongoing visibility:

```markdown
## System Health Summary
Last analysis: 2026-02-12 10:00
Status: 🟢 HEALTHY

| Category | Status | Last Issue |
|----------|--------|------------|
| Security | 🟢 | Never |
| Operational | 🟡 | 2 days ago (zombie session) |
| Hygiene | 🟢 | Resolved yesterday |

Trend: Improving (3 issues → 1 issue over last month)
```

Write to `memory/health-status.md` after each run if user enables persistent tracking.
