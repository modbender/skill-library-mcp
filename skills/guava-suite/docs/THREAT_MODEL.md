# THREAT_MODEL.md

## Assets
- Agent identity integrity
- Memory integrity/availability
- Detection rules confidentiality (high-sensitivity)
- OSS trust and reproducibility

## Trust Boundaries
1. OSS repo boundary
2. Private suite boundary
3. Runtime plugin boundary
4. Config/secrets boundary

## Primary Threats
- Direct import bypass (boundary break)
- Rule leakage via logs/errors
- Prompt-injection induced unsafe extension calls
- Replay/duplicate memory writes
- Plugin downgrade / version mismatch

## Controls
- Contract test required before merge
- Import-lint: no private path in OSS
- Fail-closed on extension errors
- Sensitive fields redaction in logs
- Version handshake + minimum supported version

## Abuse Cases
- Attacker mimics suite plugin with permissive responses
- OSS release accidentally includes private signatures
- Missing lock creates concurrent write corruption

## Security Invariants
- OSS alone must remain safe and useful
- Private logic never required for baseline safety
- Any boundary violation must fail build or fail runtime closed
