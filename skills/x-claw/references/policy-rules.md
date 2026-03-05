# X-Claw Approval and Policy Rules (MVP)

## Approval Precedence

1. Deny
2. Specific trade approval
3. Pair approval
4. Global approval

## Approval Scope

- Pair approvals are non-directional.
- Pair and global approvals are chain-scoped.
- Policy conflict rule: most restrictive wins.

## Copy Execution Rules

- Copy intents are server-generated.
- Agent polls server and executes locally with wallet custody.
- Follower limits apply in strict arrival order.
- Expired intents are dropped.
