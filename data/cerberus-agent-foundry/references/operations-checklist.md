# Operations Checklist

## Deployment checklist

- [ ] Agent workspaces exist and are isolated.
- [ ] `control-plane/tasks` has seed task.
- [ ] `control-plane/mailbox` supports send/ack/resolve.
- [ ] `events.jsonl` records task and mailbox transitions.
- [ ] Least-privilege identity files exist per role.

## Stability gate (before expansion)

Run for at least 3 days without manual intervention:
- task lifecycle transitions valid
- no mailbox duplicate-consume incident
- no unauthorized cross-workspace writes

## Security checks

- Coder write scope constrained to coder workspace.
- QA/Ops deploy actions blocked without approval ticket.
- Team Lead-only mailbox GC enforced.
