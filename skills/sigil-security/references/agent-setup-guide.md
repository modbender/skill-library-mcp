# Agent Setup Guide — Sigil Protocol

## Understanding the 3 Addresses

| Address | What It Is | Fund It? |
|---------|-----------|----------|
| **Owner Wallet** | Your personal wallet (MetaMask etc.) that controls the Sigil account | ❌ Only for gas to manage settings |
| **Sigil Smart Account** | On-chain contract that holds funds and executes transactions | ✅ **FUND THIS ONE** |
| **Agent Key** | A dedicated signing EOA for UserOp signatures | ⚡ Small gas amount only (for UserOp submission) |

> 💡 The agent key signs UserOps locally. It needs a small amount of native token (POL/ETH/AVAX) for gas when submitting to the EntryPoint. Fund it with minimal gas only — never store significant value here.

---

## Quick Setup (5 Steps)

```
1. Deploy   → sigil.codes/onboarding (connect owner wallet, pick chain & strategy)
2. Fund     → Send tokens to your SIGIL ACCOUNT (holds value). Send small gas to AGENT KEY (for tx submission).
3. API Key  → sigil.codes/dashboard/agent-access → generate key (starts with sgil_)
4. Config   → Give your agent: SIGIL_API_KEY + SIGIL_ACCOUNT_ADDRESS + SIGIL_AGENT_SIGNER
5. Go       → Agent signs UserOps locally, submits via API. Guardian evaluates + co-signs.
```

---

## How Transactions Work

```
Agent builds tx
       ↓
POST /v1/evaluate  (with Bearer token from API key auth)
       ↓
┌─────────────────────────┐
│  Guardian 3-Layer Check  │
│  L1: Policy rules        │
│  L2: Tx simulation       │
│  L3: AI risk scoring     │
└─────────────────────────┘
       ↓
   APPROVE → Guardian co-signs → Sigil account executes (using ITS funds)
   REJECT  → Returns guidance on why + how to fix
   ESCALATE → Needs owner approval
```

**Key point:** The Sigil smart account pays for everything. The agent never touches funds directly.

---

## Common Mistakes

| Mistake | Why It's Wrong |
|---------|---------------|
| ❌ Funding the agent key address | Agent key is for auth only — funds sent there are stuck/wasted |
| ❌ Giving the agent your owner wallet credentials | Owner key controls freeze/withdraw/policy — agent should NEVER have it |
| ❌ Agent sending from its own wallet | Transactions must go through Guardian API, not direct on-chain sends |
| ❌ Using agent signer credential as a wallet | It's a signing key for API auth, not an EOA to hold funds |

---

## Minimal Code Example

### 1. Authenticate

```bash
# Get a Bearer token using your API key
curl -X POST https://api.sigil.codes/v1/agent/auth/api-key \
  -H "Content-Type: application/json" \
  -d '{"apiKey": "sgil_your_key_here"}'

# Response: { "token": "eyJ..." }
```

### 2. Evaluate a Transaction

```bash
# Submit a transaction for Guardian evaluation
curl -X POST https://api.sigil.codes/v1/evaluate \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "userOp": {
      "sender": "0xYourSigilAccount",
      "nonce": "0x0",
      "callData": "0x...",
      "accountGasLimits": "0x00000000000000000000000000030d4000000000000000000000000000030d40",
      "preVerificationGas": "50000",
      "gasFees": "0x00000000000000000000000059682f000000000000000000000005d21dba00",
      "signature": "0x"
    }
  }'
```

### 3. Check Result

```jsonc
// APPROVED — Guardian co-signed, ready to submit on-chain
{ "verdict": "APPROVE", "guardianSignature": "0x..." }

// REJECTED — Read the guidance field
{ "verdict": "REJECT", "guidance": "Transfer exceeds daily limit of 0.5 AVAX..." }
```

---

## Summary

```
Owner wallet    → manages policies (human only)
Sigil account   → holds funds, executes txs  ← FUND THIS
Agent key       → authenticates API calls     ← DON'T FUND
```
