# Risk Exceptions - Security Best Practices

Use this file when a risk is intentionally accepted instead of fixed immediately.

## When to Record an Exception

- A fix would cause unacceptable production disruption right now.
- A dependency or platform limitation blocks immediate remediation.
- A temporary mitigation exists and ownership is explicit.

Do not record exceptions for unknown issues or unverified assumptions.

## Required Fields Per Exception

1. Exception ID (`EXC-001`)
2. Scope (service, file, endpoint, or workflow)
3. Linked finding ID (`SEC-00X`)
4. Rationale and business context
5. Compensating controls in place
6. Owner and review deadline

## Review Cadence

- Critical and high exceptions: review every 30 days.
- Medium exceptions: review every 90 days.
- Low exceptions: review every 180 days.

If the deadline passes, escalate and re-assess immediately.

## Closure Criteria

An exception can close only when:
- The linked finding is fixed and verified, or
- The risk is formally retired with updated architecture evidence.

Every closure must include date, owner, and verification notes.
