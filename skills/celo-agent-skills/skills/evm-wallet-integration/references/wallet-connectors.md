# Wallet Connectors Reference

## Wagmi Connectors

Source: https://wagmi.sh/react/guides/connect-wallet

### Injected (Browser Extension)

Connects to any injected wallet (MetaMask, Coinbase, etc.)

```typescript
import { injected } from "wagmi/connectors";

const connector = injected();
```

### MetaMask

Specifically targets MetaMask.

```typescript
import { metaMask } from "wagmi/connectors";

const connector = metaMask();
```

### WalletConnect (via Reown)

Universal wallet connection via QR code or deep link. WalletConnect rebranded to Reown in 2024.

- **Library imports**: Still use `walletConnect` from wagmi
- **Project ID**: Get from [cloud.reown.com](https://cloud.reown.com)

```typescript
import { walletConnect } from "wagmi/connectors";

// Get project ID from cloud.reown.com (Reown is WalletConnect's new name)
const connector = walletConnect({
  projectId: process.env.NEXT_PUBLIC_REOWN_PROJECT_ID!,
});
```

### Coinbase Wallet

Coinbase Wallet and Coinbase Smart Wallet.

```typescript
import { coinbaseWallet } from "wagmi/connectors";

const connector = coinbaseWallet({
  appName: "My Celo App",
});
```

### Safe

Connect to Safe (Gnosis Safe) wallets.

```typescript
import { safe } from "wagmi/connectors";

const connector = safe();
```

## Reown AppKit Configuration

Source: https://docs.reown.com/appkit

Reown AppKit provides a pre-built UI and handles wallet connections automatically. Use this instead of manual connector setup for most apps.

```typescript
import { WagmiAdapter } from "@reown/appkit-adapter-wagmi";
import { celo, celoAlfajores } from "@reown/appkit/networks";
import { createAppKit } from "@reown/appkit/react";

const projectId = process.env.NEXT_PUBLIC_REOWN_PROJECT_ID!;

const wagmiAdapter = new WagmiAdapter({
  networks: [celo, celoAlfajores],
  projectId,
  ssr: true,
});

createAppKit({
  adapters: [wagmiAdapter],
  networks: [celo, celoAlfajores],
  projectId,
  metadata: {
    name: "My Celo App",
    description: "Celo dApp",
    url: "https://myapp.com",
    icons: ["https://myapp.com/icon.png"],
  },
});

export const config = wagmiAdapter.wagmiConfig;
```

## Complete Wagmi Config with Connectors

```typescript
import { http, createConfig } from "wagmi";
import { celo, celoSepolia } from "wagmi/chains";
import {
  injected,
  metaMask,
  walletConnect,
  coinbaseWallet,
  safe,
} from "wagmi/connectors";

const projectId = process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID!;

export const config = createConfig({
  chains: [celo, celoSepolia],
  connectors: [
    injected(),
    metaMask(),
    walletConnect({ projectId }),
    coinbaseWallet({ appName: "My Celo App" }),
    safe(),
  ],
  transports: {
    [celo.id]: http("https://forno.celo.org"),
    [celoSepolia.id]: http("https://forno.celo-sepolia.celo-testnet.org"),
  },
});
```

## Thirdweb Wallets

```typescript
import { createWallet } from "thirdweb/wallets";

const wallets = [
  createWallet("io.metamask"),
  createWallet("com.coinbase.wallet"),
  createWallet("walletConnect"),
];
```

## Wallet Detection

### Check if Wallet Available

```typescript
function isMetaMaskInstalled(): boolean {
  return typeof window !== "undefined" && !!window.ethereum?.isMetaMask;
}

function isWalletConnected(): boolean {
  return typeof window !== "undefined" && !!window.ethereum?.selectedAddress;
}
```

### Get Available Connectors

```tsx
import { useConnectors } from "wagmi";

function AvailableWallets() {
  const connectors = useConnectors();

  return (
    <ul>
      {connectors.map((connector) => (
        <li key={connector.uid}>
          {connector.name} - {connector.type}
        </li>
      ))}
    </ul>
  );
}
```

## WalletConnect Project ID (via Reown)

Required for WalletConnect v2 connections. Reown (formerly WalletConnect Inc.) provides the cloud infrastructure.

1. Go to [cloud.reown.com](https://cloud.reown.com)
2. Create new project (select "AppKit" or "WalletKit")
3. Copy project ID
4. Add to environment variables

```bash
# For Reown AppKit
NEXT_PUBLIC_REOWN_PROJECT_ID=your_project_id

# For direct wagmi walletConnect connector (same ID works)
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID=your_project_id
```

> **Note**: The npm packages and code imports remain `walletConnect` - only the company and cloud console were rebranded to Reown.
