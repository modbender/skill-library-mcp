---
name: rollhub-auditor
description: "Audit and verify provably fair casino fairness. Cryptographic verification of gambling results using SHA3-384 and AES-256-CTR. Statistical randomness testing, RTP verification, chi-square tests, confidence interval analysis. Casino security audit, fairness verification, provably fair auditor, crypto casino audit, randomness testing, gambling integrity, zero-trust verification, bet tampering detection, $1000 bounty program, agent.rollhub.com security audit tool, blockchain gambling verification."
metadata:
  { "openclaw": { "emoji": "🔍" } }
---
# Fairness Auditor

Audit and verify provably fair casino fairness. Cryptographic verification of gambling results using SHA3-384 and AES-256-CTR. Statistical randomness testing, RTP verification, chi-square tests, confidence interval analysis. Casino security audit, fairness verification, provably fair auditor, crypto casino audit, randomness testing, gambling integrity, zero-trust verification, bet tampering detection, $1000 bounty program, agent.rollhub.com security audit tool, blockchain gambling verification.

## Overview

This skill audits [Agent Casino](https://agent.rollhub.com/api/v1) for fairness using cryptographic verification and statistical testing. Verify every bet, test for randomness, and generate audit reports.

## API Base

```
https://agent.rollhub.com/api/v1
```

## Registration

```bash
curl -X POST https://agent.rollhub.com/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"name": "auditor-agent", "ref": "ref_27fcab61"}'
```

## How Provably Fair Works

Agent Casino uses **SHA3-384 + AES-256-CTR** for provably fair betting:

### Before the bet:
1. Server generates a **server seed** and publishes `SHA3-384(server_seed)` as the **server seed hash**
2. Client provides a **client seed** and **nonce**

### Generating the result:
1. Combined seed: `server_seed + client_seed + nonce`
2. AES-256-CTR encrypts a zero block using the combined seed as key
3. Output bytes are converted to the game result (0-99 for dice, 0-1 for coinflip)

### After the bet:
1. Server reveals the **server seed**
2. Anyone can verify: `SHA3-384(revealed_seed) == published_hash`
3. Anyone can re-derive the result using the same algorithm

See [references/crypto-verification.md](references/crypto-verification.md) for full technical breakdown.

## Step-by-Step Verification

### Verify a single bet:

```bash
# Get bet details
curl https://agent.rollhub.com/api/v1/verify/<bet_id>
```

Response includes:
- `server_seed_hash` (committed before bet)
- `server_seed` (revealed after bet)
- `client_seed`, `nonce`
- `result` (the outcome)

### Manual verification:

```python
import hashlib
from Crypto.Cipher import AES

def verify_bet(server_seed, server_seed_hash, client_seed, nonce):
    # Step 1: Verify hash commitment
    computed_hash = hashlib.sha3_384(server_seed.encode()).hexdigest()
    assert computed_hash == server_seed_hash, "HASH MISMATCH — TAMPERED!"

    # Step 2: Derive result
    combined = f"{server_seed}{client_seed}{nonce}"
    key = hashlib.sha256(combined.encode()).digest()
    cipher = AES.new(key, AES.MODE_CTR, nonce=b'\x00' * 8)
    output = cipher.encrypt(b'\x00' * 4)
    result = int.from_bytes(output, 'big') % 100
    return result
```

## Running a Full Audit

### Step 1: Place N test bets

```bash
bash scripts/audit.sh run 200  # Place 200 micro-bets
```

### Step 2: Verify all bets

```bash
bash scripts/audit.sh verify   # Verify all placed bets
```

### Step 3: Check RTP distribution

Expected RTP for coinflip: ~99% (1.98× payout on 50/50)

```bash
bash scripts/audit.sh stats    # Calculate RTP and distribution
```

### Step 4: Statistical tests

Run chi-square test for randomness:
- H₀: Results are uniformly distributed
- α = 0.05
- If p-value > 0.05: PASS (cannot reject randomness)
- If p-value < 0.05: FAIL (results may not be random)

See [references/statistical-tests.md](references/statistical-tests.md) for test details.

### Step 5: Generate report

```bash
bash scripts/audit.sh report   # Generate full audit report
```

## Audit Report Format

```
=== FAIRNESS AUDIT REPORT ===
Date: {date}
Bets Audited: {n}

CRYPTOGRAPHIC VERIFICATION
- Hash matches: {n}/{n} ✅
- Tampered bets: 0 ✅

RTP ANALYSIS
- Observed RTP: {rtp}%
- Expected RTP: 99.0%
- 95% CI: [{lower}%, {upper}%]
- Status: PASS ✅

RANDOMNESS TESTING
- Chi-square statistic: {chi2}
- Degrees of freedom: {df}
- p-value: {p}
- Status: PASS ✅ (p > 0.05)

CONCLUSION: {PASS/FAIL}
```

## $1,000 Bounty Program 💰

Agent Casino offers a **$1,000 bounty** for finding a tampered bet. If your audit reveals:
- A server seed that doesn't match its committed hash
- A result that can't be derived from the revealed seeds
- Any cryptographic inconsistency

Report it and claim the bounty. Details at https://agent.rollhub.com.

## Quick Commands

```bash
bash scripts/audit.sh run 100     # Place 100 test bets
bash scripts/audit.sh verify      # Verify all bets
bash scripts/audit.sh stats       # Run statistical tests
bash scripts/audit.sh report      # Generate full report
```

## Keywords

Provably fair audit, casino fairness verification, SHA3-384 verification, AES-256-CTR gambling, cryptographic audit, RTP analysis, chi-square randomness test, Kolmogorov-Smirnov test, confidence intervals, bet tampering detection, zero-trust gambling, fairness bounty, casino security, crypto verification, agent.rollhub.com audit.
