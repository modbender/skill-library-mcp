# Process Design and Optimization

## Process Mapping

### Current State Analysis

Before improving, document what exists:

1. **Identify the process** — Clear start and end points
2. **List all steps** — What actually happens, not what should
3. **Map actors** — Who does what
4. **Note handoffs** — Where work transfers between people/teams
5. **Measure time** — How long each step takes
6. **Find pain points** — Where things break or slow down

### Process Documentation Template

```markdown
# Process: [Name]

## Purpose
Why this process exists

## Trigger
What starts this process

## Steps
1. [Actor] does [action] using [tool]
2. [Actor] does [action] using [tool]
...

## Output
What this process produces

## Owner
Who is accountable for this process

## Metrics
How we measure success
```

## Optimization Framework

### Order of Operations

1. **Eliminate** — Can we remove this step entirely?
2. **Simplify** — Can we make it easier?
3. **Combine** — Can we merge steps?
4. **Automate** — Can a machine do it?
5. **Parallelize** — Can steps happen simultaneously?

### Optimization Checklist

- [ ] Every step adds value (customer would pay for it)
- [ ] No unnecessary approvals
- [ ] Handoffs minimized
- [ ] Wait time reduced
- [ ] Error-proofing in place
- [ ] Exceptions have clear paths

## When to Automate

| Automate | Don't Automate |
|----------|----------------|
| High volume, repetitive | Rare, one-off tasks |
| Well-defined rules | Requires judgment |
| Error-prone manual work | Simple, quick tasks |
| Data transfer between systems | Frequently changing process |

### Automation ROI

```
Time saved per occurrence × Frequency × Duration
─────────────────────────────────────────────────
        Implementation time + Maintenance
```

## Process Governance

### Review Cadence

| Process Type | Review Frequency |
|--------------|------------------|
| Core operations | Quarterly |
| Support processes | Semi-annually |
| Compliance | As regulations change |

### Change Management

1. **Propose** — Document the change and rationale
2. **Review** — Affected parties provide input
3. **Approve** — Process owner decides
4. **Communicate** — Everyone knows what's changing
5. **Train** — People know how to follow new process
6. **Monitor** — Verify change achieved goals

## Common Process Problems

| Problem | Symptom | Fix |
|---------|---------|-----|
| Bottleneck | Work piles up at one step | Add capacity or parallelize |
| Rework loops | Same work done multiple times | Quality checks earlier |
| Handoff errors | Information lost in transfer | Checklists, better tooling |
| Approval delays | Waiting for sign-off | Raise thresholds, delegate |
| Tribal knowledge | Only one person knows how | Document, cross-train |
