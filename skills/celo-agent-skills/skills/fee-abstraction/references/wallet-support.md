# Wallet Support for Fee Abstraction

Source: https://docs.celo.org/wallet

## Overview

Celo's fee abstraction feature requires wallets that support the `feeCurrency` field in transactions. Most standard EVM wallets don't support this field.

## Wallet Compatibility

### Full Support

These wallets natively support fee abstraction:

| Wallet | Type | Fee Currency Selection | Notes |
|--------|------|----------------------|-------|
| MiniPay | Mobile | Automatic (cUSD) | Built into Opera Mini, optimized for stablecoin payments |
| Valora | Mobile | User selectable | Native Celo wallet with full fee currency support |
| Celo Terminal | Desktop | User selectable | Desktop wallet with Ledger support |

### No Support

These wallets use Ethereum-compatible transaction formats without `feeCurrency`:

| Wallet | Reason | Workaround |
|--------|--------|------------|
| MetaMask | Uses standard EIP-1559 transactions | Gas paid in CELO only |
| Coinbase Wallet | Standard EVM format | Gas paid in CELO only |
| Trust Wallet | Standard EVM format | Gas paid in CELO only |
| Other EVM Wallets | Standard EVM format | Gas paid in CELO only |

> **Note**: When using MetaMask or other EVM wallets, gas fees will automatically be paid in CELO because they use Ethereum-compatible transaction formats.

## Building Custom Fee Currency Support

If you need fee abstraction with wallets that don't natively support it, you can build custom solutions:

### Option 1: Custom dApp UI

Build a dApp that constructs transactions with `feeCurrency` before sending to the wallet:

```typescript
import { createWalletClient, custom } from "viem";
import { celo } from "viem/chains";

const CUSD_ADDRESS = "0x765DE816845861e75A25fCA122bb6898B8B1282a";

const walletClient = createWalletClient({
  chain: celo,
  transport: custom(window.ethereum),
});

// Note: This only works if the wallet passes through the feeCurrency field
// Most EVM wallets will ignore this field
const hash = await walletClient.sendTransaction({
  account: address,
  to: recipient,
  value: 0n,
  feeCurrency: CUSD_ADDRESS,
});
```

### Option 2: Sponsored Transactions

Use a backend service to sponsor gas fees:

```typescript
// Backend service pays gas in fee currency on behalf of user
async function sponsorTransaction(userTx: Transaction) {
  const sponsorWallet = createWalletClient({
    account: sponsorAccount,
    chain: celo,
    transport: http(),
  });

  // Execute user's intent with sponsor paying gas
  return sponsorWallet.sendTransaction({
    ...userTx,
    feeCurrency: USDC_ADAPTER,
  });
}
```

### Option 3: Account Abstraction

For complex use cases, consider ERC-4337 Account Abstraction with a Paymaster:

- User signs operations (not transactions)
- Bundler submits the actual transaction
- Paymaster can pay gas in any token

## MiniPay Integration

MiniPay is optimized for stablecoin transactions with minimal gas fees.

### Detecting MiniPay

```typescript
function isMiniPay(): boolean {
  return (
    typeof window !== "undefined" &&
    window.ethereum?.isMiniPay === true
  );
}
```

### Using Fee Currency in MiniPay

```typescript
import { createWalletClient, custom, parseUnits } from "viem";
import { celo } from "viem/chains";

// MiniPay uses cUSD by default for fee currency
const CUSD_ADDRESS = "0x765DE816845861e75A25fCA122bb6898B8B1282a";

async function sendWithMiniPay(to: string, amountInCusd: string) {
  if (!isMiniPay()) {
    throw new Error("MiniPay not detected");
  }

  const walletClient = createWalletClient({
    chain: celo,
    transport: custom(window.ethereum),
  });

  const [address] = await walletClient.getAddresses();

  // Transfer cUSD with gas paid in cUSD
  const hash = await walletClient.sendTransaction({
    account: address,
    to: CUSD_ADDRESS,
    data: encodeFunctionData({
      abi: erc20Abi,
      functionName: "transfer",
      args: [to, parseUnits(amountInCusd, 18)],
    }),
    feeCurrency: CUSD_ADDRESS,
  });

  return hash;
}
```

## Valora Integration

Valora supports fee currency selection in its UI.

### Deep Linking

```typescript
// Open Valora with a payment request
const valoraUrl = `celo://wallet/pay?address=${recipient}&amount=${amount}&token=cUSD`;
window.open(valoraUrl);
```

### WalletConnect

Valora supports WalletConnect. When connected via WalletConnect, transactions can include `feeCurrency`:

```typescript
import { createWalletClient, custom } from "viem";
import { celo } from "viem/chains";

// Connected via WalletConnect to Valora
const walletClient = createWalletClient({
  chain: celo,
  transport: custom(walletConnectProvider),
});

// Valora will honor the feeCurrency field
const hash = await walletClient.sendTransaction({
  account: address,
  to: recipient,
  value: amount,
  feeCurrency: CUSD_ADDRESS,
});
```

## Recommendations

1. **For mobile-first apps**: Use MiniPay or Valora integration
2. **For web dApps**:
   - Support both MiniPay/Valora (with fee currency) and MetaMask (CELO gas)
   - Detect wallet type and adjust UX accordingly
3. **For sponsored transactions**: Build a backend service that pays gas on behalf of users
4. **For cross-wallet support**: Consider Account Abstraction (ERC-4337)

## Detection Example

```typescript
async function detectWalletCapabilities() {
  if (typeof window === "undefined" || !window.ethereum) {
    return { connected: false };
  }

  const isMiniPay = window.ethereum.isMiniPay === true;
  const isValora = window.ethereum.isValora === true;
  const supportsFeeCurrency = isMiniPay || isValora;

  return {
    connected: true,
    isMiniPay,
    isValora,
    supportsFeeCurrency,
    recommendedFeeCurrency: supportsFeeCurrency
      ? "0x765DE816845861e75A25fCA122bb6898B8B1282a" // cUSD
      : undefined,
  };
}
```
