# Memory Template — AWS

Create `~/aws/memory.md` with this structure:

```markdown
# AWS Memory

## Status
status: ongoing
version: 2.0.0
last: YYYY-MM-DD
integration: pending

## Account Context
<!-- AWS account details learned from conversations -->
<!-- Example: Personal account, us-east-1 primary, ~$100/month budget -->

## Current Infrastructure
<!-- What's deployed, high-level -->
<!-- Example: Single EC2 (t3.small) + RDS PostgreSQL + S3 bucket -->

## Preferences
<!-- How they like to work -->
<!-- Example: Prefers Terraform, wants cost alerts at $50 -->

## Cost Notes
<!-- Budget constraints, past surprises, optimization wins -->

## Notes
<!-- Internal observations -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning context | Gather info opportunistically |
| `complete` | Know their setup well | Focus on execution |
| `paused` | User said "not now" | Don't ask, work with what you have |

## Additional Files (Optional)

### resources.md
Track active infrastructure:
```markdown
# AWS Resources

## EC2 Instances
| Name | Type | Region | Purpose |
|------|------|--------|---------|

## RDS Databases
| Name | Engine | Type | Multi-AZ |
|------|--------|------|----------|

## S3 Buckets
| Name | Region | Purpose |
|------|--------|---------|

---
*Updated: YYYY-MM-DD*
```

### costs.md
Track spending:
```markdown
# AWS Costs

## Monthly Tracking
| Month | Actual | Budget | Notes |
|-------|--------|--------|-------|

## Alerts Set
- Billing: $X threshold
- Service-specific: ...

## Optimization Wins
<!-- Cost savings achieved -->

---
*Updated: YYYY-MM-DD*
```
