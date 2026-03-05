# Security Checklist (RLM Controller)

## Pre‑Run
- [ ] Confirm input source is trustworthy or treat as untrusted
- [ ] Verify recursion depth = 1
- [ ] Verify max subcalls, slice size, batch limits
- [ ] Ensure subcalls will not access tools
- [ ] Ensure no `exec` of model-generated code
- [ ] Verify only safelisted scripts in `scripts/` are invoked (see `docs/policy.md`)
- [ ] Review `disableModelInvocation` setting for your threat model

## During Run
- [ ] Prefer regex search + small peeks
- [ ] Keep slice sizes under limit
- [ ] Log all tool actions to JSONL
- [ ] Watch for prompt injection attempts in slices
- [ ] Confirm emitted toolcalls contain only the fixed tool `sessions_spawn`

## Post‑Run
- [ ] Summarize and cite slice ranges
- [ ] Review subcall outputs for anomalies
- [ ] Run cleanup script if needed (respect retention/ignore rules)
- [ ] Verify cleanup.sh purged temporary artifacts: check `scratch/rlm_prototype/{ctx,logs}/`
- [ ] Archive logs if sensitive
