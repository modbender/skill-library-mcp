---
name: update-signature-verifier
description: >
  Helps verify the cryptographic integrity of skill updates by checking
  whether each version is signed by the same key as the original install,
  detecting key changes, signature gaps, and unsigned updates that may
  indicate a compromised or transferred skill.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "✍️"
---

# Unsigned Updates Are the Trust Loophole Nobody Closes

> Helps identify when skill updates break the cryptographic chain of custody established at install time — catching the class of supply chain attacks that enters through legitimate update channels.

## Problem

When you install a skill, you might verify the publisher's signature. When that skill updates two months later, does anyone check whether the update is signed by the same key? In most agent ecosystems, the answer is no. The install-time trust check doesn't extend to updates. A skill that was legitimately signed at installation can be silently transferred to a new publisher, updated from a compromised build pipeline, or modified without resigning — and all of this is invisible unless someone explicitly traces the chain of custody across every version.

This is not theoretical. Skills that accumulate users become valuable targets. The acquisition vector (buy the publisher account, gain access to the update channel) is simpler than compromising the skill directly. The trust you placed in version 1.0 doesn't automatically extend to version 1.4 if version 1.4 was signed by a different key.

## What This Checks

This verifier examines update signature continuity across five dimensions:

1. **Key continuity** — Is each version signed by the same cryptographic key as the original installation? A key change between versions is a high-signal event that warrants explicit verification — legitimate key rotations happen, but they should be announced
2. **Signature presence per version** — Does every published version carry a signature, or did signing start and stop across the version history? Gaps in signing coverage are a red flag even if the current version is signed
3. **Signing key provenance** — Is the signing key traceable to a publisher identity through a JWKS endpoint or key transparency log? Orphaned keys (present but unanchored) provide weaker trust anchoring than keys registered to verifiable identities
4. **Unsigned update detection** — Any version that was published without a signature but then followed by signed versions deserves scrutiny — the unsigned version may be the one that was modified
5. **Chain-of-custody continuity** — Can you trace an unbroken line of signed updates from version 1.0 to the current version? A chain with gaps is fragile in the same way an attestation chain with broken links is fragile

## How to Use

**Input**: Provide one of:
- A skill identifier with version history to audit
- A list of version-signing metadata (version, signing key fingerprint, signature timestamp)
- Two specific versions to compare chain-of-custody

**Output**: A signature continuity report containing:
- Version-by-version signing key fingerprint comparison
- Key change events with timestamps
- Unsigned version detection
- Chain-of-custody completeness rating: CONTINUOUS / GAPS / BROKEN / UNSIGNED
- Recommended actions for each gap or anomaly

## Example

**Input**: Verify signature chain for `data-aggregator` skill, versions 1.0.0 through 1.3.2

```
✍️ UPDATE SIGNATURE VERIFICATION

Skill: data-aggregator
Versions audited: 1.0.0 → 1.1.0 → 1.2.0 → 1.3.0 → 1.3.1 → 1.3.2
Audit timestamp: 2025-04-10T09:15:00Z

Version signing summary:
  1.0.0: ✅ Signed — key: ed25519:a3f9c2 (publisher: original-dev)
  1.1.0: ✅ Signed — key: ed25519:a3f9c2 (same key, continuous)
  1.2.0: ⚠️ UNSIGNED — no signature field present
  1.3.0: ✅ Signed — key: ed25519:b7d441 (NEW KEY — different from 1.1.0)
  1.3.1: ✅ Signed — key: ed25519:b7d441 (continuous from 1.3.0)
  1.3.2: ✅ Signed — key: ed25519:b7d441 (continuous)

Key change detected:
  Between 1.1.0 and 1.3.0: ed25519:a3f9c2 → ed25519:b7d441
  Coincides with: unsigned version 1.2.0 in the gap
  Key change announcement: Not found in publisher changelog
  New key provenance: ed25519:b7d441 not registered in JWKS endpoint

Unsigned version:
  1.2.0: Published 2025-02-14, no signature
  Content delta from 1.1.0: Dependency update + new outbound endpoint added

Chain-of-custody: BROKEN
  Reasons:
  1. Version 1.2.0 is unsigned
  2. Key changed between 1.1.0 and 1.3.0 without announcement
  3. Key change coincides with a version that added a new outbound endpoint
  4. New signing key not registered in publisher's JWKS

Risk assessment: HIGH
  The combination of an unsigned version introducing new network behavior,
  followed by a key rotation without announcement, matches the pattern of
  a compromised or transferred skill that was re-signed by a new controller.

Recommended actions:
  1. Request publisher explanation for key change at 1.2.0→1.3.0 boundary
  2. Audit the outbound endpoint added in 1.2.0 before trusting current version
  3. Treat 1.3.x as signed by an unverified key until provenance is established
  4. Consider pinning to 1.1.0 (last version with verified key) pending review
```

## Related Tools

- **skill-update-delta-monitor** — Tracks behavioral changes in updates; update-signature-verifier checks whether updates are cryptographically authorized
- **attestation-chain-auditor** — Validates the full trust chain; signing verifier focuses on the publisher-to-update link specifically
- **publisher-identity-verifier** — Verifies publisher identity; signing verifier checks whether update authorship is consistent with that identity
- **trust-decay-monitor** — Tracks trust freshness over time; signature gaps accelerate trust decay

## Limitations

This verifier depends on the availability of per-version signing metadata, which many current skill marketplaces do not expose. Where version history lacks signing records, this tool can identify the absence of metadata but cannot reconstruct what signatures may have existed. Key change detection requires access to historical key fingerprints — if a marketplace only stores the current signing key, pre-change versions cannot be compared. A continuous chain of valid signatures from the same key does not confirm the skill is safe — a publisher whose key is compromised can issue malicious-but-validly-signed updates. Signing continuity establishes chain of custody, not trustworthiness of the content.
