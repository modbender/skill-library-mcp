---
name: fee-abstraction
description: Pay gas fees with ERC-20 tokens on Celo. Covers supported tokens, implementation, and wallet compatibility.
license: Apache-2.0
metadata:
  author: celo-org
  version: "1.0.0"
---

# Fee Abstraction on Celo

This skill covers Celo's native fee abstraction feature that allows gas fees to be paid in ERC-20 tokens.

## When to Use

- Paying gas fees with stablecoins (USDC, USDT, cUSD)
- Building user-friendly dApps where users don't need CELO
- MiniPay integrations
- Any Celo transaction where users prefer stablecoin gas

## Overview

Celo's native fee abstraction allows gas fees to be paid in ERC-20 tokens without Account Abstraction, Paymasters, or Relay Services. Wallets simply add a `feeCurrency` field to transaction objects.

Source: https://docs.celo.org/developer/fee-currency

## Supported Fee Currencies

### Mainnet (Chain ID: 42220)

| Token | Token Address | Adapter Address | Use in feeCurrency |
|-------|---------------|-----------------|-------------------|
| USDC | 0xcebA9300f2b948710d2653dD7B07f33A8B32118C | 0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B | Adapter |
| USDT | 0x48065fbbe25f71c9282ddf5e1cd6d6a887483d5e | 0x0e2a3e05bc9a16f5292a6170456a710cb89c6f72 | Adapter |
| cUSD | 0x765DE816845861e75A25fCA122bb6898B8B1282a | - | Token |
| cEUR | 0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73 | - | Token |
| cREAL | 0xe8537a3d056DA446677B9E9d6c5dB704EaAb4787 | - | Token |

### Celo Sepolia Testnet (Chain ID: 11142220)

| Token | Token Address | Adapter Address | Use in feeCurrency |
|-------|---------------|-----------------|-------------------|
| USDC | 0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B | 0x4822e58de6f5e485eF90df51C41CE01721331dC0 | Adapter |

> **Important**: Use adapter addresses for 6-decimal tokens (USDC, USDT). Use token addresses directly for 18-decimal tokens (cUSD, cEUR, cREAL).

## Wallet Support

| Wallet | Fee Abstraction Support | Notes |
|--------|------------------------|-------|
| MiniPay | Full | Native support, recommended for mobile |
| Valora | Full | Native Celo wallet |
| MetaMask | No | Uses Ethereum tx format without feeCurrency field |
| Coinbase Wallet | No | Standard EVM format |
| Other EVM Wallets | No | Require custom dApp implementation |

> MetaMask and standard EVM wallets don't support fee abstraction because they use Ethereum-compatible transaction formats that don't include the `feeCurrency` field.

## Library Support

| Library | feeCurrency Support |
|---------|---------------------|
| viem | Supported |
| ethers.js | Not supported |
| web3.js | Not supported |

**viem is required for fee abstraction in dApps.**

## Basic Implementation

### Send Transaction with Fee Currency

```typescript
import { createWalletClient, custom, parseEther } from "viem";
import { celo } from "viem/chains";

// Use adapter address for USDC (6 decimals)
const USDC_ADAPTER = "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B";

const walletClient = createWalletClient({
  chain: celo,
  transport: custom(window.ethereum),
});

const [address] = await walletClient.getAddresses();

const hash = await walletClient.sendTransaction({
  account: address,
  to: "0xRecipientAddress",
  value: parseEther("0.01"),
  feeCurrency: USDC_ADAPTER, // Pay gas in USDC
});

console.log("Transaction hash:", hash);
```

### Estimate Gas Price in Fee Currency

```typescript
import { createPublicClient, http } from "viem";
import { celo } from "viem/chains";

const USDC_ADAPTER = "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B";

const publicClient = createPublicClient({
  chain: celo,
  transport: http("https://forno.celo.org"),
});

// Get gas price in USDC
const priceHex = await publicClient.request({
  method: "eth_gasPrice",
  params: [USDC_ADAPTER],
});

const gasPrice = BigInt(priceHex);
console.log("Gas price in USDC:", gasPrice);
```

### Serialize Transaction (CIP-64)

```typescript
import { serializeTransaction } from "viem/celo";
import { parseGwei, parseEther } from "viem";

const USDC_ADAPTER = "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B";

const serialized = serializeTransaction({
  chainId: 42220,
  gas: 21000n,
  feeCurrency: USDC_ADAPTER,
  maxFeePerGas: parseGwei("20"),
  maxPriorityFeePerGas: parseGwei("2"),
  nonce: 1,
  to: "0xRecipientAddress",
  value: parseEther("0.01"),
});
```

## Key Concepts

### Transaction Type

Fee currency transactions use CIP-64 type `0x7b` (123 decimal). This is a Celo-specific transaction type.

### Gas Overhead

Non-CELO fee currencies add approximately 50,000 gas overhead for the currency conversion.

### Adapters vs Token Addresses

- **6-decimal tokens** (USDC, USDT): Must use adapter address
- **18-decimal tokens** (cUSD, cEUR, cREAL): Use token address directly

Adapters normalize decimals since Celo's gas calculations use 18 decimals internally.

### Querying Available Currencies

**Using celocli:**
```bash
celocli network:whitelist --node https://forno.celo.org
```

**Using FeeCurrencyDirectory contract:**
```typescript
import { createPublicClient, http } from "viem";
import { celo } from "viem/chains";

const FEE_CURRENCY_DIRECTORY = "0x9212Fb72ae65367A7c887eC4Ad9bE310BAC611BF";

const publicClient = createPublicClient({
  chain: celo,
  transport: http("https://forno.celo.org"),
});

const currencies = await publicClient.readContract({
  address: FEE_CURRENCY_DIRECTORY,
  abi: [{
    name: "getCurrencies",
    type: "function",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "address[]" }],
  }],
  functionName: "getCurrencies",
});

console.log("Allowed fee currencies:", currencies);
```

## Limitations

1. **Wallet Dependency**: Only works with Celo-native wallets (MiniPay, Valora) or custom dApp implementations
2. **Library Dependency**: Requires viem (ethers.js/web3.js don't support feeCurrency)
3. **Gas Overhead**: ~50k additional gas for non-CELO currencies
4. **Balance Requirements**: User must have sufficient balance in the chosen fee currency

## Advanced: Custom Fee Currency Selector UI

Build a UI that lets users choose their gas payment token:

```tsx
import { useState } from "react";
import { useAccount, useBalance } from "wagmi";
import { celo } from "viem/chains";

const FEE_CURRENCIES = [
  { symbol: "CELO", address: null, adapter: null },
  {
    symbol: "USDC",
    address: "0xcebA9300f2b948710d2653dD7B07f33A8B32118C",
    adapter: "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B",
  },
  {
    symbol: "USDT",
    address: "0x48065fbbe25f71c9282ddf5e1cd6d6a887483d5e",
    adapter: "0x0e2a3e05bc9a16f5292a6170456a710cb89c6f72",
  },
  {
    symbol: "cUSD",
    address: "0x765DE816845861e75A25fCA122bb6898B8B1282a",
    adapter: null,
  },
];

interface FeeCurrency {
  symbol: string;
  address: string | null;
  adapter: string | null;
}

function FeeCurrencySelector({
  onSelect,
}: {
  onSelect: (currency: FeeCurrency) => void;
}) {
  const { address } = useAccount();
  const [selected, setSelected] = useState(0);

  const handleChange = (index: number) => {
    setSelected(index);
    onSelect(FEE_CURRENCIES[index]);
  };

  return (
    <div>
      <label>Pay gas with:</label>
      <select
        value={selected}
        onChange={(e) => handleChange(Number(e.target.value))}
      >
        {FEE_CURRENCIES.map((currency, i) => (
          <option key={currency.symbol} value={i}>
            {currency.symbol}
          </option>
        ))}
      </select>
    </div>
  );
}

// Usage in transaction
function useFeeCurrencyTransaction() {
  const [feeCurrency, setFeeCurrency] = useState<FeeCurrency>(FEE_CURRENCIES[0]);

  const getFeeCurrencyAddress = () => {
    if (!feeCurrency.address) return undefined; // CELO native
    return feeCurrency.adapter || feeCurrency.address;
  };

  return { feeCurrency, setFeeCurrency, getFeeCurrencyAddress };
}
```

## Advanced: Server-Side Transaction Building

Build fee currency transactions server-side for gasless or sponsored transactions:

```typescript
import { createWalletClient, http, parseEther } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { celo } from "viem/chains";

const USDC_ADAPTER = "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B";

async function buildSponsoredTransaction(
  recipientAddress: `0x${string}`,
  amount: bigint
) {
  // Sponsor account pays gas in USDC
  const sponsorAccount = privateKeyToAccount(
    process.env.SPONSOR_PRIVATE_KEY as `0x${string}`
  );

  const walletClient = createWalletClient({
    account: sponsorAccount,
    chain: celo,
    transport: http("https://forno.celo.org"),
  });

  const hash = await walletClient.sendTransaction({
    to: recipientAddress,
    value: amount,
    feeCurrency: USDC_ADAPTER,
  });

  return hash;
}

// Example: sponsor a user's transaction
async function sponsorUserTransfer() {
  const hash = await buildSponsoredTransaction(
    "0xUserAddress",
    parseEther("1")
  );
  console.log("Sponsored transaction:", hash);
}
```

## Additional Resources

- [fee-currencies.md](references/fee-currencies.md) - Complete token addresses and adapters
- [wallet-support.md](references/wallet-support.md) - Detailed wallet compatibility guide
