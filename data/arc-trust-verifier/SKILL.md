---
name: trust-verifier
description: Verify skill provenance and build trust scores for ClawHub skills. Checks publisher history, version consistency, dependency trust chains, and generates trust attestations.
user-invocable: true
metadata: {"openclaw": {"emoji": "🔑", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Trust Verifier

Trust, but verify. Assess the trustworthiness of a ClawHub skill by analyzing its publisher, history, dependencies, and consistency.

## Why This Exists

Security scanning catches known malicious patterns. But what about skills that are technically clean but published by unknown authors, have inconsistent version histories, or depend on untrusted packages? Trust Verifier fills the gap between "no vulnerabilities detected" and "safe to install."

## Commands

### Assess trust for a skill directory
```bash
python3 {baseDir}/scripts/trust_verifier.py assess --path ~/.openclaw/skills/some-skill/
```

### Generate a trust attestation
```bash
python3 {baseDir}/scripts/trust_verifier.py attest --path ~/.openclaw/skills/some-skill/ --output trust.json
```

### Verify an existing attestation
```bash
python3 {baseDir}/scripts/trust_verifier.py verify --attestation trust.json --path ~/.openclaw/skills/some-skill/
```

### Check dependency trust chain
```bash
python3 {baseDir}/scripts/trust_verifier.py deps --path ~/.openclaw/skills/some-skill/
```

## Trust Signals

- **Publisher reputation**: Known vs unknown publisher, account age, skill count
- **Version consistency**: Do updates match expected patterns? Sudden permission changes?
- **Content integrity**: SHA-256 hashes of all files, reproducible builds
- **Dependency chain**: Are dependencies from trusted sources?
- **Community signals**: Moltbook mentions, upvotes, known endorsements

## Trust Levels

- **VERIFIED** — Meets all trust criteria, attestation valid
- **TRUSTED** — Most signals positive, minor gaps
- **UNKNOWN** — Insufficient data to assess trust
- **SUSPICIOUS** — One or more trust signals failed
- **UNTRUSTED** — Multiple trust failures, do not install
