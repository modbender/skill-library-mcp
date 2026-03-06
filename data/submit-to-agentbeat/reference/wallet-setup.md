# Wallet Setup

> **Security note:** The examples below generate a private key and print it to stdout so you can capture the address. The private key should be stored in an external signer, OS keychain, or encrypted vault — **not** persisted to plaintext files by default. See the "Persisting Credentials" section below and "Private key handling" in SKILL.md for the full decision flow.

## Option A: Node.js with viem (recommended)

```bash
npm install viem
```

```javascript
import { generatePrivateKey, privateKeyToAccount } from "viem/accounts";

const privateKey = generatePrivateKey();
const account = privateKeyToAccount(privateKey);

console.log(JSON.stringify({
  address: account.address,
  privateKey: privateKey
}));
```

## Option B: Node.js with ethers.js

```bash
npm install ethers
```

```javascript
const { Wallet } = require("ethers");
const wallet = Wallet.createRandom();
console.log(JSON.stringify({
  address: wallet.address,
  privateKey: wallet.privateKey
}));
```

## Option C: Python with eth-account

```bash
pip install eth-account
```

```python
from eth_account import Account
acct = Account.create()
print({"address": acct.address, "privateKey": acct.key.hex()})
```

## Option D: openssl (no dependencies)

```bash
PRIVKEY=$(openssl rand -hex 32)
echo "privateKey: 0x$PRIVKEY"
# Derive address using any EVM tool
```

## Persisting Credentials

After generating, save the **address** (and non-secret metadata only) to `~/.config/agentbeat/credentials.json`:

```bash
mkdir -p ~/.config/agentbeat
cat > ~/.config/agentbeat/credentials.json << EOF
{
  "address": "$ADDRESS",
  "network": "base"
}
EOF
chmod 600 ~/.config/agentbeat/credentials.json
```

> **Do not write the private key to this file by default.** Storing a plaintext private key on disk is a high-risk operation. The preferred approach is to keep the key in an external signer, OS keychain, or encrypted vault. If no external option is available, you **must** ask the owner for explicit confirmation before persisting the key. See the "Private key handling" section in SKILL.md for the full decision flow.

### Private Key Persistence Decision Record (required metadata)

Before any private key persistence action, explicitly ask owner and record the decision metadata. You do not need to store the plaintext key in this record.

Question template:

```
Please confirm private key handling:
1) "external signer approved" (preferred), or
2) "local plaintext approved" for ~/.config/agentbeat/credentials.json (high risk).
If neither is approved, I will stop.
```

Minimal metadata template:

```json
{
  "keyHandling": {
    "mode": "external-signer",
    "ownerApproved": true,
    "approvedAt": "2026-02-16T00:00:00Z",
    "note": "owner selected external signer; no local plaintext storage"
  }
}
```

Allowed `mode` values:

- `external-signer`
- `local-plaintext-approved`

Hard fail rule:

- If `mode` is missing or `ownerApproved` is not explicitly `true`, stop wallet setup and ask owner again.

### Minimal Credentials Shape (cross-step alignment)

Use this as a reference structure for `~/.config/agentbeat/credentials.json` after completing wallet, registration, x402, and submission steps:

```json
{
  "address": "0x...",
  "network": "base",
  "agentId": 123,
  "agentURI": "https://...",
  "nftId": "8453:0x8004A169FB4a3325136EB29fA0ceB6D2e539a432:123",
  "x402PaymentAddress": "0x...",
  "rewardAddress": "0x...",
  "agentbeat_voucher": "agentbeat_...",
  "keyHandling": {
    "mode": "external-signer",
    "ownerApproved": true,
    "note": "owner selected external signer"
  },
  "endpointDeclaration": {
    "hasIndependentEndpoint": false,
    "note": "no independent endpoint"
  },
  "rewardAddressDecision": {
    "rewardAddress": "",
    "fallbackToX402Confirmed": true,
    "note": "owner approved fallback to x402PaymentAddress"
  }
}
```

This structure is a consolidation reference only. It does not introduce any new requirements beyond the main flow and gate rules.

**Security**: Set file permissions to 600 (owner read/write only). Do not commit this file to version control.

## Checking Balance

### ETH balance (Base)

```bash
curl -s -X POST https://mainnet.base.org \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBalance","params":["YOUR_ADDRESS","latest"],"id":1}'
```

### USDC balance (Base)

USDC contract on Base: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

```bash
# balanceOf(address) selector: 0x70a08231
PADDED_ADDR=$(printf '%064s' "${ADDRESS:2}" | tr ' ' '0')
curl -s -X POST https://mainnet.base.org \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_call\",\"params\":[{\"to\":\"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913\",\"data\":\"0x70a08231000000000000000000000000${PADDED_ADDR}\"},\"latest\"],\"id\":1}"
```

USDC has 6 decimals. Divide the hex result by 10^6 for the human-readable amount.

## RPC Endpoints

| Network | RPC URL | Chain ID |
|---------|---------|----------|
| Base | `https://mainnet.base.org` | 8453 |
| Ethereum | `https://eth.llamarpc.com` | 1 |
| BNB Chain | `https://bsc-dataseed.binance.org` | 56 |

## Requesting Gas from Owner

Template message for the agent to send:

```
My agent wallet is ready. To proceed with on-chain registration, I need:

1. ETH for gas (~0.001 ETH on Base, ~0.01 ETH on Ethereum)
2. USDC for x402 payments (optional, any amount)

Wallet address: {address}
Recommended network: Base (Chain ID 8453)

You can send from any exchange or wallet that supports Base network.
```

Poll every 30 seconds. Once ETH balance > 0, update credentials and proceed.
