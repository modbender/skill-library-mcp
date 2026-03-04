# Safety Rules (Enforced)

## Must Not Leak
- passcodes
- exact location URLs
- private notes
- bearer tokens

## Human Approval Required
Before:
- publish if draft materially changed
- major invite fanout changes
- confirm/decline/withdraw actions

## Status and Scope Enforcement
- Host operations require `meetup:create` scope.
- Attendee operations require attendee scopes.
- Invites and join approvals require meetup `open` status.

## Logging Policy
- Redact secrets and private fields.
- Log only status transitions and event IDs.

## Delivery Policy
- Ack only after corresponding processing milestone.
- Maintain monotonic cursor progression.

## Incident Response
If secret leakage is suspected:
1. rotate token/session
2. stop automation
3. notify operator/human
4. resume after remediation
