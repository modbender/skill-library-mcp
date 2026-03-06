# Wallet Strategy: User-Controlled vs Agent-Managed

## TL;DR
**Recommendation**: Let users connect their own wallets (MetaMask, Coinbase Wallet). No custody, no key management, simpler and safer.

---

## Current Problem
- Creating wallets with CDP AgentKit
- Need to export/store keys (custody risk)
- Need to build wallet management UI
- Regulatory/security burden

## Better Approach: User Connects Own Wallet

### Architecture
```
┌─────────────────────────────────────────┐
│ Bloom Identity Skill                    │
│  ↓ Generates identity                   │
│  ↓ Returns dashboard link               │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Dashboard (Frontend)                    │
│                                         │
│  [Connect Wallet Button]                │
│     ↓                                   │
│  User connects MetaMask/Coinbase Wallet │
│     ↓                                   │
│  Save wallet address to backend         │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ User's Wallet (Self-Custody)            │
│  • User controls private keys           │
│  • User manages funds                   │
│  • User initiates transactions          │
└─────────────────────────────────────────┘
```

---

## Implementation

### 1. Frontend: Add Wallet Connect

**Install dependencies:**
```bash
npm install wagmi viem @tanstack/react-query
npm install @rainbow-me/rainbowkit
```

**Setup wagmi config:**
```typescript
// lib/wagmi.ts
import { createConfig, http } from 'wagmi';
import { base, baseSepolia } from 'wagmi/chains';
import { coinbaseWallet, metaMask, walletConnect } from 'wagmi/connectors';

export const config = createConfig({
  chains: [base, baseSepolia],
  connectors: [
    metaMask(),
    coinbaseWallet({ appName: 'Bloom Protocol' }),
    walletConnect({ projectId: process.env.NEXT_PUBLIC_WC_PROJECT_ID! }),
  ],
  transports: {
    [base.id]: http(),
    [baseSepolia.id]: http(),
  },
});
```

**Wrap app with providers:**
```typescript
// app/layout.tsx
import { WagmiProvider } from 'wagmi';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RainbowKitProvider } from '@rainbow-me/rainbowkit';
import { config } from '@/lib/wagmi';

const queryClient = new QueryClient();

export default function RootLayout({ children }) {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          {children}
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}
```

### 2. Dashboard: Wallet Section

```tsx
// app/dashboard/page.tsx
'use client';

import { useAccount, useDisconnect } from 'wagmi';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useEffect } from 'react';

export default function DashboardPage() {
  const { address, isConnected } = useAccount();
  const { disconnect } = useDisconnect();

  // Save wallet address to backend when connected
  useEffect(() => {
    if (isConnected && address) {
      saveWalletAddress(address);
    }
  }, [isConnected, address]);

  return (
    <div className="space-y-6">
      {/* Identity Card Section */}
      <Card>
        <CardHeader>
          <h2>Your Bloom Identity</h2>
        </CardHeader>
        <CardContent>
          {/* ... identity display ... */}
        </CardContent>
      </Card>

      {/* Wallet Section */}
      <Card>
        <CardHeader>
          <h2>🤖 Your Wallet</h2>
        </CardHeader>
        <CardContent>
          {!isConnected ? (
            <div className="text-center space-y-4">
              <p className="text-muted-foreground">
                Connect your wallet to tip skill creators
              </p>
              <ConnectButton />
            </div>
          ) : (
            <div className="space-y-4">
              {/* Wallet Info */}
              <div>
                <Label>Connected Wallet</Label>
                <div className="flex items-center gap-2">
                  <code className="text-sm">{address}</code>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigator.clipboard.writeText(address!)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Balance */}
              <WalletBalance address={address} />

              {/* Actions */}
              <div className="flex gap-2">
                <Button onClick={() => handleSendTip()}>
                  Send Tip
                </Button>
                <Button variant="outline" onClick={() => disconnect()}>
                  Disconnect
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Skills Section */}
      <RecommendedSkills />
    </div>
  );
}

async function saveWalletAddress(address: string) {
  await fetch('/api/user/wallet', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ walletAddress: address }),
  });
}
```

### 3. Backend: Save Wallet Address

```typescript
// app/api/user/wallet/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';

export async function POST(req: NextRequest) {
  const session = await getServerSession();
  if (!session?.user?.id) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { walletAddress } = await req.json();

  // Validate address
  if (!walletAddress.match(/^0x[a-fA-F0-9]{40}$/)) {
    return NextResponse.json({ error: 'Invalid address' }, { status: 400 });
  }

  // Save to database
  await db.user.update({
    where: { id: session.user.id },
    data: {
      walletAddress,
      walletConnectedAt: new Date(),
    },
  });

  return NextResponse.json({ success: true });
}
```

### 4. Database Schema

```sql
-- Add to users table
ALTER TABLE users ADD COLUMN wallet_address VARCHAR(42);
ALTER TABLE users ADD COLUMN wallet_connected_at TIMESTAMP;
ALTER TABLE users ADD COLUMN wallet_provider VARCHAR(50); -- 'metamask', 'coinbase-wallet', etc.

-- Index for lookups
CREATE INDEX idx_users_wallet_address ON users(wallet_address);
```

### 5. Send Tip Feature

```tsx
// components/SendTipModal.tsx
'use client';

import { useSendTransaction } from 'wagmi';
import { parseUnits } from 'viem';

export function SendTipModal({ creatorAddress, onClose }) {
  const [amount, setAmount] = useState('');
  const { sendTransaction, isPending } = useSendTransaction();

  const handleSend = async () => {
    // Send USDC on Base
    const USDC_BASE = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';

    await sendTransaction({
      to: USDC_BASE,
      data: encodeTransferCall(creatorAddress, parseUnits(amount, 6)),
    });
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Send Tip</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label>Amount (USDC)</Label>
            <Input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="5.00"
            />
          </div>
          <Button onClick={handleSend} disabled={isPending}>
            {isPending ? 'Sending...' : 'Send Tip'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

---

## Comparison: User Wallet vs Agent Wallet

| Feature | User Wallet (Recommended) | Agent Wallet (CDP) |
|---------|---------------------------|-------------------|
| **Custody** | User controls keys | We manage keys (or CDP) |
| **Security Risk** | None for us | High - need encryption, backup |
| **Implementation** | 2-3 days | 2-3 weeks |
| **User Trust** | High - users control funds | Lower - users trust us |
| **Regulatory** | None | Potentially subject to regulation |
| **Recovery** | User's responsibility | Our responsibility |
| **UX** | Familiar for Web3 users | Better for non-Web3 users |
| **Automation** | Manual user actions | Can automate |

---

## Use Cases

### ✅ Use User Wallet For:
- Manual tipping
- User-initiated transactions
- Displaying wallet balance
- Connecting to other dapps

### ✅ Use Agent Wallet For:
- Automated micro-tipping based on identity match
- Scheduled recurring tips
- Bot-initiated actions
- When user doesn't have a wallet

### 💡 Hybrid Approach:
```typescript
{
  userId: 123,

  // User's own wallet (primary)
  userWallet: "0xUser123...",
  walletProvider: "metamask",

  // Optional: Agent wallet for automation (if needed later)
  agentWallet: "0xAgent456...",
  agentWalletManaged: "cdp"
}
```

---

## Recommended Next Steps

### Phase 1: User Wallet Only (RECOMMENDED - Start Here)
1. Add wallet connect button to dashboard
2. Save wallet address when connected
3. Show balance and transaction history
4. Allow manual tips to creators

**Timeline**: 2-3 days
**Risk**: Low
**Value**: High - users can immediately tip creators

### Phase 2: Agent Wallet for Automation (Optional - Later)
1. Create CDP managed wallet for automation
2. Fund it with small amount
3. Auto-tip based on identity match
4. User can top up agent wallet from their own wallet

**Timeline**: 1-2 weeks
**Risk**: Medium
**Value**: Nice to have - automation

---

## Decision Matrix

**Choose User Wallet If:**
- ✅ You want to launch quickly (2-3 days)
- ✅ You don't want custody responsibility
- ✅ Manual tipping is acceptable
- ✅ Your users are Web3-native

**Choose Agent Wallet If:**
- ✅ You need full automation
- ✅ You're willing to handle custody
- ✅ You have 2-3 weeks to build properly
- ✅ Your users are not Web3-native

**Recommendation**: Start with User Wallet, add Agent Wallet later if needed.

---

## Update Skill Output

Once User Wallet is implemented, update the skill output:

```typescript
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 **View Full Dashboard**
   ${dashboardUrl}

   • Connect your wallet
   • Tip skill creators
   • Track your identity

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

No mention of "agent wallet" - just a call to action to connect their own wallet in the dashboard.
