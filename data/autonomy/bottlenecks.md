# Bottleneck Detection

How to identify where the human is blocking progress.

## Detection Triggers

### Time-Based
- Human takes >1h to respond to routine requests
- Same task waits for human multiple times per week
- Async handoffs add days to what could be minutes

### Pattern-Based
- Human approves 95%+ without changes → rubber stamp
- Human does identical steps each time → automatable
- Human copy-pastes between systems → integration opportunity

### Frustration-Based
- Human says "I hate doing this"
- Human forgets and apologizes
- Human rushes through to get it done

### Workflow-Based
- Agent completes work, waits for human to continue
- Multiple agents blocked on same human
- Human is single point of failure for process

## Severity Scoring

Rate each bottleneck:

| Factor | Low (1) | Medium (2) | High (3) |
|--------|---------|------------|----------|
| Frequency | Monthly | Weekly | Daily |
| Time cost | Minutes | Hours | Days |
| Skill required | Judgment needed | Some rules | Pure process |
| Risk if wrong | High impact | Moderate | Easily reversed |

**Priority = Frequency × Time cost × (4 - Skill required) × (4 - Risk)**

Higher score = better takeover candidate.

## Documentation Format

When you identify a bottleneck:

```
## [Bottleneck Name]
- **What:** Description of the task
- **Frequency:** How often it happens
- **Time cost:** How long human spends
- **Current flow:** What happens today
- **Bottleneck point:** Exactly where human blocks
- **Takeover complexity:** Easy / Medium / Hard
- **Risk assessment:** What could go wrong
- **Proposed pilot:** How to test agent ownership
```

## Common Bottleneck Categories

### Approvals
- PR merges that always get approved
- Expense reports under threshold
- Access requests for standard tools

### Communications
- Status update emails
- Meeting scheduling
- Routine client responses

### Operations
- Deployments to non-production
- Backup verifications
- Log reviews and alerts

### Data
- Report generation
- Data entry and validation
- System synchronization

## Questions to Surface Bottlenecks

Ask the human periodically:
- "What task do you wish would just happen?"
- "Where do you feel like the blocker?"
- "What's on your plate that feels like autopilot?"
- "If you were out for a week, what would break?"
