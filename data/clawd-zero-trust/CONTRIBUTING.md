# Contributing to clawd-zero-trust

Thanks for your interest. This is security infrastructure — contributions are welcome but held to a high standard.

## Before you start

Open an issue first. Describe what you want to fix or add, and why. This avoids wasted effort on PRs that won't be merged.

## Standards

Every change to a shell script must:

1. Pass `shellcheck` with zero warnings
2. Pass the full release gate:
   ```bash
   bash scripts/release-gate.sh .
   ```
3. Not introduce new `eval` patterns without explicit justification
4. Not weaken the rollback guarantees (`perform_reset_or_die` must remain non-optional)
5. Not add domains to `PROVIDERS` without documented justification

## Pull request checklist

- [ ] `shellcheck` clean
- [ ] `release-gate.sh` passes
- [ ] Changes documented in the version header comment of the modified script
- [ ] `README.md` updated if architecture or behavior changes
- [ ] No hardcoded IPs (use DNS resolution)
- [ ] No `perform_reset || true` patterns (always use `perform_reset_or_die`)

## What gets merged

- Bug fixes with clear reproduction steps
- Security improvements that don't break existing safety guarantees
- New providers added to the allowlist (with justification)
- Documentation improvements

## What won't be merged

- Weakening of the rollback or lockout detection logic
- Removing the script hash gate
- Adding `2>/dev/null` to commands where failure must be detected
- Changes that break `--dry-run` idempotency

## Code style

- Bash only. No additional runtime dependencies beyond `ufw`, `dig`, `curl`, `python3`.
- All functions documented with a comment explaining their safety contract.
- Dry-run must always be the default. Apply requires an explicit flag.

## Maintainer

Stan Stolberg — stan@blocksoft.tech  
Blocksoft GmbH — https://blocksoft.tech
