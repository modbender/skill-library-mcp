---
name: transparency-log-auditor
description: >
  Helps verify that skill signing events are recorded in an independently
  auditable transparency log — catching the class of trust failures where
  a registry operator can silently rewrite history without detection.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "📋"
---

# The Registry Said the Skill Was Signed. The Log Says Otherwise.

> Helps identify when skill signing history cannot be independently verified — exposing the gap between "the registry claims it's signed" and "an auditor can confirm it was signed."

## Problem

A signed skill is only as trustworthy as the registry that stores its signing records. If the registry is the sole authority on what was signed, when, and by whom, then a compromised registry operator can retroactively alter signing history without detection. A skill that was never signed can be backdated as signed. A key rotation that was suspicious can be erased. An unsigned version that introduced malicious behavior can be removed from the audit trail.

Transparency logs solve this by making signing events append-only and independently verifiable: each new entry must chain to all previous entries, and any external party can verify the chain without trusting the registry. A registry that silently rewrites history will produce a fork that's detectable by anyone holding an older version of the log.

This is the same principle that makes Certificate Transparency logs effective for TLS: the CA cannot issue a certificate without producing a publicly auditable record. Without it, trust in certificates is bounded by trust in the CA. With it, a CA that misbehaves produces evidence of misbehavior that anyone can find.

Agent skill ecosystems don't yet have this infrastructure. This auditor helps identify the gap — and what it means for the skills you trust.

## What This Checks

This auditor examines transparency log coverage across five dimensions:

1. **Log existence and accessibility** — Does the skill registry maintain a transparency log at all? Is it publicly accessible and independently queryable, or is it an internal record only the registry operator can read?
2. **Append-only verifiability** — Can the log's append-only property be verified? A log that allows deletion or modification without producing an auditable fork is not a transparency log — it's a mutable history
3. **Signing event completeness** — Does every version publication, key rotation, and revocation event appear in the log? Gaps indicate either missing log coverage or selective omission
4. **Cross-log consistency** — If a skill appears in multiple registries, do their transparency logs agree on signing history? Divergent records indicate one registry's history has been altered
5. **Independent verification path** — Can an auditor verify the log's consistency without trusting the registry operator? A log where verification requires querying the same registry that produced it provides no additional assurance

## How to Use

**Input**: Provide one of:
- A skill registry URL to audit for transparency log infrastructure
- A skill identifier to check whether its signing events are log-covered
- Two registry records of the same skill to compare for consistency

**Output**: A transparency log audit report containing:
- Log infrastructure assessment (exists / partial / absent)
- Append-only verifiability rating
- Signing event coverage gaps
- Cross-registry consistency check (if applicable)
- Independent verification path availability
- Coverage verdict: FULL / PARTIAL / REGISTRY-ONLY / ABSENT

## Example

**Input**: Audit transparency log coverage for `data-pipeline-connector` skill

```
📋 TRANSPARENCY LOG AUDIT

Skill: data-pipeline-connector
Registry: primary-marketplace.example
Audit timestamp: 2025-04-15T11:00:00Z

Log infrastructure:
  Registry transparency log endpoint: ✗ Not found
  Fallback: Registry signing record (internal only)
  Third-party log inclusion: ✗ Not configured

Signing events in internal record:
  v1.0.0: ✅ Signed — key: ed25519:a3f9c2 — timestamp: 2024-11-01
  v1.1.0: ✅ Signed — key: ed25519:a3f9c2 — timestamp: 2024-12-15
  v1.2.0: ✅ Signed — key: ed25519:b7d441 — timestamp: 2025-01-30

Independent verification:
  Can auditor verify v1.0.0 signature without trusting registry? ✗ No
  Can auditor verify key rotation at v1.2.0 without trusting registry? ✗ No
  External log cross-check available? ✗ No

Cross-registry check:
  Mirror registry (backup-marketplace.example): Available
  Mirror signing record for v1.2.0: key ed25519:a3f9c2 (diverges from primary)
  ⚠️ INCONSISTENCY: Primary records key change at v1.2.0; mirror records same key

Coverage verdict: REGISTRY-ONLY
  Signing history exists but is not independently verifiable.
  Cross-registry inconsistency detected at v1.2.0 — one registry's
  history has been altered without a transparency log to detect which.

Risk assessment: HIGH
  Without an independently auditable log, the key rotation at v1.2.0
  cannot be attributed to legitimate key management vs. retroactive
  record alteration. The cross-registry divergence makes this worse:
  at least one registry's signing history is incorrect.

Recommended actions:
  1. Request explanation for cross-registry divergence at v1.2.0
  2. Treat v1.2.0+ as signed by an unverified key pending investigation
  3. Advocate for registry to publish to a public transparency log
  4. Consider pinning to v1.1.0 (last version with consistent records)
```

## Related Tools

- **update-signature-verifier** — Checks signing key continuity across versions; transparency-log-auditor checks whether those signing events are independently verifiable
- **attestation-chain-auditor** — Validates the full trust chain; transparency log provides the auditable substrate that attestation chains should be anchored to
- **attestation-root-diversity-analyzer** — Checks whether trust roots are diversified; transparency logs make root behavior auditable
- **publisher-identity-verifier** — Verifies publisher identity; transparency logs make key rotation events auditable

## Limitations

Transparency log auditing can only assess infrastructure that exists and is accessible. Many current skill registries do not publish transparency logs at all — this tool can identify the absence, but cannot reconstruct what a log would have contained. Cross-registry consistency checks require access to multiple registries carrying the same skill, which is not always available. The presence of a transparency log does not confirm it is correctly implemented — a log can exist and still allow modifications if its cryptographic properties are incorrectly applied. This tool helps surface transparency gaps and inconsistencies; resolving them requires registry operators to publish to properly implemented append-only logs.
