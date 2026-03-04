---
name: publisher-identity-verifier
description: >
  Helps verify publisher identity integrity in AI agent ecosystems.
  Detects impersonation, key rotation anomalies, and identity gaps
  in the trust chain between skill publishers and their claimed identities.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🪪"
---

# You Trusted the Publisher. But Who Verified the Publisher?

> Helps identify gaps in publisher identity verification that allow impersonation, key compromise, and identity fraud in agent marketplaces.

## Problem

When you install a skill, you trust the publisher. But what proves the publisher is who they claim to be? Most agent marketplaces verify email addresses — not identities. A publisher account can be created in minutes, build reputation over months, then be compromised or sold. The skill ecosystem has no equivalent of code signing certificates, no publisher key transparency logs, and no mechanism to detect when a trusted publisher identity has been taken over. This is the weakest link in agent-to-agent trust: you can audit the code, audit the permissions, audit the tests — but if the publisher behind them isn't who you think, all those audits verify the wrong thing.

## What This Checks

This verifier examines publisher identity integrity across five dimensions:

1. **Publication history consistency** — Does the publisher's output show a coherent expertise trajectory, or sudden topic shifts that suggest account takeover? A Python tooling publisher that suddenly releases a crypto wallet skill is a signal worth investigating
2. **Key rotation analysis** — Tracks signing key changes over time. Normal rotation follows predictable patterns (annual, after security events). Suspicious patterns: key change immediately before a controversial update, key change with no announcement, multiple key changes in short succession
3. **Identity impersonation detection** — Scans for publisher names that are typo-squats (e.g., `anthroplc` vs `anthropic`), Unicode homoglyphs (e.g., Cyrillic `а` vs Latin `a`), or prefix/suffix variations of established publishers
4. **Cross-platform identity correlation** — Checks whether the publisher has consistent identity signals across multiple platforms (marketplace profile, code repository, community presence). A publisher that exists only on one platform with no external footprint is higher risk
5. **Credential lifecycle gaps** — Identifies publishers whose verification credentials have expired, whose linked accounts have been deleted, or whose attestation chain has broken links

## How to Use

**Input**: Provide one of:
- A publisher ID or username to investigate
- A skill identifier to trace back to its publisher
- A marketplace search term to audit publisher identities in results

**Output**: A publisher identity report containing:
- Identity consistency score across dimensions
- Timeline of key events (account creation, key changes, topic shifts)
- Impersonation risk assessment
- Cross-platform presence map
- Trust rating: VERIFIED / PARTIAL / UNVERIFIED / SUSPICIOUS
- Recommended actions for downstream adopters

## Example

**Input**: Verify publisher identity for `secure-tools-org` (popular security utility publisher)

```
🪪 PUBLISHER IDENTITY REPORT — SUSPICIOUS

Publisher: secure-tools-org
Account age: 14 months
Skills published: 8
Total downloads: ~2,400

History consistency: ⚠️ WARNING
  Months 1-11: Published 5 Python linting tools (consistent theme)
  Month 12: Published 3 "security audit" tools (sudden pivot)
  Topic shift coincides with key rotation event

Key rotation: ⚠️ ANOMALY DETECTED
  Key #1: Created 2024-01-15, used for 11 months
  Key #2: Created 2024-12-03, used since (current)
  Gap: Key changed 2 days before first security tool published
  No rotation announcement found in any channel

Impersonation check: ✓ CLEAN
  No known publishers with confusable names
  No Unicode homoglyph matches

Cross-platform presence: ⚠️ THIN
  Marketplace: ✓ Active profile
  Code repository: ✗ No linked repository
  Community: ✗ No forum/social presence found
  Single-platform publisher — limited identity corroboration

Credential lifecycle: ⚠️ PARTIAL
  Email verification: ✓ Valid
  Repository attestation: ✗ Not configured
  Signing key transparency: ✗ No public key log

Trust rating: SUSPICIOUS
  Reason: Topic pivot + key rotation timing + single-platform presence

Recommended actions:
  1. Review the 3 security tools manually before adoption
  2. Contact publisher to request repository attestation
  3. Monitor for further key rotation events
  4. Cross-reference with clone-farm-detector for content analysis
```

## Related Tools

- **clone-farm-detector** — Detects content-level cloning; use together to distinguish "same code, different publisher" (clone) from "same publisher, different identity" (impersonation)
- **protocol-doc-auditor** — Audits documentation trust signals; publisher identity adds context to whether doc instructions should be trusted
- **trust-decay-monitor** — Tracks verification freshness; publisher identity credentials also decay over time
- **evolution-drift-detector** — Detects behavioral drift in skills; sudden drift may correlate with publisher identity changes

## Limitations

Publisher identity verification helps surface inconsistencies but cannot prove malicious intent. Account takeovers may be invisible if the attacker maintains the publisher's established patterns. Cross-platform correlation depends on public information availability — publishers who deliberately maintain privacy may appear suspicious when they are simply private. This tool provides identity risk signals, not identity proof — it helps prioritize which publishers warrant deeper investigation but does not replace platform-level identity verification infrastructure.
