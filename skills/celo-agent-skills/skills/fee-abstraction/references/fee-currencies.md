# Fee Currencies Reference

Source: https://docs.celo.org/developer/fee-currency

## Overview

Celo allows paying gas fees in tokens other than the native CELO currency. The protocol maintains a governable allowlist of tokens through the `FeeCurrencyDirectory` contract.

## Mainnet Fee Currencies (Chain ID: 42220)

| Token | Decimals | Token Address | Adapter Address | Use in feeCurrency |
|-------|----------|---------------|-----------------|-------------------|
| CELO | 18 | Native | - | Leave empty |
| USDC | 6 | 0xcebA9300f2b948710d2653dD7B07f33A8B32118C | 0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B | Adapter |
| USDT | 6 | 0x48065fbbe25f71c9282ddf5e1cd6d6a887483d5e | 0x0e2a3e05bc9a16f5292a6170456a710cb89c6f72 | Adapter |
| cUSD | 18 | 0x765DE816845861e75A25fCA122bb6898B8B1282a | - | Token |
| cEUR | 18 | 0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73 | - | Token |
| cREAL | 18 | 0xe8537a3d056DA446677B9E9d6c5dB704EaAb4787 | - | Token |

## Celo Sepolia Testnet Fee Currencies (Chain ID: 11142220)

| Token | Decimals | Token Address | Adapter Address | Use in feeCurrency |
|-------|----------|---------------|-----------------|-------------------|
| CELO | 18 | Native | - | Leave empty |
| USDC | 6 | 0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B | 0x4822e58de6f5e485eF90df51C41CE01721331dC0 | Adapter |

## Why Adapters?

Adapters are needed to normalize decimals for tokens that use different precision:

- USDC and USDT use **6 decimals**
- Celo's gas calculations use **18 decimals** internally
- Adapters convert between these precisions

For 18-decimal tokens (cUSD, cEUR, cREAL), use the token address directly.

## TypeScript Constants

```typescript
// Mainnet Fee Currency Addresses
export const MAINNET_FEE_CURRENCIES = {
  USDC: {
    token: "0xcebA9300f2b948710d2653dD7B07f33A8B32118C",
    adapter: "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B",
    decimals: 6,
  },
  USDT: {
    token: "0x48065fbbe25f71c9282ddf5e1cd6d6a887483d5e",
    adapter: "0x0e2a3e05bc9a16f5292a6170456a710cb89c6f72",
    decimals: 6,
  },
  cUSD: {
    token: "0x765DE816845861e75A25fCA122bb6898B8B1282a",
    adapter: null, // Use token address directly
    decimals: 18,
  },
  cEUR: {
    token: "0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73",
    adapter: null,
    decimals: 18,
  },
  cREAL: {
    token: "0xe8537a3d056DA446677B9E9d6c5dB704EaAb4787",
    adapter: null,
    decimals: 18,
  },
} as const;

// Testnet Fee Currency Addresses
export const SEPOLIA_FEE_CURRENCIES = {
  USDC: {
    token: "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B",
    adapter: "0x4822e58de6f5e485eF90df51C41CE01721331dC0",
    decimals: 6,
  },
} as const;

// Helper to get feeCurrency address
export function getFeeCurrencyAddress(
  currency: keyof typeof MAINNET_FEE_CURRENCIES,
  isTestnet = false
): `0x${string}` | undefined {
  const currencies = isTestnet ? SEPOLIA_FEE_CURRENCIES : MAINNET_FEE_CURRENCIES;
  const config = currencies[currency as keyof typeof currencies];
  if (!config) return undefined;

  // Use adapter if available, otherwise use token address
  return (config.adapter || config.token) as `0x${string}`;
}
```

## FeeCurrencyDirectory Contract

The allowlist of fee currencies is maintained in the `FeeCurrencyDirectory` contract.

**Contract Address (all networks):** `0x9212Fb72ae65367A7c887eC4Ad9bE310BAC611BF`

### Query Available Currencies

```typescript
import { createPublicClient, http } from "viem";
import { celo } from "viem/chains";

const FEE_CURRENCY_DIRECTORY = "0x9212Fb72ae65367A7c887eC4Ad9bE310BAC611BF";

const FEE_CURRENCY_DIRECTORY_ABI = [
  {
    name: "getCurrencies",
    type: "function",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "address[]" }],
  },
  {
    name: "getCurrencyConfig",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "token", type: "address" }],
    outputs: [
      { name: "oracle", type: "address" },
      { name: "intrinsicGas", type: "uint256" },
    ],
  },
] as const;

const publicClient = createPublicClient({
  chain: celo,
  transport: http("https://forno.celo.org"),
});

// Get all allowed fee currencies
const currencies = await publicClient.readContract({
  address: FEE_CURRENCY_DIRECTORY,
  abi: FEE_CURRENCY_DIRECTORY_ABI,
  functionName: "getCurrencies",
});

console.log("Allowed fee currencies:", currencies);
```

### Using celocli

```bash
# List all whitelisted fee currencies
celocli network:whitelist --node https://forno.celo.org

# For testnet
celocli network:whitelist --node https://forno.celo-sepolia.celo-testnet.org
```

## Transaction Type

Fee currency transactions use CIP-64 transaction type `0x7b` (123 in decimal).

## Gas Overhead

Transactions using non-CELO fee currencies incur approximately **50,000 additional gas** for the fee currency conversion.

## Viem Usage Examples

### Basic Transaction

```typescript
import { createWalletClient, custom, parseEther } from "viem";
import { celo } from "viem/chains";

const USDC_ADAPTER = "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B";

const walletClient = createWalletClient({
  chain: celo,
  transport: custom(window.ethereum),
});

const hash = await walletClient.sendTransaction({
  account: address,
  to: recipient,
  value: parseEther("0.01"),
  feeCurrency: USDC_ADAPTER,
});
```

### Serialize Transaction

```typescript
import { serializeTransaction } from "viem/celo";
import { parseGwei, parseEther } from "viem";

const USDC_ADAPTER = "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B";

const serialized = serializeTransaction({
  chainId: 42220,
  gas: 21001n,
  feeCurrency: USDC_ADAPTER,
  maxFeePerGas: parseGwei("20"),
  maxPriorityFeePerGas: parseGwei("2"),
  nonce: 69,
  to: "0x1234512345123451234512345123451234512345",
  value: parseEther("0.01"),
});
```

### Get Gas Price in Fee Currency

```typescript
import { createPublicClient, http } from "viem";
import { celo } from "viem/chains";

const USDC_ADAPTER = "0x2F25deB3848C207fc8E0c34035B3Ba7fC157602B";

const publicClient = createPublicClient({
  chain: celo,
  transport: http("https://forno.celo.org"),
});

const priceHex = await publicClient.request({
  method: "eth_gasPrice",
  params: [USDC_ADAPTER],
});

const gasPrice = BigInt(priceHex);
```

## Library Support

| Library | feeCurrency Support |
|---------|---------------------|
| viem | Supported |
| ethers.js | Not supported |
| web3.js | Not supported |

Viem is the recommended library for Celo development when using fee currencies.
