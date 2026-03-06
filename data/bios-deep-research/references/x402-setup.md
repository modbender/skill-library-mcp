# x402 Signer Setup

**This guide is for the human operator**, not the agent. The agent never handles private keys or signing material — it only sends pre-signed payment headers produced by your signer.

Configure a wallet to sign x402 payments for BIOS deep research. You need a wallet on **Base mainnet** (chain ID 8453) with USDC balance.

## Security Recommendations

- **Use a dedicated wallet** with only the USDC needed for research. Do not use your primary wallet.
- **Prefer managed signers** (Coinbase CDP, hardware wallets) over raw private keys.
- **Never commit secrets to version control.**
- **Scope exposure:** the x402 "exact" scheme only authorizes a specific payment amount to a specific recipient — it cannot drain your wallet.

## Wallet Options

Any wallet that can produce EIP-712 signatures works. Listed from most to least recommended:

| Method | Security | How |
|--------|----------|-----|
| **Coinbase CDP** | Managed keys, scoped access | Use `cdp-sdk` with `sign_typed_data()` |
| **Hardware wallet** | Keys never leave device | Via MetaMask/Rabby bridge |
| **MPC / multisig** | Distributed signing | Any signer that produces valid EIP-712 signatures |
| **Private key** | Least secure — use a dedicated wallet | Sign locally with viem, ethers.js, web3.py |

## Python Setup

### Install dependencies

```bash
# Coinbase CDP wallet (recommended):
pip install x402 httpx cdp-sdk

# Private key wallet (use a dedicated wallet only):
pip install x402 httpx eth-account
```

### Coinbase CDP signer (recommended)

```python
from x402 import x402Client
from x402.mechanisms.evm.exact import register_exact_evm_client
from cdp import Cdp, Wallet

Cdp.configure(api_key_id="YOUR_CDP_KEY_ID", api_key_secret="YOUR_CDP_SECRET")
wallet = Wallet.fetch("YOUR_WALLET_ID")

client = x402Client()
register_exact_evm_client(client, signer=wallet, networks="eip155:8453")
```

### Private key signer

Only use a dedicated wallet with limited funds. Never use your primary wallet's private key.

```python
from x402 import x402Client
from x402.mechanisms.evm.exact import register_exact_evm_client
from eth_account import Account

signer = Account.from_key("0xYOUR_PRIVATE_KEY")

client = x402Client()
register_exact_evm_client(client, signer=signer, networks="eip155:8453")
```

### Handling the 402 flow

```python
from x402 import parse_payment_required
from x402.http.utils import encode_payment_signature_header

# After receiving 402 response:
payment_required = parse_payment_required(response_data)
payment_payload = await client.create_payment_payload(payment_required)
header_value = encode_payment_signature_header(payment_payload)

# Retry with payment headers:
headers = {
    "X-PAYMENT": header_value,
    "PAYMENT-SIGNATURE": header_value,
    "Content-Type": "application/json"
}
```

## TypeScript/Node Setup

### Install dependencies

```bash
npm install @x402/core @x402/evm viem
```

### Signer setup

```typescript
import { x402Client } from '@x402/core/client';
import { x402HTTPClient } from '@x402/core/http';
import { ExactEvmScheme } from '@x402/evm';

// signer = any viem-compatible wallet client with { address, signTypedData }
const scheme = new ExactEvmScheme(signer);
const client = new x402Client();
client.register('eip155:8453', scheme);
const httpClient = new x402HTTPClient(client);
```

See the [x402 documentation](https://github.com/coinbase/x402) for complete examples.

## EIP-712 Domain (Reference)

The x402 "exact" scheme uses this EIP-712 domain:

```json
{
  "name": "x402",
  "version": "1",
  "chainId": 8453,
  "verifyingContract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
}
```

The verifying contract is the USDC contract on Base mainnet.
