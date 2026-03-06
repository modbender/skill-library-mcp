# Agent Wallet Implementation Plan

## Current State
- ✅ Agent wallet creation (CDP AgentKit)
- ✅ Wallet address generation
- ❌ Wallet export/storage
- ❌ Dashboard wallet management
- ❌ X402 payment implementation

## Safety Issue
**Problem**: Wallets are created but not exported/stored. If users send funds, they cannot be recovered.

**Solution**: Build complete wallet management in Dashboard before showing wallet to users.

---

## Implementation Phases

### Phase 1: Wallet Export & Storage (CRITICAL - Do First)
**Priority**: 🔴 High - Safety critical

**Backend Changes:**
1. Export wallet data after creation
```typescript
// In agent-wallet.ts
async exportWallet(): Promise<string> {
  if (!this.walletProvider) {
    throw new Error('Agent wallet not initialized');
  }

  // Export wallet data (includes seed/keys)
  const walletData = await this.walletProvider.exportWallet();
  return JSON.stringify(walletData);
}
```

2. Store encrypted wallet data in database
```typescript
// In bloom-identity-skill-v2.ts after wallet creation
const walletData = await this.agentWallet.exportWallet();

// Save to user's account (encrypted)
await saveUserWalletData({
  userId,
  walletData: encrypt(walletData), // Encrypt before storing
  network: agentWallet.network,
  address: agentWallet.address,
  createdAt: Date.now()
});
```

3. Database schema
```sql
-- Add to users table or create separate agent_wallets table
ALTER TABLE users ADD COLUMN agent_wallet_data TEXT; -- Encrypted JSON
ALTER TABLE users ADD COLUMN agent_wallet_address VARCHAR(42);
ALTER TABLE users ADD COLUMN agent_wallet_network VARCHAR(20);
```

**Security:**
- Encrypt wallet data with user-specific key (derived from JWT secret + userId)
- Never expose raw wallet data in API responses
- Only decrypt server-side when needed

---

### Phase 2: Dashboard - Agent Tab/Section
**Priority**: 🟡 Medium - Required before showing wallet to users

**Dashboard Location Options:**

#### Option A: Separate Agent Tab (Recommended)
```
Dashboard Tabs:
├── Overview
├── Identity Card
├── Skills
├── Agent Wallet  ← NEW
└── Settings
```

**Pros**:
- Clear separation of concerns
- Room to expand agent features
- Less cluttered

#### Option B: Section in Existing Tab
```
Dashboard > Identity Card
├── Your Personality
├── Recommended Skills
└── Agent Wallet  ← NEW SECTION
```

**Pros**:
- Everything about identity in one place
- Simpler navigation

**Recommendation**: Go with Option A (separate tab) for future scalability.

---

### Phase 3: Agent Wallet UI Components

**3.1 Wallet Overview Card**
```tsx
// components/AgentWallet/WalletOverview.tsx

<Card>
  <CardHeader>
    <h2>🤖 Your Agent Wallet</h2>
    <Badge>Base Network</Badge>
  </CardHeader>

  <CardContent>
    {/* Wallet Address */}
    <div className="space-y-4">
      <div>
        <Label>Wallet Address</Label>
        <CopyableAddress address={wallet.address} />
      </div>

      {/* Balance */}
      <div>
        <Label>Balance</Label>
        <BalanceDisplay balance={balance} />
      </div>

      {/* X402 Endpoint */}
      <div>
        <Label>X402 Payment Endpoint</Label>
        <CopyableAddress address={wallet.x402Endpoint} />
      </div>
    </div>
  </CardContent>
</Card>
```

**3.2 Wallet Actions**
```tsx
// components/AgentWallet/WalletActions.tsx

<div className="grid grid-cols-2 gap-4">
  {/* Receive */}
  <Button onClick={handleShowQR}>
    <QRCode className="mr-2" />
    Receive USDC
  </Button>

  {/* Send (X402) */}
  <Button onClick={handleSendModal}>
    <Send className="mr-2" />
    Send Tip
  </Button>

  {/* Export/Backup */}
  <Button variant="outline" onClick={handleExport}>
    <Download className="mr-2" />
    Export Wallet
  </Button>

  {/* View Transactions */}
  <Button variant="outline" onClick={handleViewTx}>
    <History className="mr-2" />
    Transactions
  </Button>
</div>
```

**3.3 Security & Backup Section**
```tsx
// components/AgentWallet/WalletSecurity.tsx

<Alert>
  <Shield className="h-4 w-4" />
  <AlertTitle>Backup Your Wallet</AlertTitle>
  <AlertDescription>
    Export your wallet data to recover access if needed.
    Store it securely - anyone with this data can access your funds.
  </AlertDescription>
  <Button onClick={handleExportWallet}>
    Export Now
  </Button>
</Alert>
```

**3.4 Transaction History**
```tsx
// components/AgentWallet/TransactionHistory.tsx

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Type</TableHead>
      <TableHead>To/From</TableHead>
      <TableHead>Amount</TableHead>
      <TableHead>Date</TableHead>
      <TableHead>Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {transactions.map(tx => (
      <TableRow key={tx.hash}>
        <TableCell>{tx.type}</TableCell>
        <TableCell>{truncate(tx.address)}</TableCell>
        <TableCell>{tx.amount} USDC</TableCell>
        <TableCell>{formatDate(tx.timestamp)}</TableCell>
        <TableCell>
          <Badge variant={tx.status}>{tx.status}</Badge>
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

---

### Phase 4: X402 Payment Implementation
**Priority**: 🟢 Low - Nice to have, build after wallet management

**4.1 Backend: Implement sendX402Payment**
```typescript
// In agent-wallet.ts - replace the placeholder
async sendX402Payment(to: string, amount: number): Promise<string> {
  if (!this.walletProvider) {
    throw new Error('Agent wallet not initialized');
  }

  console.log(`💸 Sending ${amount} USDC via X402 to ${to}...`);

  try {
    // Use CDP SDK to send transaction
    const tx = await this.walletProvider.sendTransaction({
      to: extractAddressFromX402(to),
      value: 0,
      data: encodeX402Payment(amount),
    });

    return tx.transactionHash;
  } catch (error) {
    console.error('❌ X402 payment failed:', error);
    throw new Error(`X402 payment failed: ${error.message}`);
  }
}
```

**4.2 Dashboard: Send Modal**
```tsx
// components/AgentWallet/SendModal.tsx

<Dialog>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Send USDC Tip</DialogTitle>
    </DialogHeader>

    <Form onSubmit={handleSend}>
      {/* Recipient */}
      <FormField>
        <Label>To (Creator Name or X402 Address)</Label>
        <Input
          placeholder="Alice or https://x402.bloomprotocol.ai/base/0x..."
          value={recipient}
          onChange={e => setRecipient(e.target.value)}
        />
      </FormField>

      {/* Amount */}
      <FormField>
        <Label>Amount (USDC)</Label>
        <Input
          type="number"
          placeholder="5.00"
          value={amount}
          onChange={e => setAmount(e.target.value)}
        />
      </FormField>

      {/* Preview */}
      <Alert>
        <AlertDescription>
          You're sending ${amount} USDC to {resolvedName}
          Network fee: $0 (sponsored)
        </AlertDescription>
      </Alert>

      <Button type="submit" disabled={!isValid}>
        Send Tip
      </Button>
    </Form>
  </DialogContent>
</Dialog>
```

---

## Phase 5: Update Skill Output

**Only after Phase 1-3 are complete**, update the skill output to show wallet with dashboard CTA:

```typescript
// In formatSuccessMessage()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 **Your Agent Wallet**

${agentWallet.address}
Network: ${networkDisplay}

🌐 **Manage your wallet in Dashboard**
   ${dashboardUrl.replace('/dashboard', '/dashboard/agent-wallet')}

   • View balance
   • Send tips to creators
   • Export backup

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Marketing & Onboarding Considerations

### Agent Tab Structure (Recommended)
```
Dashboard > Agent Wallet Tab

┌─────────────────────────────────────────┐
│ 🤖 Your Agent Wallet                    │
├─────────────────────────────────────────┤
│                                         │
│ [Wallet Overview Card]                  │
│   • Address                             │
│   • Balance                             │
│   • X402 Endpoint                       │
│                                         │
│ [Quick Actions]                         │
│   [Receive] [Send] [Export] [History]   │
│                                         │
│ [Security & Backup]                     │
│   ⚠️  Backup reminder if not done       │
│                                         │
│ [Recent Transactions]                   │
│   • Last 10 transactions                │
│                                         │
│ [Coming Soon]                           │
│   • Auto-tip based on identity match    │
│   • Recurring tips to favorite creators │
│   • X402 payment scheduling             │
│                                         │
└─────────────────────────────────────────┘
```

### Section Priority for User Onboarding
1. **Wallet Overview** - What you have
2. **Backup Security Alert** - Critical action needed
3. **Quick Actions** - What you can do
4. **Transactions** - What you've done
5. **Coming Soon** - Future value

### Privacy Considerations
- ✅ Wallet address is public (blockchain)
- ✅ Show it prominently
- ⚠️  Wallet data (seed/keys) is private
- ⚠️  Only show export after password confirmation
- ⚠️  Add warning: "Store securely, don't share"

---

## Timeline Estimate

**Phase 1** (Wallet Export & Storage): 2-3 days
- Backend: 1 day
- Database: 0.5 day
- Testing: 0.5 day
- Encryption setup: 1 day

**Phase 2** (Dashboard Structure): 1 day
- Add Agent tab/route
- Basic layout

**Phase 3** (Wallet UI): 3-4 days
- Overview card: 1 day
- Actions: 1 day
- Security/Export: 1 day
- Transaction history: 1 day

**Phase 4** (X402 Implementation): 2-3 days
- Backend send: 1 day
- Frontend modal: 1 day
- Testing: 1 day

**Total**: ~8-11 days for complete implementation

---

## Next Steps

1. **Immediate**: Remove wallet from skill output (safety)
2. **Week 1**: Implement Phase 1 (wallet export/storage)
3. **Week 2**: Build Phase 2-3 (dashboard UI)
4. **Week 3**: Implement Phase 4 (X402 payments)
5. **Week 4**: Test, polish, re-add to skill output

---

## Decision Point: Do We Build This Now?

### ✅ Build Now If:
- You're ready to commit to wallet management
- Dashboard exists and is maintained
- This is core to your agent identity value prop
- You have 2-3 weeks to complete it

### ⏸️ Defer If:
- Other features are higher priority
- Dashboard needs major work first
- Agent tipping is not core to MVP
- Timeline is too aggressive

**Recommendation**: Build it! Wallet management is table stakes for Web3 identity. Without it, showing a wallet address is misleading/dangerous.
