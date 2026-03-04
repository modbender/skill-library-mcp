---
name: skill-audit
description: On-chain skill provenance registry. Check, register, audit, and vouch for agent skills on Solana. Use when evaluating skill safety, registering new skills, or looking up provenance before installation.
---

# Skill Audit — On-Chain Provenance Registry

## Commands

### /check-skill <name>
Look up on-chain provenance for a skill before installing.
1. Read all three tables (registry, audits, vouches) for the given skill ID
2. Compute trust level from audit verdicts
3. Display: trust badge, author, hash, version, audit history, vouch count

### /audit-skill <name> <severity>
Submit an audit verdict (requires IQ tokens in wallet).
Severities: S (secure), L (low), M (medium), H (high), C (critical)
Optionally run ZeroLeaks first and inscribe full report via codeIn.

### /vouch-skill <name> [score]
Community endorsement. Score 1-5 (default 5).

### /register-skill <path>
Register a local skill with on-chain hash.
1. Read skill.md at given path
2. Normalize and SHA-256 hash the content
3. Write registration row with short hash (first 8 hex chars)

## Trust Badges
- MALICIOUS: BLOCK installation, warn user
- FLAGGED: Strong warning
- CAUTIONED: Mild warning
- VERIFIED: Green checkmark
- AUDITED: Has audits but not yet verified secure
- REGISTERED: In registry, no audits yet
- UNKNOWN: Not in registry — warn "no on-chain provenance"
- Hash mismatch: Warn "content differs from registered version"

## Implementation

Package: [`@rocketlabs/skill-audit`](https://www.npmjs.com/package/@rocketlabs/skill-audit)

```javascript
const { checkSkill, registerSkill, auditSkill, vouchForSkill, hashSkill } = require('@rocketlabs/skill-audit');
```

### checkSkill({ connection, skillId, rpcUrl })
Returns: `{ trustLevel, skill, audits, vouches, summary }`
Free (RPC read only, no SOL needed).

### registerSkill({ connection, signer, skillId, author, shortHash, version, codeInTx, rpcUrl })
Writes to `skill_registry` table. Public — anyone can register.

### auditSkill({ connection, signer, skillId, auditor, severity, categories, codeInTx, rpcUrl })
Writes to `skill_audits` table. IQ-token-gated — signer must hold IQ tokens.
Severity: S/L/M/H/C. Categories: dir,enc,per,soc,tec,cre,mny,cot,pol,asc,ctx,sem,too,sir,ech

### vouchForSkill({ connection, signer, skillId, voucher, score, rpcUrl })
Writes to `skill_vouches` table. Public — anyone can vouch. Score 1-5.

### hashSkill(content)
Returns: `{ fullHash, shortHash }` — SHA-256 of normalized content.

## On-Chain Architecture

- **Program:** `9KLLchQVJpGkw4jPuUmnvqESdR7mtNCYr3qS4iQLabs`
- **DB Root ID:** `skill-audit`
- **Tables:** skill_registry (public), skill_audits (IQ-gated), skill_vouches (public)
- **Row limit:** ~100 bytes. Full data via codeIn inscriptions.
- **Reads are free.** Only writes cost SOL.
- **Append-only.** No in-place updates. Version counter for re-registration.

## Prerequisites
- `@iqlabs-official/solana-sdk` v0.1.1+ (CommonJS required)
- `@solana/web3.js` v1.x
- Solana wallet for writes
- IQ tokens for audit writes (token mint: `3uXACfojUrya7VH51jVC1DCHq3uzK4A7g469Q954LABS`)
- Buffer monkey-patch applied (handled automatically by the package)
