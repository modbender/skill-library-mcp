---
name: agent-card-signing-auditor
description: >
  Helps audit Agent Card signing practices in A2A protocol implementations.
  Identifies missing signatures, weak signing schemes, and revocation gaps
  that allow impersonation in agent-to-agent trust handshakes.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🪪"
---

# A2A Says Signing Is Optional. That's the Problem.

> Helps identify gaps in Agent Card signing that allow impersonation, identity spoofing, and unverifiable capability claims in agent-to-agent trust handshakes.

## Problem

The A2A Protocol specifies Agent Cards as the primary mechanism for agent identity and capability advertisement. An Agent Card tells other agents: who you are, what you can do, and what trust level you claim. But the A2A spec makes signing optional — "recommended but not required." In an ecosystem where 15-18% of published skills are already confirmed malicious, optional signing means any agent can present any identity and any capability claim with zero verifiable proof. The trust handshake that underpins all A2A interactions is built on a foundation that most implementations don't verify.

## What This Checks

This auditor examines Agent Card signing practices across five dimensions:

1. **Signature presence** — Does the Agent Card include a signature field? Many implementations omit it entirely, relying on the marketplace's account verification as a trust proxy. That's a single point of failure — marketplace accounts can be compromised or impersonated
2. **Signing scheme strength** — If a signature is present, which algorithm was used? RSA-1024 and ECDSA with weak curves are no longer adequate for high-stakes agent interactions. Checks against current recommendations (Ed25519, RSA-2048+ with PSS padding)
3. **Key transparency** — Is the signing key published in a verifiable key transparency log or JWKS endpoint? A signature is only as trustworthy as the process by which you obtained the public key to verify it
4. **Revocation mechanism** — Does the signing infrastructure include a revocation path? Signing keys get compromised. An Agent Card signed with a compromised key looks identical to a legitimately-signed one without revocation checking
5. **Rotation audit trail** — Has the signing key changed? When? With what announcement? Key rotation events that coincide with capability changes or that happen without public announcement are higher-risk than routine scheduled rotations

## How to Use

**Input**: Provide one of:
- An Agent Card JSON object to audit directly
- An agent endpoint URL to fetch and audit the Agent Card
- A set of Agent Card snapshots to compare for rotation events

**Output**: A signing audit report containing:
- Signature presence and scheme assessment
- Key transparency verification result
- Revocation mechanism check
- Rotation history (if available)
- Risk rating: STRONG / ADEQUATE / WEAK / UNSIGNED
- Specific recommendations for remediation

## Example

**Input**: Audit Agent Card for `data-processing-agent.example`

```
🪪 AGENT CARD SIGNING AUDIT

Agent: data-processing-agent.example
Card version: 2.1.0
Audit timestamp: 2025-03-15T10:30:00Z

Signature presence: ⚠️ ABSENT
  Agent Card contains no signature field
  Identity claim is unverifiable — relies entirely on marketplace account trust
  Risk: any agent can claim this identity or capabilities without detection

Signing scheme: N/A (unsigned)

Key transparency: ✗ NOT CONFIGURED
  No JWKS endpoint referenced in Agent Card
  No key transparency log entry found

Revocation mechanism: ✗ NONE
  No revocation endpoint specified
  No CRL or OCSP equivalent configured

Rotation history: N/A

Risk rating: UNSIGNED
  This Agent Card makes identity and capability claims that cannot be
  cryptographically verified. In a trust-sensitive interaction, treat
  all capability claims as unverified assertions.

Recommended actions:
  1. Implement Ed25519 signing for Agent Card with JWKS endpoint
  2. Register signing key in a public key transparency log
  3. Add revocation endpoint to Agent Card metadata
  4. Establish rotation policy with public announcement process
```

## Related Tools

- **publisher-identity-verifier** — Audits publisher identity at the marketplace level; signing auditor checks the A2A protocol layer
- **trust-decay-monitor** — Tracks trust freshness over time; signing provides the baseline trust claim that decays
- **protocol-doc-auditor** — Checks documentation trust signals; Agent Card signing is the machine-readable equivalent
- **attestation-chain-auditor** — Validates the full trust chain from signing key to capability claim

## Limitations

This auditor evaluates signing practices based on publicly observable Agent Card metadata. It cannot assess the security of key storage practices on the agent's host system, verify that the private key holder is actually the claimed agent, or detect signing key compromise that has not yet been publicly disclosed. A well-formed signed Agent Card with strong cryptography can still represent a compromised or malicious agent — signing establishes identity, not trustworthiness. Use in combination with behavioral analysis tools for comprehensive trust assessment.
