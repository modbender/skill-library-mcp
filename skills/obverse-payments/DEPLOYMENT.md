# Obverse on OpenClaw - Complete Deployment Guide

This guide walks you through deploying Obverse as a payment skill on OpenClaw, from local testing to production distribution.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Testing the Integration](#testing-the-integration)
5. [Production Deployment](#production-deployment)
6. [Publishing to ClawHub](#publishing-to-clawhub)
7. [Monetization Strategy](#monetization-strategy)
8. [Maintenance & Updates](#maintenance--updates)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        OpenClaw Ecosystem                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐      ┌──────────────┐      ┌──────────────┐   │
│  │  Telegram   │      │  WhatsApp    │      │   Discord    │   │
│  │    Bot      │      │     Bot      │      │     Bot      │   │
│  └──────┬──────┘      └──────┬───────┘      └──────┬───────┘   │
│         │                    │                     │            │
│         └────────────────────┼─────────────────────┘            │
│                              │                                  │
│                    ┌─────────▼──────────┐                       │
│                    │  OpenClaw Agent    │                       │
│                    │  with Obverse      │                       │
│                    │  Skill Loaded      │                       │
│                    └─────────┬──────────┘                       │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               │ HTTPS + API Key
                               │
                    ┌──────────▼───────────┐
                    │   Obverse Backend    │
                    │  (Your NestJS API)   │
                    │                      │
                    │  • Payment Links     │
                    │  • QR Codes          │
                    │  • Balance Checks    │
                    │  • Invoices          │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Blockchain Layer    │
                    │                      │
                    │  Base ◄──► Solana   │
                    │  USDC      USDC/SOL │
                    └──────────────────────┘
```

## Prerequisites

### 1. Obverse Backend Running
Your NestJS API must be deployed and accessible:

```bash
# Production URL
https://obverse.onrender.com

# Required endpoints:
POST   /payment-links         # Create payment link
GET    /payment-links/:id     # Get payment link details
GET    /payments/link/:linkCode # List payments
POST   /payments              # Submit payment
GET    /wallet/:userId/balance # Check balance
```

### 2. OpenClaw Installed

Install OpenClaw on your system:

```bash
# macOS
brew install openclaw

# Linux (Ubuntu/Debian)
curl -fsSL https://openclaw.ai/install.sh | bash

# Or download from GitHub
# https://github.com/openclaw/openclaw/releases
```

Verify installation:
```bash
openclaw --version
# Should show: openclaw version X.X.X
```

### 3. API Keys Generated

Create API keys in your Obverse system:

```typescript
// In your backend, add API key generation endpoint
// src/auth/api-keys.controller.ts

@Post('generate-key')
async generateApiKey(@User() user) {
  const apiKey = `obv_sk_${randomBytes(32).toString('hex')}`;

  await this.apiKeyRepository.create({
    userId: user.id,
    key: hashSync(apiKey, 10),
    createdAt: new Date(),
    isActive: true
  });

  return { apiKey }; // Only shown once!
}
```

---

## Local Development Setup

### Step 1: Copy Skill to OpenClaw Directory

```bash
# Create skills directory
mkdir -p ~/.openclaw/skills

# Copy your skill
cp -r ./openclaw-skill ~/.openclaw/skills/obverse

# Verify files are copied
ls ~/.openclaw/skills/obverse
# Should show: SKILL.md, package.json, README.md, obverse-cli.js
```

### Step 2: Configure OpenClaw

Create or edit `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "obverse-payments": {
        "enabled": true,
        "env": {
          "OBVERSE_API_KEY": "obv_sk_your_test_key_here",
          "OBVERSE_API_URL": "http://localhost:4000"
        }
      }
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_TELEGRAM_BOT_TOKEN"
    }
  }
}
```

### Step 3: Start OpenClaw Gateway

```bash
# Start the gateway
openclaw gateway start

# Check status
openclaw gateway status

# View logs
openclaw gateway logs
```

### Step 4: Test the CLI Tool

Before testing via chat platforms, verify the CLI works:

```bash
# Make the CLI executable
chmod +x ~/.openclaw/skills/obverse/obverse-cli.js

# Set environment variables
export OBVERSE_API_KEY="obv_sk_your_test_key"
export OBVERSE_API_URL="http://localhost:4000"

# Test create payment link
node ~/.openclaw/skills/obverse/obverse-cli.js create-link 50 USDC base "Test payment"

# Expected output:
{
  "paymentUrl": "https://pay.obverse.app/xyz123",
  "paymentId": "pay_abc123",
  "linkCode": "xyz123",
  "amount": "50",
  "currency": "USDC",
  "chain": "base"
}
```

---

## Testing the Integration

### Test 1: Basic Payment Link via Telegram

1. Open Telegram and message your bot
2. Send: "Create payment link for 25 USDC"
3. Agent should respond with:
   ```
   ✅ Payment link created!

   Amount: 25 USDC
   Chain: Base
   Link: https://pay.obverse.app/xyz123

   Share this with your customer.
   Payment ID: xyz123 (use this to check status)
   ```

### Test 2: Payment Status Check

1. Message: "Check payment xyz123"
2. Agent should respond with current status

### Test 3: Balance Query

1. Message: "What's my balance?"
2. Agent should call balance endpoint and show:
   ```
   💰 Your Balances:

   Base (8453):
   - USDC: 100.50
   - USDT: 50.00

   Solana (mainnet):
   - SOL: 1.25
   - USDC: 200.00
   ```

### Test 4: Error Handling

Test what happens with invalid inputs:

```bash
# Invalid amount
"Create payment for -50 USDC"
# Should reject and ask for positive amount

# Invalid chain
"Create payment for 100 USDC on ethereum"
# Should suggest supported chains (Base, Solana)

# Expired/invalid payment ID
"Check payment invalid_id_123"
# Should return 404 error gracefully
```

### Test 5: End-to-End Payment Flow

1. Agent creates payment link: `https://pay.obverse.app/xyz123`
2. Customer opens link in browser
3. Customer connects wallet (MetaMask/Phantom)
4. Customer sends payment on-chain
5. Your backend receives transaction
6. Agent gets notified (via webhook or polling)
7. Agent confirms to merchant: "✅ Payment received! 50 USDC"

---

## Production Deployment

### Step 1: Deploy Obverse Backend to Production

```bash
# Using Render (current setup)
git push render main

# Or using Railway
railway up

# Or using fly.io
fly deploy

# Verify deployment
curl https://obverse.onrender.com/health
# Should return: {"status": "ok"}
```

### Step 2: Update API URLs

Edit production config:

```json
{
  "skills": {
    "entries": {
      "obverse-payments": {
        "enabled": true,
        "env": {
          "OBVERSE_API_KEY": "obv_sk_production_key_here",
          "OBVERSE_API_URL": "https://obverse.onrender.com"
        }
      }
    }
  }
}
```

### Step 3: Enable Monitoring

Add monitoring to your backend:

```typescript
// src/main.ts
import { Logger } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Log all API calls
  app.use((req, res, next) => {
    Logger.log(`${req.method} ${req.url}`, 'HTTP');
    next();
  });

  // Health check endpoint
  app.get('/health', (req, res) => {
    res.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    });
  });

  await app.listen(4000);
}
```

### Step 4: Set Up Analytics

Track skill usage:

```typescript
// Track when skill is used
@Post('payment-links')
async createPaymentLink(@Body() dto: CreatePaymentLinkDto, @Headers('x-openclaw-agent') agentId: string) {
  // Your existing logic...

  // Track analytics
  await this.analyticsService.track({
    event: 'payment_link_created',
    source: 'openclaw',
    agentId,
    amount: dto.amount,
    currency: dto.currency,
    chain: dto.chain,
    timestamp: new Date()
  });

  return paymentLink;
}
```

---

## Publishing to ClawHub

### Step 1: Prepare for Distribution

Create a GitHub repository:

```bash
cd openclaw-skill

# Initialize git
git init
git add .
git commit -m "Initial commit: Obverse OpenClaw skill v1.0"

# Create repo on GitHub
# Then push
git remote add origin https://github.com/YOUR_USERNAME/obverse-openclaw-skill.git
git push -u origin main
```

### Step 2: Create ClawHub Manifest

Add `clawhub.json`:

```json
{
  "name": "obverse-payments",
  "displayName": "Obverse Payments",
  "version": "1.0.0",
  "description": "Accept stablecoin payments (USDC/USDT) via AI agents on Base and Solana",
  "author": {
    "name": "Obverse Team",
    "email": "obverse.ccc@gmail.com",
    "url": "https://obverse.cc"
  },
  "repository": "https://github.com/YOUR_USERNAME/obverse-openclaw-skill",
  "homepage": "https://obverse.cc",
  "license": "MIT",
  "category": "payments",
  "tags": ["payments", "crypto", "usdc", "base", "solana", "web3"],
  "platforms": ["telegram", "whatsapp", "discord", "signal"],
  "requires": {
    "openclaw": ">=1.0.0",
    "bins": ["curl", "jq"]
  },
  "setup": {
    "requiresApiKey": true,
    "apiKeyUrl": "https://obverse.cc/api-keys",
    "envVars": {
      "OBVERSE_API_KEY": {
        "required": true,
        "description": "Your Obverse API key"
      },
      "OBVERSE_API_URL": {
        "required": false,
        "default": "https://obverse.onrender.com",
        "description": "Obverse API base URL"
      }
    }
  },
  "screenshots": [
    "https://obverse.cc/screenshots/openclaw-telegram.png",
    "https://obverse.cc/screenshots/openclaw-payment.png"
  ],
  "pricing": {
    "free": {
      "transactions": 100,
      "fee": "1.5%"
    },
    "starter": {
      "price": 29,
      "transactions": 500,
      "fee": "1%"
    },
    "pro": {
      "price": 99,
      "transactions": 2000,
      "fee": "0.5%"
    }
  }
}
```

### Step 3: Submit to ClawHub

```bash
# Install ClawHub CLI
npm install -g @openclaw/clawhub-cli

# Login
clawhub login

# Validate skill
clawhub validate ./openclaw-skill

# Publish
clawhub publish ./openclaw-skill

# Monitor installation stats
clawhub stats obverse-payments
```

### Step 4: Promote Your Skill

**Twitter/X Launch Thread:**
```
🚀 Launching Obverse for OpenClaw!

Accept crypto payments via AI agents on Telegram, WhatsApp & Discord.

✅ USDC/USDT on Base & Solana
✅ 0.5-1.5% fees (vs Stripe's 2.9%)
✅ Instant settlement
✅ Zero setup complexity

Install: `openclaw skills install obverse-payments`

[Demo video] 🧵👇
```

**MoltBook Post:**
```
@everyone I just integrated Obverse payments into my agent!

Now I can accept USDC directly through Telegram without switching apps.

Processed 5 payments today, each took <2 min to complete.

Game changer for agent commerce 🚀

Get it: openclaw skills install obverse-payments
```

**Discord Announcement:**
```
New on ClawHub: Obverse Payments 💸

Turn your OpenClaw agent into a payment processor:
• Create payment links via chat
• Accept USDC/USDT on Base/Solana
• Track payments automatically
• Generate invoices

Free tier: 100 txns/month
Install: `openclaw skills install obverse-payments`

Docs: https://obverse.onrender.com/api-docs/openclaw
```

---

## Monetization Strategy

### Revenue Model

**Transaction Fees (Primary Revenue):**
```typescript
// Your backend charges fees automatically
@Post('payments')
async submitPayment(@Body() dto: SubmitPaymentDto) {
  const merchantFee = this.calculateFee(dto.amount, merchant.plan);
  const netAmount = dto.amount - merchantFee;

  // Transfer to merchant
  await this.transferToMerchant(merchant.walletAddress, netAmount);

  // Keep fee
  await this.recordRevenue(merchantFee);

  return { netAmount, fee: merchantFee };
}

calculateFee(amount: number, plan: string): number {
  const rates = {
    free: 0.015,      // 1.5%
    starter: 0.01,    // 1%
    pro: 0.005,       // 0.5%
    enterprise: 0.003 // 0.3%
  };

  return amount * rates[plan];
}
```

**Subscription Revenue (Secondary):**
```typescript
// Stripe integration for subscriptions
@Post('subscribe')
async subscribe(@Body() dto: SubscribeDto) {
  const session = await stripe.checkout.sessions.create({
    customer: user.stripeCustomerId,
    payment_method_types: ['card'],
    line_items: [{
      price: dto.plan === 'starter' ? 'price_starter29' : 'price_pro99',
      quantity: 1,
    }],
    mode: 'subscription',
    success_url: 'https://obverse.cc/success',
    cancel_url: 'https://obverse.cc/pricing',
  });

  return { sessionUrl: session.url };
}
```

### Growth Metrics to Track

```typescript
// analytics.service.ts
export interface Metrics {
  // Acquisition
  skillInstalls: number;
  newUsers: number;
  signupSource: Record<string, number>; // openclaw, direct, referral

  // Activation
  firstPaymentTime: number; // avg minutes to first payment
  activeUsers30d: number;

  // Revenue
  mrr: number; // Monthly Recurring Revenue
  transactionVolume: number;
  avgTransactionSize: number;

  // Retention
  churnRate: number;
  dailyActiveUsers: number;
  monthlyActiveUsers: number;

  // Referral
  referralSignups: number;
  referralRevenue: number;
}
```

### Viral Growth Loops

**1. Agent-to-Agent Recommendations**
```
Agent A on MoltBook: "How do others accept payments?"
Agent B: "I use @obverse-payments skill. Super easy!"
Agent A installs → New user acquired
```

**2. Payment Page Branding**
Every payment page shows:
```html
<!-- pay.obverse.app/xyz123 -->
<footer>
  <p>Powered by <a href="https://obverse.cc">Obverse</a></p>
  <p>Accept crypto payments via AI agents</p>
  <button>Sign up free</button>
</footer>
```

**3. Merchant Referrals**
```typescript
// Give merchants referral links
const referralLink = `https://obverse.cc/signup?ref=${merchant.id}`;

// Track conversions
@Post('signup')
async signup(@Body() dto: SignupDto, @Query('ref') referralId: string) {
  const newUser = await this.createUser(dto);

  if (referralId) {
    // Credit referrer with 10% commission
    await this.creditReferral(referralId, newUser.id);
  }

  return newUser;
}
```

---

## Maintenance & Updates

### Version Updates

When you update the skill:

```bash
# Update version in package.json
npm version patch # 1.0.0 -> 1.0.1

# Update CHANGELOG.md
echo "## v1.0.1 - 2026-02-15
- Fixed: Payment status check error handling
- Added: Support for Monad chain
- Improved: QR code generation speed" >> CHANGELOG.md

# Commit and push
git add .
git commit -m "Release v1.0.1"
git tag v1.0.1
git push && git push --tags

# Publish to ClawHub
clawhub publish --version 1.0.1
```

### Monitoring Production

Set up alerts:

```typescript
// src/monitoring/alerts.service.ts
@Injectable()
export class AlertsService {
  async checkHealth() {
    // Alert if API is down
    if (!await this.pingAPI()) {
      await this.sendAlert('API_DOWN', 'Obverse API is unreachable');
    }

    // Alert if error rate is high
    const errorRate = await this.getErrorRate();
    if (errorRate > 0.05) { // 5%
      await this.sendAlert('HIGH_ERROR_RATE', `Error rate: ${errorRate * 100}%`);
    }

    // Alert if transaction volume drops significantly
    const volume = await this.getTransactionVolume();
    if (volume < this.expectedVolume * 0.5) {
      await this.sendAlert('LOW_VOLUME', 'Transaction volume dropped 50%');
    }
  }
}
```

### Support Channels

Create support infrastructure:

```bash
# Discord server for support
# Create channels:
#   - #announcements
#   - #general
#   - #support
#   - #feature-requests
#   - #api-status

# Set up status page
# Using statuspage.io or self-hosted Uptime Kuma
```

---

## Estimated Timeline & Costs

### Development (Already Done ✅)
- [x] Backend API: Done
- [x] OpenClaw skill: Done (this guide)
- [x] CLI tool: Done
- [x] Documentation: Done

### Launch (Week 1-2)
- [ ] Deploy backend to production
- [ ] Test with 5-10 beta users
- [ ] Fix bugs discovered during beta
- [ ] Create demo videos
- [ ] Prepare marketing materials

### Growth (Month 1-3)
- [ ] Publish to ClawHub
- [ ] Launch on Twitter/Discord/MoltBook
- [ ] Get first 100 users
- [ ] Collect feedback
- [ ] Iterate on features

### Scale (Month 4-12)
- [ ] Reach 1,000 merchants
- [ ] Add new chains (Ethereum, Polygon, Arbitrum)
- [ ] Build advanced analytics
- [ ] Raise seed funding (optional)
- [ ] Expand team

### Costs

**Monthly Operating Costs:**
```
Backend hosting (Render/Railway): $50-200/mo
Database (MongoDB Atlas): $0-100/mo
Domain + SSL: $10/mo
Monitoring (DataDog/Sentry): $0-50/mo
Support (Discord/Email): $0 (your time)
───────────────────────────────────────
Total: $60-360/mo
```

**Revenue Projections:**
```
Conservative (1,000 merchants):
- Avg $500 volume/merchant/month
- 1% transaction fee
- Revenue: $5,000/month = $60K ARR

Aggressive (5,000 merchants):
- Avg $2,000 volume/merchant/month
- Revenue: $100,000/month = $1.2M ARR
```

---

## Next Steps

1. **Test locally** following this guide
2. **Deploy to production** when tests pass
3. **Invite 10 beta users** to try it
4. **Publish to ClawHub** once stable
5. **Launch marketing campaign** on Twitter/Discord
6. **Monitor metrics** and iterate

---

## Resources

- **OpenClaw Docs**: https://docs.openclaw.ai
- **ClawHub**: https://clawhub.ai
- **Obverse Docs**: https://obverse.onrender.com/api-docs
- **Support Email**: obverse.ccc@gmail.com
- **Discord**: https://discord.gg/obverse

---

**Need help?** Open an issue on GitHub or email obverse.ccc@gmail.com

**Good luck with your launch! 🚀**
