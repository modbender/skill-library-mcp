# Remediation Patterns - Security Best Practices

Use these patterns to reduce security risk without destabilizing delivery.

## Pattern 1: Validate at Boundaries

- Add schema validation at request and message boundaries.
- Reject malformed input early.
- Keep internal logic typed and normalized.

Why: boundary validation blocks whole classes of injection and logic abuse.

## Pattern 2: Deny by Default for Access Control

- Start with no access, then grant explicit permissions.
- Keep authorization checks near resource operations.
- Avoid scattered ad hoc permission logic.

Why: default-deny reduces accidental privilege escalation.

## Pattern 3: Secret-Safe Configuration

- Move secrets to environment or secret managers.
- Avoid logging credentials, tokens, or raw sensitive payloads.
- Fail fast if required secrets are missing.

Why: most operational breaches come from secret exposure, not cryptography errors.

## Pattern 4: Output Minimization

- Return only required fields.
- Hide internals in error responses.
- Keep verbose diagnostics in protected logs only.

Why: reduced output lowers reconnaissance value for attackers.

## Pattern 5: Progressive Hardening Rollout

- Apply high-impact fix in smallest possible diff.
- Add tests for changed behavior.
- Release in controlled batches when risk is high.

Why: teams ship security improvements faster when regression risk is bounded.

## Pattern 6: Verified Closure

- Re-test every fixed finding.
- Mark status as fixed only after verification evidence exists.
- Track residual risk explicitly when fixes are deferred.

Why: unverified fixes create false confidence and recurring incidents.
