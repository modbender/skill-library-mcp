# Builder Quest UI Design - Agent Identity Dashboard

## Design Philosophy
**Goal**: Showcase agent identity feature cleanly for Builder Quest judges
**Principle**: Identity first, wallet second. Don't overwhelm with too many features.

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│ Bloom Protocol - Agent Identity Dashboard                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────┐  ┌──────────────────────────────────────────┐ │
│  │                │  │                                          │ │
│  │  Agent Info    │  │      Identity Card (Main)                │ │
│  │  (Left Sidebar)│  │                                          │ │
│  │                │  │  💜 The Visionary                        │ │
│  │  🤖 Agent      │  │  "See beyond the hype"                   │ │
│  │  Wallet        │  │                                          │ │
│  │                │  │  [Description]                           │ │
│  │  0x03Ce...9905 │  │                                          │ │
│  │  Balance: 0    │  │  Categories: Crypto • DeFi • Web3       │ │
│  │  Network: Base │  │                                          │ │
│  │                │  │  ─────────────────────────────────       │ │
│  │  [Manage]      │  │                                          │ │
│  │                │  │  🎯 Top Skills Matched for You           │ │
│  │                │  │                                          │ │
│  │                │  │  1. DeFi Protocol Analyzer (95%)         │ │
│  │                │  │  2. Smart Contract Auditor (90%)         │ │
│  │                │  │  3. Gas Optimizer (88%)                  │ │
│  │                │  │                                          │ │
│  │                │  │  [Tip Creator]  [View More]              │ │
│  │                │  │                                          │ │
│  └────────────────┘  └──────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### Left Sidebar: Agent Info (20% width)

**Purpose**: Quick reference, doesn't distract from main content

```tsx
// components/AgentInfo.tsx
<aside className="w-64 border-r bg-muted/30 p-6 space-y-6">
  {/* Agent Wallet Card */}
  <Card className="border-none bg-background">
    <CardHeader className="pb-3">
      <CardTitle className="text-sm font-medium text-muted-foreground">
        🤖 Agent Wallet
      </CardTitle>
    </CardHeader>
    <CardContent className="space-y-3">
      {/* Address */}
      <div>
        <div className="text-xs text-muted-foreground mb-1">Address</div>
        <code className="text-xs">
          {address.slice(0, 6)}...{address.slice(-4)}
        </code>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 ml-1"
          onClick={() => copy(address)}
        >
          <Copy className="h-3 w-3" />
        </Button>
      </div>

      {/* Balance */}
      <div>
        <div className="text-xs text-muted-foreground mb-1">Balance</div>
        <div className="text-sm font-medium">{balance} USDC</div>
      </div>

      {/* Network */}
      <div>
        <div className="text-xs text-muted-foreground mb-1">Network</div>
        <Badge variant="secondary" className="text-xs">
          Base
        </Badge>
      </div>

      {/* Manage Button */}
      <Button
        variant="outline"
        size="sm"
        className="w-full"
        onClick={() => setShowWalletModal(true)}
      >
        Manage Wallet
      </Button>
    </CardContent>
  </Card>

  {/* Stats Card (Optional) */}
  <Card className="border-none bg-background">
    <CardHeader className="pb-3">
      <CardTitle className="text-sm font-medium text-muted-foreground">
        📊 Stats
      </CardTitle>
    </CardHeader>
    <CardContent className="space-y-2 text-sm">
      <div className="flex justify-between">
        <span className="text-muted-foreground">Tips Sent</span>
        <span className="font-medium">3</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Total Tipped</span>
        <span className="font-medium">$15</span>
      </div>
    </CardContent>
  </Card>
</aside>
```

---

### Main Content: Identity Card (80% width)

**Purpose**: Hero section, this is what Builder Quest judges see first

```tsx
// app/dashboard/page.tsx
<main className="flex-1 p-8">
  {/* Hero: Identity Card */}
  <Card className="mb-8">
    <CardHeader>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <CardTitle className="text-3xl flex items-center gap-3">
            💜 The Visionary
            <Badge variant="secondary" className="text-xs font-normal">
              85% confidence
            </Badge>
          </CardTitle>
          <p className="text-lg text-muted-foreground italic">
            "See beyond the hype"
          </p>
        </div>
        <Button variant="outline" size="sm">
          <Share className="h-4 w-4 mr-2" />
          Share
        </Button>
      </div>
    </CardHeader>
    <CardContent className="space-y-6">
      {/* Description */}
      <p className="text-base">
        You are a forward-thinking builder who sees beyond the hype
        and focuses on real-world impact.
      </p>

      {/* Categories */}
      <div className="flex flex-wrap gap-2">
        <Badge variant="outline">Crypto</Badge>
        <Badge variant="outline">DeFi</Badge>
        <Badge variant="outline">Web3</Badge>
      </div>

      {/* Interests */}
      <div>
        <div className="text-sm text-muted-foreground mb-2">
          Interests
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="secondary">Smart Contracts</Badge>
          <Badge variant="secondary">Layer 2</Badge>
          <Badge variant="secondary">Cross-chain</Badge>
        </div>
      </div>
    </CardContent>
  </Card>

  {/* Recommended Skills */}
  <Card>
    <CardHeader>
      <CardTitle>🎯 Top Skills Matched for You</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="space-y-4">
        {skills.map((skill, i) => (
          <SkillCard key={skill.id} skill={skill} rank={i + 1} />
        ))}
      </div>
    </CardContent>
  </Card>
</main>
```

---

### Skill Card Component

```tsx
// components/SkillCard.tsx
<Card className="hover:border-primary transition-colors">
  <CardContent className="p-4">
    <div className="flex items-start justify-between gap-4">
      {/* Left: Skill Info */}
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-2xl font-bold text-muted-foreground">
            {rank}
          </span>
          <div>
            <h3 className="font-semibold">{skill.name}</h3>
            {skill.creator && (
              <p className="text-sm text-muted-foreground">
                by {skill.creator}
              </p>
            )}
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          {skill.description}
        </p>
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{skill.matchScore}% match</Badge>
          {skill.categories.map(cat => (
            <Badge key={cat} variant="outline" className="text-xs">
              {cat}
            </Badge>
          ))}
        </div>
      </div>

      {/* Right: Action */}
      <Button
        size="sm"
        variant="outline"
        onClick={() => handleTip(skill)}
      >
        💰 Tip
      </Button>
    </div>
  </CardContent>
</Card>
```

---

## Modal: Wallet Management (When Clicked "Manage")

**Purpose**: Keep advanced features hidden until user wants them

```tsx
// components/WalletManagementModal.tsx
<Dialog open={showWalletModal} onOpenChange={setShowWalletModal}>
  <DialogContent className="max-w-2xl">
    <DialogHeader>
      <DialogTitle>🤖 Manage Agent Wallet</DialogTitle>
      <DialogDescription>
        Your agent wallet is managed by Coinbase CDP
      </DialogDescription>
    </DialogHeader>

    <Tabs defaultValue="overview">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="transactions">Transactions</TabsTrigger>
        <TabsTrigger value="settings">Settings</TabsTrigger>
      </TabsList>

      {/* Tab: Overview */}
      <TabsContent value="overview" className="space-y-4">
        {/* Wallet Address */}
        <div>
          <Label>Wallet Address</Label>
          <div className="flex items-center gap-2 mt-1">
            <Input value={address} readOnly />
            <Button
              variant="outline"
              size="icon"
              onClick={() => copy(address)}
            >
              <Copy className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Balance */}
        <div className="grid grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Balance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{balance} USDC</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Network</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge>Base Mainnet</Badge>
            </CardContent>
          </Card>
        </div>

        {/* Actions */}
        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline">
            <QrCode className="h-4 w-4 mr-2" />
            Show QR Code
          </Button>
          <Button variant="outline">
            <ExternalLink className="h-4 w-4 mr-2" />
            View on BaseScan
          </Button>
        </div>

        {/* CDP Info */}
        <Alert>
          <Shield className="h-4 w-4" />
          <AlertTitle>Managed by Coinbase CDP</AlertTitle>
          <AlertDescription>
            Your wallet is secured with Coinbase's MPC technology.
            Private keys are managed securely and never exposed.
          </AlertDescription>
        </Alert>
      </TabsContent>

      {/* Tab: Transactions */}
      <TabsContent value="transactions">
        <TransactionHistory address={address} />
      </TabsContent>

      {/* Tab: Settings */}
      <TabsContent value="settings" className="space-y-4">
        {/* Export Wallet Data */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Export Wallet</CardTitle>
            <CardDescription>
              Export your wallet data for backup or recovery
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" onClick={handleExport}>
              <Download className="h-4 w-4 mr-2" />
              Export Wallet Data
            </Button>
          </CardContent>
        </Card>

        {/* Network Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Network</CardTitle>
          </CardHeader>
          <CardContent>
            <Select defaultValue="base">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="base">Base Mainnet</SelectItem>
                <SelectItem value="base-sepolia">Base Sepolia</SelectItem>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  </DialogContent>
</Dialog>
```

---

## Responsive Considerations

### Desktop (>1024px)
- Left sidebar visible
- 20/80 split
- Identity card and skills in main area

### Tablet (768px - 1024px)
- Collapse sidebar to icon-only
- Show wallet info in top bar
- Full width for main content

### Mobile (<768px)
- Hide sidebar completely
- Add wallet button to top nav
- Stack cards vertically

```tsx
// Responsive Layout
<div className="flex min-h-screen">
  {/* Sidebar - Hidden on mobile */}
  <aside className="hidden lg:block w-64">
    <AgentInfo />
  </aside>

  {/* Mobile: Top bar with wallet */}
  <div className="lg:hidden border-b p-4">
    <Button variant="outline" onClick={() => setShowWalletModal(true)}>
      🤖 {address.slice(0, 6)}...{address.slice(-4)}
    </Button>
  </div>

  {/* Main content */}
  <main className="flex-1">
    {/* ... */}
  </main>
</div>
```

---

## Feature Priorities for Builder Quest

### ✅ Must Have (For Demo)
1. **Identity Card Display** - The star of the show
2. **Recommended Skills** - Shows the AI matching
3. **Agent Wallet Info** (sidebar) - Shows CDP integration
4. **Clean, professional UI** - Impresses judges

### 🟡 Nice to Have (If Time)
1. **Tip Modal** - Shows X402 concept (even if placeholder)
2. **Transaction History** - Shows it's functional
3. **Share Button** - Shows social aspect

### ⚪ Can Skip (For Now)
1. Wallet export/recovery
2. Advanced settings
3. Multiple network support
4. Detailed analytics

---

## Builder Quest Judging Criteria Alignment

### Innovation
- ✅ AI-powered identity matching
- ✅ CDP wallet integration
- ✅ X402 payment protocol

### Technical Implementation
- ✅ Clean architecture (identity + wallet separated)
- ✅ CDP AgentKit usage
- ✅ Next.js best practices

### User Experience
- ✅ Simple, clean UI
- ✅ Progressive disclosure (advanced features in modal)
- ✅ Mobile responsive

### Potential Impact
- ✅ Helps users discover relevant skills
- ✅ Enables creator monetization
- ✅ Agent-to-agent economy

---

## Implementation Timeline for Builder Quest

### Day 1-2: Core UI
- [ ] Dashboard layout (sidebar + main)
- [ ] Identity card display
- [ ] Skills list with match scores

### Day 3-4: Wallet Integration
- [ ] CDP wallet info in sidebar
- [ ] Wallet management modal
- [ ] Transaction history (read-only)

### Day 5: Polish
- [ ] Responsive design
- [ ] Loading states
- [ ] Error handling
- [ ] Demo data if needed

### Day 6: Test & Deploy
- [ ] E2E testing
- [ ] Deploy to production
- [ ] Prepare demo script

---

## Color Scheme Recommendations

```css
/* Personality Type Colors */
--visionary: #8B5CF6;    /* Purple */
--explorer: #10B981;     /* Green */
--cultivator: #06B6D4;   /* Cyan */
--optimizer: #F59E0B;    /* Orange */
--innovator: #3B82F6;    /* Blue */

/* UI Colors */
--background: #FFFFFF;
--foreground: #0A0A0A;
--muted: #F4F4F5;
--muted-foreground: #71717A;
--border: #E4E4E7;
--primary: #18181B;
--accent: #8B5CF6;  /* Match personality color */
```

---

## Demo Script for Builder Quest

### Introduction (30 seconds)
"Hi, I'm showing Bloom Identity - an AI agent that analyzes your on-chain activity and generates a personalized identity card with matched skill recommendations."

### Walkthrough (2 minutes)
1. **Show Skill Generation**
   - Run the skill: "Generate my bloom identity"
   - Show AI analysis process
   - Display generated identity card

2. **Dashboard Tour**
   - Point out personality type and description
   - Show matched skills with scores
   - Highlight agent wallet (CDP integration)

3. **X402 Integration**
   - Click "Tip Creator" button
   - Show X402 payment modal
   - Explain agent-to-agent economy vision

### Technical Highlights (30 seconds)
- "Built with Coinbase CDP AgentKit for wallet management"
- "Using Base for gasless transactions"
- "X402 protocol for agent-to-agent payments"

---

## Conclusion

**Recommended Approach for Builder Quest:**

1. **Keep UI Simple**: Left sidebar for wallet info, main area for identity
2. **Progressive Disclosure**: Hide complex features in modals
3. **Focus on Story**: Identity matching is the hero, wallet is supporting cast
4. **Builder Quest Ready**: Can implement in 5-6 days, clean and impressive

**Key Decision**: Sidebar wallet info is perfect because it:
- ✅ Shows CDP integration without overwhelming
- ✅ Keeps focus on identity card
- ✅ Easy to access when needed
- ✅ Professional, clean layout
