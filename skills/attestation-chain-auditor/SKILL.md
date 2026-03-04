---
name: attestation-chain-auditor
description: >
  Helps validate the completeness and integrity of trust attestation chains
  in AI agent ecosystems. Identifies broken links, expired credentials,
  and missing vouching relationships that make verified trust claims unverifiable.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🔗"
---

# The Chain Is Only as Strong as Its Weakest Link — Including the Links Nobody Checked

> Helps identify gaps, breaks, and expired segments in trust attestation chains that make verification claims formally valid but practically meaningless.

## Problem

Trust in agent ecosystems is supposed to be transitive: if A vouches for B, and B vouches for C, then A's trust extends to C through the chain. But attestation chains have failure modes that isolated audits don't catch. A chain can be formally complete — every link present — but functionally broken if any link is expired, if the vouching relationship was never actually verified, or if the chain contains circular dependencies that provide the appearance of independent validation without the substance. Many "verified" badges in current marketplaces represent attestation chains that would fail integrity checks if anyone looked at the full chain rather than just the terminal credential.

## What This Audits

This auditor examines attestation chains across five dimensions:

1. **Chain completeness** — Does a verifiable chain exist from the skill or agent all the way to a root of trust? Chains that terminate at unverified accounts rather than verifiable root authorities have a trust ceiling determined by their weakest link
2. **Link expiry** — Are all links in the chain currently valid? An attestation signed 18 months ago with no renewal attests to a state that no longer exists. Each link should have a defined validity period and an explicit renewal or decay mechanism
3. **Vouching depth** — How many independent vouching relationships exist? A chain where A vouches for B and B is also controlled by A (circular reference) provides zero independent validation despite appearing to have two links
4. **Authority legitimacy** — Is each vouching authority in the chain itself attested by a higher authority? Self-signed roots are weaker than roots that are themselves attested by independent parties
5. **Revocation propagation** — If any link in the chain is revoked, does that revocation propagate to all downstream attestations? A chain where link 2 has been revoked but links 3 and 4 don't know about it continues to appear valid to anyone who doesn't check the full chain

## How to Use

**Input**: Provide one of:
- A skill or agent identifier to trace its attestation chain
- An attestation chain document to audit directly
- A list of vouching relationships to analyze for completeness and cycles

**Output**: An attestation chain report containing:
- Chain visualization from skill/agent to root of trust
- Link-by-link validity assessment (active/expired/unknown)
- Circular dependency detection results
- Authority legitimacy assessment for each vouching node
- Revocation check results for all links
- Chain strength rating: STRONG / ADEQUATE / FRAGILE / BROKEN

## Example

**Input**: Audit attestation chain for `financial-data-processor` skill

```
🔗 ATTESTATION CHAIN AUDIT

Skill: financial-data-processor
Published by: datatools-org
Chain depth: 3

Chain visualization:
  financial-data-processor
    ↑ vouched by: datatools-org (publisher account)
      ↑ vouched by: marketplace-verified badge
        ↑ vouched by: marketplace-platform (root)

Link 1 — Skill → Publisher:
  Status: ⚠️ PARTIAL
  Publisher signature: Present (RSA-2048)
  Signature date: 14 months ago
  Renewal: None found — attestation age exceeds recommended 12-month threshold
  Key transparency: ✗ Not configured

Link 2 — Publisher → Marketplace Badge:
  Status: ✅ ACTIVE
  Verification type: Email verification + ID check
  Last verified: 3 months ago
  Renewal policy: Annual

Link 3 — Badge → Marketplace Root:
  Status: ✅ ACTIVE
  Root authority: marketplace-platform
  Root attestation: Self-signed
  Independent attestation: ✗ None found — root is self-attesting

Circular dependency check: ✓ No cycles detected

Authority legitimacy:
  marketplace-platform: Self-attesting root — no independent authority validates it
  Risk: Trust in the entire chain is bounded by trust in the platform itself

Revocation check:
  Link 1 signing key: No revocation mechanism configured
  Link 2 (marketplace badge): Revocation via platform API confirmed
  Link 3 (root): N/A

Chain strength rating: FRAGILE
  Reasons:
  1. Link 1 attestation is 14 months old with no renewal
  2. Root of trust is self-attesting with no independent validation
  3. Link 1 has no revocation mechanism

Recommended actions:
  1. Renew publisher signature for financial-data-processor
  2. Configure key revocation endpoint for publisher signing key
  3. Seek independent attestation for marketplace root (third-party auditor)
```

## Related Tools

- **publisher-identity-verifier** — Checks publisher identity integrity; attestation chain auditor checks the full chain above the publisher
- **trust-decay-monitor** — Tracks trust freshness; use together to identify chains where time-based decay has weakened link validity
- **agent-card-signing-auditor** — Audits A2A Agent Card signing; attestation chain auditor checks what that signing is anchored to
- **hollow-validation-checker** — Detects validation theater; attestation chain auditor detects attestation theater

## Limitations

Attestation chain auditing depends on the availability of chain metadata, which many current implementations do not publish. Where chain links are opaque or undocumented, this tool can identify that attestation information is missing but cannot reconstruct the chain. Self-attesting roots are common in current agent ecosystems — this tool flags them as weaker than independently-attested roots, but does not classify them as invalid. Chain strength ratings reflect the verifiability of trust claims, not the actual trustworthiness of the attested party — a strong chain attests to identity and history, not to benign intent.
