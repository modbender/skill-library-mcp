---
name: near-getpay
description: Accept crypto payments (NEAR, USDC, USDT) via a beautiful payment page with PingPay or HOT PAY integration.
---

# NEAR GetPay Skill

Accept crypto payments (NEAR, USDC, USDT) via a beautiful payment page with PingPay or HOT PAY integration.

## 🎯 What It Does

Creates a hosted payment page where people can pay you in crypto with just a few clicks:

1. **Beautiful UI** - Mobile-friendly payment page with preset amounts
2. **Multi-token** - Accept NEAR, USDC, or USDT
3. **Dual provider** - Works with PingPay or HOT PAY (or both)
4. **Public URL** - Exposes via localhost.run tunnel
5. **First-time friendly** - Setup wizard guides new users
6. **Smart token selection** - Once a token is selected, others are hidden to avoid confusion (great for HOT PAY where each token has a unique checkout link)

## 🎨 User Flow

### PingPay Flow (default, best flow)
1. User selects token (NEAR, USDC, or USDT)
2. User enters amount or picks preset
3. Clicks "Pay Now"
4. Redirects to PingPay checkout with pre-filled amount

### HOT PAY Flow
1. User selects token (only configured tokens shown)
2. **Other tokens are hidden** to avoid confusion
3. User enters amount or picks preset
4. Clicks "Pay Now"
5. Redirects to HOT PAY checkout link for that specific token and amount

## 🚀 Quick Start

### 1. Installation

```bash
cd ~/.openclaw/skills
# Clone or extract the skill
npm install
```

### 2. Choose Your Provider

You need **either** PingPay **or** HOT PAY (or both):

**Option A: PingPay** (recommended for beginners)
- Sign up at https://pingpay.io
- Set your NEAR wallet in Dashboard → Settings
- Get API key from Dashboard → Settings → API Keys
- Add to `.env`: `PINGPAY_API_KEY=your_key_here`

**Option B: HOT PAY** (for advanced users)
- Visit https://pay.hot-labs.org/admin/overview
- Create payment links for each token (NEAR, USDC, USDT)
- Set your NEAR wallet as recipient when creating each link
- Copy each `item_id` and add to `.env`

### 3. Configure

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Display name (actual recipient is set in PingPay/HOT PAY dashboard!)
RECIPIENT_ADDRESS=your-account.near

# Choose provider
PAYMENT_PROVIDER=pingpay  # or 'hotpay'

# PingPay config (if using PingPay)
PINGPAY_API_KEY=your_api_key_here

# HOT PAY config (if using HOT PAY)
HOTPAY_NEAR_ITEM_ID=your_near_item_id
HOTPAY_USDC_ITEM_ID=your_usdc_item_id
HOTPAY_USDT_ITEM_ID=your_usdt_item_id
```

### 4. Start Server

```bash
./start.sh
```

Or manually:

```bash
npx ts-node start-tunnel.ts
```

This will:
- Start Express server on port 3000
- Create public URL via localhost.run
- Display the shareable payment link

### 5. Share Your Link

Share the generated `https://xxxxx.lhr.life` URL to accept payments!

## ⚠️ Important Notes

### Recipient Address Configuration

**The recipient address (where payments go) is configured at the provider level, NOT in the .env file:**

- **PingPay**: Set in your PingPay Dashboard → Settings → Wallet Address
- **HOT PAY**: Set when creating each payment link

The `RECIPIENT_ADDRESS` in `.env` is **only for display** on the payment page. To change where payments actually go, update your provider's dashboard settings.

### Tunnel Domains

localhost.run generates random URLs that change each restart. For a permanent domain:

1. Sign up at https://admin.localhost.run/
2. Configure your custom domain
3. Update the tunnel command in `start-tunnel.ts`

Or use your own reverse proxy (Cloudflare Tunnel, ngrok paid, etc.)

## 📖 Usage in OpenClaw

When a user asks to accept payments:

```
User: "Create a payment page to accept USDT donations"

Agent:
1. Check if near-getpay skill is installed
2. Ask which provider they want (PingPay or HOT PAY)
3. Guide them through setup if not configured
4. Run: cd ~/.openclaw/skills/near-getpay && ./start.sh
5. Share the generated public URL
```

### Example Conversation

```
User: I need to accept crypto payments

Agent: I'll set up a payment page for you using the GetPay skill.

First, do you have a PingPay or HOT PAY account?

User: No, what's easier?

Agent: PingPay is simpler. Here's what to do:

1. Sign up at https://pingpay.io
2. Add your NEAR wallet address in settings
3. Get an API key from Dashboard → API Keys
4. Share it with me (or add to .env yourself)

Let me know when you have the API key!

User: Got it: sk_test_abc123...

Agent: Perfect! Starting your payment server...

[runs start.sh]

✅ Your payment page is live:
https://abc123xyz.lhr.life

Share this link to accept NEAR, USDC, or USDT payments!
```

## 🛠️ File Structure

```
near-getpay/
├── SKILL.md              ← You are here
├── package.json
├── tsconfig.json
├── .env.example          ← Config template
├── .env                  ← Your config (gitignored)
├── start.sh              ← Quick start script
├── start-tunnel.ts       ← Server + tunnel launcher
├── server-simple.ts      ← Main payment server
└── scripts/
    ├── pingpay-client.ts
    └── payment-orchestrator.ts
```

## 🔧 Advanced Configuration

### Custom Port

Edit `.env`:

```env
PORT=8080
```

### Custom Tunnel

Replace localhost.run in `start-tunnel.ts`:

```typescript
// Option 1: ngrok
const tunnel = spawn('ngrok', ['http', PORT.toString()]);

// Option 2: Cloudflare Tunnel
const tunnel = spawn('cloudflared', ['tunnel', '--url', `http://localhost:${PORT}`]);

// Option 3: localtunnel (less reliable)
const tunnel = spawn('npx', ['localtunnel', '--port', PORT.toString()]);
```

### Webhook Integration (HOT PAY only)

HOT PAY sends webhooks to `/webhook/hotpay`. To use:

1. Expose your server publicly (not localhost.run - needs stable URL)
2. Configure webhook URL in HOT PAY dashboard
3. Server logs payment confirmations automatically

## 🎨 Customization

### Payment Amounts

Edit preset amounts in `server-simple.ts`:

```typescript
tokens: [
  {
    symbol: 'NEAR',
    chain: 'NEAR',
    decimals: 24,
    presets: [0.5, 1, 5, 10]  // ← Change these
  },
  // ...
]
```

### Branding

Update colors, fonts, text in the HTML template sections of `server-simple.ts`.

### Add More Tokens

Add to the `tokens` array (requires provider support):

```typescript
{
  symbol: 'ETH',
  chain: 'NEAR',
  decimals: 18,
  presets: [0.01, 0.05, 0.1, 0.5]
}
```

## 🐛 Troubleshooting

### "No provider configured"

Visit `http://localhost:3000/setup` to see setup instructions.

### "Permission denied (publickey)" (localhost.run)

Run: `ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -N ""`

### "Tunnel closed"

localhost.run tunnels timeout after inactivity. Restart the server.

### "Token not configured" (HOT PAY)

You need to create a payment link for each token. Missing tokens won't appear on the payment page.

### Provider returning errors

- **PingPay**: Check API key is valid and account is active
- **HOT PAY**: Verify item_ids match your created links

## 🔐 Security

- ✅ API keys stored in `.env` (gitignored)
- ✅ No private keys needed (payments go directly to provider)
- ✅ HTTPS via tunnel
- ✅ Webhook signature verification (HOT PAY)

**Never commit `.env` to git!**

## 📦 Sharing This Skill

### As a Skill Package

```bash
# From the skill directory
openclaw skill pack

# Share the .skill file
# Users install with: openclaw skill install near-getpay.skill
```

### Via GitHub

```bash
git init
git add .
git commit -m "Initial commit: NEAR GetPay skill"
git remote add origin https://github.com/yourusername/near-getpay.git
git push -u origin main
```

Users install with:

```bash
cd ~/.openclaw/skills
git clone https://github.com/yourusername/near-getpay.git
cd near-getpay
npm install
```

### Via Clawhub

1. Visit https://clawhub.com
2. Upload the `.skill` package
3. Add description and tags
4. Publish!

## 🤝 Support

- **Issues**: GitHub Issues (if published)
- **PingPay**: https://pingpay.io/docs
- **HOT PAY**: https://pay.hot-labs.org/admin
- **OpenClaw**: https://docs.openclaw.ai

## 📝 License

MIT

---

**Made for OpenClaw** 🐾
