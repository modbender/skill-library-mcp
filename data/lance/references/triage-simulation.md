# Triage Simulation

Simulate strict triage before final report generation.

## Verdict States

- `Accepted`: reproducible, exploitable, impactful, in-scope
- `Needs More Evidence`: plausible but missing required proof
- `Rejected`: non-exploitable, out-of-scope, or weak impact

## Triage Questions

1. Is the root cause technical and security-relevant?
2. Is there a deterministic exploit path?
3. Is impact real and non-trivial?
4. Are assumptions realistic for attackers?
5. Does the finding survive policy exclusions?

## Rejection Triggers

- speculative attack path
- social engineering as primary mechanism
- admin-malicious premise only
- no economic viability for market attacks
- missing reproduction details

## Minimum Evidence to Avoid `Needs More Evidence`

- precise target + function references
- transaction-level exploit sequence
- state transition and impact evidence
- quantified impact or bounded loss estimate

## Output Format

```text
Triage Verdict: [Accepted / Needs More Evidence / Rejected]
Severity Recommendation: [Critical / High / Medium / Low]
Rationale:
Missing Evidence (if any):
```
