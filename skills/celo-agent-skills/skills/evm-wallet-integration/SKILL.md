---
name: evm-wallet-integration
description: Integrate wallets into Celo dApps. Covers RainbowKit, Dynamic, and wallet connection patterns.
license: Apache-2.0
metadata:
  author: celo-org
  version: "1.0.0"
---

# EVM Wallet Integration for Celo

This skill covers integrating wallet connection libraries into Celo dApps.

## When to Use

- Adding wallet connection to a dApp
- Supporting multiple wallet types
- Implementing authentication flows
- Building wallet experiences

## Wallet Connection Libraries

| Library | Description | Best For |
|---------|-------------|----------|
| Reown AppKit | Official WalletConnect SDK with wagmi | Production React apps |
| Dynamic | Auth-focused with dashboard | Apps needing user management |
| ConnectKit | Simple wagmi integration | Quick setup |
| Custom wagmi | Direct connector setup | Full control |

## Reown AppKit

Official WalletConnect SDK for React apps with built-in wallet UI. Supports 600+ wallets.

Source: https://docs.reown.com/appkit

> **Note**: Reown is the company formerly known as WalletConnect Inc. (rebranded in 2024). The protocol and npm packages for wagmi connectors still use "walletConnect" naming.

### Installation

```bash
npm install @reown/appkit @reown/appkit-adapter-wagmi wagmi viem @tanstack/react-query
```

### Get Project ID

1. Go to [cloud.reown.com](https://cloud.reown.com)
2. Create a new project
3. Copy the project ID

### Configuration

```typescript
// config.ts
import { WagmiAdapter } from "@reown/appkit-adapter-wagmi";
import { celo, celoAlfajores } from "@reown/appkit/networks";

const projectId = process.env.NEXT_PUBLIC_REOWN_PROJECT_ID!;

export const wagmiAdapter = new WagmiAdapter({
  networks: [celo, celoAlfajores],
  projectId,
  ssr: true,
});

export const config = wagmiAdapter.wagmiConfig;
```

### Provider Setup

```tsx
"use client";
import { WagmiProvider } from "wagmi";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createAppKit } from "@reown/appkit/react";
import { wagmiAdapter } from "./config";
import { celo, celoAlfajores } from "@reown/appkit/networks";

const queryClient = new QueryClient();

createAppKit({
  adapters: [wagmiAdapter],
  networks: [celo, celoAlfajores],
  projectId: process.env.NEXT_PUBLIC_REOWN_PROJECT_ID!,
  metadata: {
    name: "My Celo App",
    description: "Celo dApp",
    url: "https://myapp.com",
    icons: ["https://myapp.com/icon.png"],
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <WagmiProvider config={wagmiAdapter.wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </WagmiProvider>
  );
}
```

### Connect Button

```tsx
import { AppKitButton } from "@reown/appkit/react";

function Header() {
  return (
    <nav>
      <AppKitButton />
    </nav>
  );
}
```

### Custom Connect Button

```tsx
import { useAppKit, useAppKitAccount } from "@reown/appkit/react";

function WalletConnect() {
  const { open } = useAppKit();
  const { address, isConnected } = useAppKitAccount();

  if (isConnected) {
    return (
      <div>
        <p>Connected: {address}</p>
        <button onClick={() => open({ view: "Account" })}>Account</button>
      </div>
    );
  }

  return <button onClick={() => open()}>Connect Wallet</button>;
}
```

### Using Wagmi Hooks with AppKit

```tsx
import { useAccount, useBalance, useDisconnect } from "wagmi";

function AccountInfo() {
  const { address, isConnected } = useAccount();
  const { data: balance } = useBalance({ address });
  const { disconnect } = useDisconnect();

  if (!isConnected) return null;

  return (
    <div>
      <p>Address: {address}</p>
      <p>Balance: {balance?.formatted} {balance?.symbol}</p>
      <button onClick={() => disconnect()}>Disconnect</button>
    </div>
  );
}
```

## Dynamic

Authentication-focused wallet connection with user management dashboard.

Source: https://docs.dynamic.xyz

### Installation

```bash
npm install @dynamic-labs/sdk-react
```

### Setup

```tsx
import {
  DynamicContextProvider,
  DynamicWidget,
} from "@dynamic-labs/sdk-react";

function App() {
  return (
    <DynamicContextProvider
      settings={{
        environmentId: process.env.NEXT_PUBLIC_DYNAMIC_ENV_ID!,
      }}
    >
      <DynamicWidget />
    </DynamicContextProvider>
  );
}
```

### Enable Celo

1. Go to app.dynamic.xyz dashboard
2. Navigate to Configurations
3. Select EVM card
4. Toggle Celo on

## Custom Implementation

Build wallet connection without a library using wagmi directly.

### Wagmi Configuration

```typescript
import { http, createConfig } from "wagmi";
import { celo, celoSepolia } from "wagmi/chains";
import { injected, walletConnect, metaMask } from "wagmi/connectors";

const projectId = process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID!;

export const config = createConfig({
  chains: [celo, celoSepolia],
  connectors: [
    injected(),
    walletConnect({ projectId }),
    metaMask(),
  ],
  transports: {
    [celo.id]: http(),
    [celoSepolia.id]: http(),
  },
});
```

### Wallet Connect Component

```tsx
import { useConnect, useConnectors, useAccount, useDisconnect } from "wagmi";

function WalletConnect() {
  const { connect } = useConnect();
  const connectors = useConnectors();
  const { address, isConnected } = useAccount();
  const { disconnect } = useDisconnect();

  if (isConnected) {
    return (
      <div>
        <p>Connected: {address}</p>
        <button onClick={() => disconnect()}>Disconnect</button>
      </div>
    );
  }

  return (
    <div>
      {connectors.map((connector) => (
        <button
          key={connector.uid}
          onClick={() => connect({ connector })}
        >
          {connector.name}
        </button>
      ))}
    </div>
  );
}
```

## Network Configuration

### Celo Networks

| Network | Chain ID | Reown Import | Wagmi Import |
|---------|----------|--------------|--------------|
| Mainnet | 42220 | `celo` from `@reown/appkit/networks` | `celo` from `wagmi/chains` |
| Celo Alfajores | 44787 | `celoAlfajores` from `@reown/appkit/networks` | `celoAlfajores` from `wagmi/chains` |
| Celo Sepolia | 11142220 | - | `celoSepolia` from `wagmi/chains` |

### Reown Project ID

Required for WalletConnect connections. WalletConnect Inc. rebranded to **Reown** in 2024.

1. Go to [cloud.reown.com](https://cloud.reown.com) (formerly WalletConnect Cloud)
2. Create a new project (select "AppKit" type)
3. Copy the project ID
4. Add to environment variables:

```bash
NEXT_PUBLIC_REOWN_PROJECT_ID=your_project_id
```

> **Note**: The wagmi `walletConnect` connector still uses the same project ID. Only the cloud console was rebranded.

## Best Practices

1. **Support Multiple Wallets** - Don't force users into one wallet
2. **Handle Network Switching** - Prompt users to switch to Celo
3. **Show Connection State** - Clear UI for connected/disconnected
4. **Handle Errors** - User-friendly error messages
5. **Test on Mobile** - Mobile browsers and wallet apps

## Dependencies

### Reown AppKit

```json
{
  "dependencies": {
    "@reown/appkit": "^1.0.0",
    "@reown/appkit-adapter-wagmi": "^1.0.0",
    "wagmi": "^2.0.0",
    "viem": "^2.0.0",
    "@tanstack/react-query": "^5.0.0"
  }
}
```

### Custom wagmi (without AppKit)

```json
{
  "dependencies": {
    "wagmi": "^2.0.0",
    "viem": "^2.0.0",
    "@tanstack/react-query": "^5.0.0"
  }
}
```

## Additional Resources

- [wallet-connectors.md](references/wallet-connectors.md) - Connector configuration reference
