---
name: oneshot
description: |
  OneShot SDK for AI agent commercial transactions. Send emails, make calls, research, buy products, and more with automatic x402 payments.
  Use this skill when agents need to execute real-world actions: email, voice, SMS, research, commerce, or data enrichment.
  Supports Coinbase CDP Wallets (recommended, no private keys) or raw wallet key authentication.
metadata:
  author: oneshotagent
  version: "1.3.0"
  homepage: "https://oneshotagent.com"
---

# OneShot

Infrastructure for autonomous AI agents to execute real-world commercial transactions: email, payments, e-commerce, research, and data enrichment with native x402 payments.

## Quick Start

```bash
npm install @oneshot-agent/sdk
```

**With CDP Wallet (Recommended — no private keys):**

```typescript
import { OneShot } from '@oneshot-agent/sdk';

// Reads CDP_API_KEY_ID, CDP_API_KEY_SECRET, CDP_WALLET_SECRET from env
const agent = await OneShot.create({ cdp: true });

// Send an email
await agent.email({
  to: 'recipient@example.com',
  subject: 'Hello from my agent',
  body: 'This email was sent autonomously.'
});
```

**With Raw Private Key:**

```typescript
import { OneShot } from '@oneshot-agent/sdk';

const agent = new OneShot({
  privateKey: process.env.ONESHOT_WALLET_PRIVATE_KEY
});
```

## Authentication

OneShot uses x402 payments (USDC on Base). Two wallet options:

### Option A: Coinbase CDP Wallet (Recommended)

Server-side wallet managed by Coinbase — no private keys in your config. Signing happens in Coinbase's secure enclave (TEE).

```bash
export CDP_API_KEY_ID="your-api-key-id"
export CDP_API_KEY_SECRET="your-api-key-secret"
export CDP_WALLET_SECRET="your-wallet-secret"
```

```typescript
const agent = await OneShot.create({ cdp: true });
```

Get credentials at [Coinbase Developer Platform](https://portal.cdp.coinbase.com). The SDK auto-creates a wallet on first use. Optional: `npm install @coinbase/cdp-sdk`

### Option B: Raw Private Key (Advanced)

Direct wallet control for agents managing their own keys:

```bash
export ONESHOT_WALLET_PRIVATE_KEY="0xYourPrivateKey"
```

```typescript
const agent = new OneShot({ privateKey: process.env.ONESHOT_WALLET_PRIVATE_KEY });
```

### Custom Wallet Provider

Bring your own signing implementation:

```typescript
const agent = await OneShot.create({
  walletProvider: {
    address: '0x...',
    signTypedData: async (domain, types, value) => signature
  }
});
```

**Test Mode:** SDK runs in test mode by default (Base Sepolia testnet). Set `ONESHOT_TEST_MODE=false` for production.

## SDK Methods

### Email

```typescript
// Send email (~$0.01 per email, ~$10 first-time domain setup)
const result = await agent.email({
  to: 'recipient@example.com',
  subject: 'Subject line',
  body: 'Email body content',
  attachments: [{ filename: 'doc.pdf', content: base64String }]
});

// Bulk email
const result = await agent.email({
  to: ['user1@example.com', 'user2@example.com'],
  subject: 'Bulk message',
  body: 'Sent to multiple recipients'
});
```

### Inbox

```typescript
// List inbound emails (free)
const emails = await agent.inboxList();

// Get specific email
const email = await agent.inboxGet({ id: 'email_id' });
```

### SMS

```typescript
// Send SMS (~$0.035 per segment)
const result = await agent.sms({
  to: '+15551234567',
  body: 'Hello via SMS'
});

// List SMS inbox
const messages = await agent.smsInboxList();
```

### Voice Calls

```typescript
// Make a call (~$0.25/min)
const result = await agent.voice({
  to: '+15551234567',
  objective: 'Schedule a meeting for next Tuesday',
  context: 'Calling to follow up on our email exchange'
});
```

### Research

```typescript
// Deep research ($0.50-$2.00)
const result = await agent.research({
  query: 'What are the latest developments in agent commerce?',
  depth: 'deep' // 'quick' or 'deep'
});

// Returns report with citations
console.log(result.report);
console.log(result.sources);
```

### Data Enrichment

```typescript
// Find email (~$0.10)
const result = await agent.findEmail({
  name: 'John Doe',
  company: 'Acme Corp'
});

// Verify email deliverability (~$0.01)
const result = await agent.verifyEmail({
  email: 'john@acme.com'
});

// Enrich profile from LinkedIn (~$0.10)
const result = await agent.enrichProfile({
  linkedin_url: 'https://linkedin.com/in/johndoe'
});

// People search (~$0.10/result)
const results = await agent.peopleSearch({
  job_title: 'CTO',
  company: 'Acme Corp',
  location: 'San Francisco'
});
```

### Commerce

```typescript
// Search products (free)
const products = await agent.commerceSearch({
  query: 'wireless headphones',
  max_results: 10
});

// Buy product (product price + fee)
const result = await agent.commerceBuy({
  product_url: 'https://amazon.com/dp/B0...',
  shipping_address: {
    name: 'John Doe',
    street: '123 Main St',
    city: 'San Francisco',
    state: 'CA',
    zip: '94102',
    country: 'US'
  },
  max_price: 100.00
});
```

### Build Websites

```typescript
// Build a website (~$10+)
const result = await agent.build({
  type: 'landing_page',
  description: 'A SaaS landing page for an AI writing tool',
  domain: 'myproduct.com'
});

// Update existing site
const result = await agent.updateBuild({
  build_id: 'build_abc123',
  changes: 'Update the hero section headline to: Ship faster with AI'
});
```

### Utilities

```typescript
// Check balance (free)
const balance = await agent.getBalance();
console.log(`Balance: ${balance.usdc} USDC`);

// Universal tool call
const result = await agent.tool('email', {
  to: 'user@example.com',
  subject: 'Hello',
  body: 'Sent via universal tool method'
});
```

## MCP Server

Use OneShot tools in Claude Desktop, Cursor, OpenClaw, or Claude Code:

```bash
npm install -g @oneshot-agent/mcp-server
```

**With CDP Wallet (Recommended):**
```json
{
  "mcpServers": {
    "oneshot": {
      "command": "npx",
      "args": ["-y", "@oneshot-agent/mcp-server"],
      "env": {
        "CDP_API_KEY_ID": "your-api-key-id",
        "CDP_API_KEY_SECRET": "your-api-key-secret",
        "CDP_WALLET_SECRET": "your-wallet-secret"
      }
    }
  }
}
```

**With Raw Private Key:**
```json
{
  "mcpServers": {
    "oneshot": {
      "command": "npx",
      "args": ["-y", "@oneshot-agent/mcp-server"],
      "env": {
        "ONESHOT_WALLET_PRIVATE_KEY": "0xYourPrivateKey"
      }
    }
  }
}
```

## Pricing

| Tool | Cost |
|------|------|
| Email | ~$0.01/email (+$10 first domain) |
| SMS | ~$0.035/segment |
| Voice | ~$0.25/minute |
| Research (quick) | ~$0.50 |
| Research (deep) | ~$2.00 |
| Find Email | ~$0.10 |
| Verify Email | ~$0.01 |
| Enrich Profile | ~$0.10 |
| People Search | ~$0.10/result |
| Product Search | Free |
| Commerce Buy | Product price + fee |
| Build Website | ~$10+ |
| Inbox/Notifications | Free |

## Funding Your Agent

Add USDC to your agent's wallet on Base network:
1. Get wallet address: `console.log(agent.address)`
2. Send USDC (Base) to the address
3. Or use https://oneshotagent.com to fund

Test mode uses Base Sepolia testnet (free test USDC).

## Error Handling

```typescript
import { OneShot, ContentBlockedError, InsufficientBalanceError } from '@oneshot-agent/sdk';

try {
  const result = await agent.email({ to, subject, body });
} catch (error) {
  if (error instanceof InsufficientBalanceError) {
    console.log('Need to fund wallet');
  } else if (error instanceof ContentBlockedError) {
    console.log('Content policy violation');
  }
}
```

## Soul.Markets

Monetize your agent by listing on Soul.Markets:
- Upload your soul.md
- Define services and pricing
- Earn 80% of every transaction
- USDC settlements, instant payouts

Docs: https://docs.soul.mds.markets

## Resources

- [Documentation](https://docs.oneshotagent.com)
- [SDK Examples](https://docs.oneshotagent.com/sdk/examples)
- [Pricing](https://docs.oneshotagent.com/pricing)
- [GitHub](https://github.com/oneshot-agent/sdk)
- [Soul.Markets](https://soul.mds.markets)
