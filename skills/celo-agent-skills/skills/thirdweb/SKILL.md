---
name: thirdweb
description: Use thirdweb SDK for Celo development. Includes wallet connection, contract deployment, and pre-built UI components.
license: Apache-2.0
metadata:
  author: celo-org
  version: "1.0.0"
---

# Thirdweb for Celo

Thirdweb is a full-stack Web3 development platform with SDK support for Celo.

Source: https://docs.celo.org/tooling/libraries-sdks/thirdweb-sdk/index.md

## When to Use

- Building dApps with pre-built UI components
- Deploying contracts without writing deployment scripts
- Integrating 500+ wallet options
- Building cross-chain applications

## Installation

```bash
npm install thirdweb
```

Or create a new project:

```bash
npx thirdweb create app
```

## Client Setup

### Get Client ID

1. Go to https://thirdweb.com/team
2. Create a project with localhost in allowed domains
3. Copy the client ID

### Initialize Client

```typescript
import { createThirdwebClient } from "thirdweb";

export const client = createThirdwebClient({
  clientId: process.env.NEXT_PUBLIC_THIRDWEB_CLIENT_ID!,
});
```

For server-side usage:

```typescript
const client = createThirdwebClient({
  secretKey: process.env.THIRDWEB_SECRET_KEY!,
});
```

Source: https://portal.thirdweb.com/typescript/v5/getting-started

## Chain Configuration

### Using Predefined Chains

```typescript
import { celo } from "thirdweb/chains";

// Use directly
const chain = celo;
```

### Custom Chain Definition

```typescript
import { defineChain } from "thirdweb";

const celoChain = defineChain(42220);

// Or with custom RPC
const celoCustom = defineChain({
  id: 42220,
  rpc: "https://forno.celo.org",
});
```

Source: https://portal.thirdweb.com/typescript/v5/chain

## React Provider Setup

```tsx
import { ThirdwebProvider } from "thirdweb/react";

function App({ children }: { children: React.ReactNode }) {
  return (
    <ThirdwebProvider>
      {children}
    </ThirdwebProvider>
  );
}
```

## Wallet Connection

### ConnectButton Component

```tsx
import { ConnectButton } from "thirdweb/react";
import { celo } from "thirdweb/chains";
import { client } from "./client";

function WalletConnect() {
  return (
    <ConnectButton
      client={client}
      chain={celo}
    />
  );
}
```

### With Specific Wallets

```tsx
import { ConnectButton } from "thirdweb/react";
import { createWallet } from "thirdweb/wallets";

const wallets = [
  createWallet("io.metamask"),
  createWallet("com.coinbase.wallet"),
  createWallet("app.valora"),
];

function WalletConnect() {
  return (
    <ConnectButton
      client={client}
      wallets={wallets}
    />
  );
}
```

## Contract Interaction

### Get Contract Reference

```typescript
import { getContract } from "thirdweb";
import { celo } from "thirdweb/chains";

const contract = getContract({
  client,
  chain: celo,
  address: "0x...",
});
```

### Read Contract Data

```tsx
import { useReadContract } from "thirdweb/react";
import { balanceOf } from "thirdweb/extensions/erc20";

function TokenBalance({ address }: { address: string }) {
  const { data, isLoading } = useReadContract(
    balanceOf,
    {
      contract,
      address,
    }
  );

  if (isLoading) return <div>Loading...</div>;
  return <div>Balance: {data?.toString()}</div>;
}
```

### Write to Contract

```tsx
import { useSendTransaction } from "thirdweb/react";
import { transfer } from "thirdweb/extensions/erc20";

function TransferTokens() {
  const { mutate: sendTransaction, isPending } = useSendTransaction();

  async function handleTransfer() {
    const transaction = transfer({
      contract,
      to: "0x...",
      amount: "10",
    });

    sendTransaction(transaction);
  }

  return (
    <button onClick={handleTransfer} disabled={isPending}>
      Transfer
    </button>
  );
}
```

## Account Hooks

### Get Active Account

```tsx
import { useActiveAccount } from "thirdweb/react";

function Account() {
  const account = useActiveAccount();

  if (!account) return <div>Not connected</div>;
  return <div>Connected: {account.address}</div>;
}
```

### Get Wallet Balance

```tsx
import { useWalletBalance } from "thirdweb/react";
import { celo } from "thirdweb/chains";

function Balance() {
  const account = useActiveAccount();
  const { data, isLoading } = useWalletBalance({
    client,
    chain: celo,
    address: account?.address,
  });

  if (isLoading) return <div>Loading...</div>;
  return <div>{data?.displayValue} {data?.symbol}</div>;
}
```

## Server-Side Usage

```typescript
import { createThirdwebClient } from "thirdweb";
import { getContract } from "thirdweb";
import { celo } from "thirdweb/chains";
import { getNFTs } from "thirdweb/extensions/erc1155";

const client = createThirdwebClient({
  secretKey: process.env.THIRDWEB_SECRET_KEY!,
});

const contract = getContract({
  client,
  chain: celo,
  address: "0x...",
});

const nfts = await getNFTs({ contract });
```

## Pre-built Extensions

Thirdweb provides type-safe extensions for common contracts:

| Extension | Import Path |
|-----------|-------------|
| ERC20 | `thirdweb/extensions/erc20` |
| ERC721 | `thirdweb/extensions/erc721` |
| ERC1155 | `thirdweb/extensions/erc1155` |

## Deployment

Deploy to decentralized storage:

```bash
npx thirdweb deploy --app
```

## Environment Variables

```bash
# .env
NEXT_PUBLIC_THIRDWEB_CLIENT_ID=your_client_id
THIRDWEB_SECRET_KEY=your_secret_key  # Server-side only
```

## Dependencies

```json
{
  "dependencies": {
    "thirdweb": "^5.0.0"
  }
}
```

## Additional Resources

- [extensions.md](references/extensions.md) - Available contract extensions
