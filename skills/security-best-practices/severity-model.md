# Severity Model - Security Best Practices

Use this model to keep severity decisions consistent.

## Critical

Conditions:
- Remote compromise or privilege escalation is realistic.
- Sensitive data exposure is broad and immediate.
- Business-impacting abuse is likely without major prerequisites.

Action expectation:
- Fix immediately.
- Add focused regression checks before release.

## High

Conditions:
- Exploitation is feasible with moderate effort.
- Access control bypass, significant data exposure, or strong abuse vector exists.

Action expectation:
- Prioritize in current sprint.
- Ship with explicit validation evidence.

## Medium

Conditions:
- Exploitation needs specific preconditions.
- Impact is limited but meaningful if combined with other weaknesses.

Action expectation:
- Plan fix with clear owner and deadline.
- Consider compensating controls if immediate change is risky.

## Low

Conditions:
- Limited impact, low exploitability, or defense-in-depth gap only.

Action expectation:
- Backlog with rationale.
- Reassess during future hardening cycles.

## Confidence Scale

- High: direct code evidence and clear exploit path.
- Medium: strong signal with minor unknown runtime assumptions.
- Low: incomplete visibility; needs runtime or infrastructure confirmation.

Never inflate confidence when evidence is partial.
