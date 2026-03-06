# 🌱 Chia WalletConnect - Telegram Signature Verification

**Verify Chia wallet ownership via Telegram using WalletConnect and Sage Wallet.**

A Telegram Web App (Mini App) that enables seamless wallet signature verification for Chia blockchain addresses through WalletConnect integration with Sage Wallet, powered by MintGarden's signature verification API.

---

## ✨ Features

- 🔗 **WalletConnect v2 Integration** — Industry-standard wallet connection protocol
- 📱 **Telegram Mini App** — Native in-app experience
- 🔐 **Signature Verification** — Cryptographic proof of wallet ownership
- ✅ **MintGarden API** — Trusted signature validation
- 🎯 **CHIP-0002 Support** — Sage Wallet compatibility
- 💚 **Mobile-First** — Optimized for Telegram mobile clients
- 🚀 **Zero Manual Copy/Paste** — Seamless user experience

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Telegram Bot   │
│ (Clawdbot)      │
└────────┬────────┘
         │ /verify command
         │ Opens Web App →
         ▼
┌─────────────────────────────┐
│   Telegram Mini App         │
│   (Hosted Web Frontend)     │
│                             │
│  ┌──────────────────────┐  │
│  │  WalletConnect v2    │  │
│  │  Sign Client         │  │
│  └──────────┬───────────┘  │
│             │               │
│             │ Connect & Sign
│             ▼               │
│      ┌──────────────┐      │
│      │ Sage Wallet  │      │
│      │   (Mobile)   │      │
│      └──────┬───────┘      │
│             │               │
│             │ Returns signature
│             ▼               │
│  ┌──────────────────────┐  │
│  │  Send to Bot via     │  │
│  │  Telegram.sendData() │  │
│  └──────────────────────┘  │
└─────────────────────────────┘
              │
              │ web_app_data
              ▼
┌─────────────────────────┐
│  Bot Webhook Handler    │
│  (Verifies signature)   │
└────────┬────────────────┘
         │
         │ POST /verify_signature
         ▼
┌─────────────────────────┐
│  MintGarden API         │
│  (Signature validation) │
└─────────────────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
# Install skill via ClawdHub
clawdhub install chia-walletconnect

# Install dependencies
cd skills/chia-walletconnect
npm install

# Make CLI executable
chmod +x cli.js
```

### Local Development

```bash
# Start the development server
npm start
# Server runs on http://localhost:3000

# Test in browser
open http://localhost:3000
```

### CLI Usage

```bash
# Generate a challenge
node cli.js challenge xch1abc... telegram_user_123

# Verify a signature
node cli.js verify xch1abc... "message" "signature" "pubkey"

# Validate address format
node cli.js validate xch1abc...

# Start web server
node cli.js server
```

---

## 📱 Telegram Bot Integration

### Step 1: Deploy Web App

Deploy the `webapp/` folder to a public HTTPS URL:

**Option A: Vercel**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd webapp
vercel

# Copy the deployment URL (e.g., https://your-app.vercel.app)
```

**Option B: Netlify**
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
cd webapp
netlify deploy --prod

# Copy the deployment URL
```

**Option C: Your Own Server**
```bash
# Run the server on your VPS
npm start

# Use ngrok for testing
ngrok http 3000
```

### Step 2: Register with BotFather

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newapp` or `/editapp`
3. Select your bot
4. **Web App URL:** Enter your deployed URL (e.g., `https://your-app.vercel.app`)
5. **Short Name:** `verify` (or any unique identifier)

### Step 3: Add Bot Command

Create a `/verify` command in your bot:

```javascript
// In your Clawdbot skill or bot handler

bot.onText(/\/verify/, async (msg) => {
  const chatId = msg.chat.id;
  
  // Send inline button to launch Web App
  bot.sendMessage(chatId, 'Click below to verify your Chia wallet:', {
    reply_markup: {
      inline_keyboard: [[
        {
          text: '🌱 Verify Wallet',
          web_app: { url: 'https://your-app.vercel.app' }
        }
      ]]
    }
  });
});
```

### Step 4: Handle Web App Data

Listen for signature data returned from the Web App:

```javascript
// Handle web_app_data callback
bot.on('web_app_data', async (msg) => {
  const chatId = msg.chat.id;
  const data = JSON.parse(msg.web_app_data.data);
  
  const { address, message, signature, publicKey, userId } = data;
  
  console.log(`🔐 Received signature from ${address}`);
  
  // Verify signature with MintGarden API
  const { verifySignature } = require('./lib/verify');
  const result = await verifySignature(address, message, signature, publicKey);
  
  if (result.verified) {
    bot.sendMessage(chatId, `✅ Wallet verified!\n\nAddress: ${address}`);
    
    // Store verification in your database
    // await saveVerification(userId, address);
    
  } else {
    bot.sendMessage(chatId, `❌ Verification failed: ${result.error}`);
  }
});
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# Server configuration
PORT=3000
NODE_ENV=production

# WalletConnect Project ID
# Get yours at https://cloud.walletconnect.com
WALLETCONNECT_PROJECT_ID=6d377259062295c0f6312b4f3e7a5d9b

# Optional: MintGarden API
MINTGARDEN_API_URL=https://api.mintgarden.io

# Optional: Your backend API
BACKEND_API_URL=https://your-backend.com/api
```

### WalletConnect Project ID

The included Project ID (`6d377259062295c0f6312b4f3e7a5d9b`) is from the Dracattus reference implementation. For production:

1. Visit [WalletConnect Cloud](https://cloud.walletconnect.com)
2. Create a new project
3. Copy your Project ID
4. Update in `webapp/app.js`:

```javascript
const WALLETCONNECT_PROJECT_ID = 'your-project-id-here';
```

---

## 🛠️ API Reference

### MintGarden Signature Verification

**Endpoint:** `POST https://api.mintgarden.io/address/verify_signature`

**Request:**
```json
{
  "address": "xch1abc...",
  "message": "Verify ownership of...",
  "signature": "signature_hex",
  "pubkey": "public_key_hex"
}
```

**Response:**
```json
{
  "verified": true
}
```

### CHIP-0002 Methods

The skill uses these WalletConnect methods for Sage Wallet:

| Method | Description |
|--------|-------------|
| `chip0002_getPublicKeys` | Fetch wallet public keys |
| `chip0002_signMessage` | Sign a message with wallet |
| `chia_getCurrentAddress` | Get current receive address |

---

## 📂 Project Structure

```
chia-walletconnect/
├── webapp/                   # Telegram Web App frontend
│   ├── index.html           # Main UI
│   ├── app.js               # WalletConnect logic
│   └── styles.css           # Styling
├── lib/                      # Core libraries
│   ├── challenge.js         # Challenge generation
│   ├── verify.js            # MintGarden API client
│   └── telegram.js          # Telegram Web App helpers
├── server/                   # Optional backend
│   └── index.js             # Express server for webhooks
├── cli.js                    # CLI interface
├── package.json             # Dependencies
├── SKILL.md                 # Clawdbot skill documentation
└── README.md                # This file
```

---

## 🧪 Testing

### Test Locally

1. **Start server:**
   ```bash
   npm start
   ```

2. **Open in browser:**
   ```
   http://localhost:3000
   ```

3. **Test WalletConnect:**
   - Click "Connect Sage Wallet"
   - Copy the URI or scan QR code
   - Open Sage Wallet → paste URI
   - Approve connection
   - Sign the challenge message

### Test with Telegram

1. **Use ngrok for local testing:**
   ```bash
   ngrok http 3000
   ```

2. **Update BotFather Web App URL** to ngrok URL

3. **Send `/verify` in your bot**

4. **Click the inline button**

5. **Complete verification flow**

---

## 🔐 Security Considerations

### ✅ What's Secure

- **Challenge Nonces** — Prevents replay attacks
- **Timestamp Validation** — Challenges expire after 5 minutes
- **MintGarden Verification** — Cryptographic signature validation
- **HTTPS Required** — Telegram enforces HTTPS for Web Apps
- **No Private Keys** — Never requests or stores private keys

### ⚠️ Important Notes

1. **Store Verifications Securely**
   - Use encrypted database
   - Don't log signatures/public keys
   - Implement rate limiting

2. **Validate User Identity**
   - Link Telegram user ID to verified address
   - Prevent address spoofing
   - Implement cooldown periods

3. **Production Checklist**
   - [ ] Use your own WalletConnect Project ID
   - [ ] Enable CORS only for your domain
   - [ ] Implement rate limiting on verification endpoint
   - [ ] Log verification attempts for auditing
   - [ ] Use environment variables for secrets
   - [ ] Deploy behind CDN for DDoS protection

---

## 💡 Use Cases

### 1. **NFT Gated Chats**
Verify users own a specific NFT before granting access to Telegram groups.

### 2. **Airdrop Eligibility**
Verify wallet ownership before distributing tokens.

### 3. **Authentication**
Use wallet as login credential (Web3-style auth).

### 4. **Proof of Holdings**
Verify users hold a minimum XCH balance or specific CATs.

### 5. **DAO Voting**
Authenticate voters based on token holdings.

---

## 🐛 Troubleshooting

### Problem: WalletConnect URI Not Working

**Solutions:**
1. Check Sage Wallet supports WalletConnect v2
2. Try manual URI paste instead of QR scan
3. Ensure Sage is on the latest version
4. Check console for connection errors

### Problem: Signature Verification Fails

**Solutions:**
1. Ensure correct message format (exact match)
2. Verify public key matches address
3. Check MintGarden API status
4. Confirm signature encoding (hex/base64)

### Problem: Web App Doesn't Load

**Solutions:**
1. Verify HTTPS deployment (Telegram requires SSL)
2. Check CORS headers
3. Test URL directly in browser
4. Review Telegram Bot logs

### Problem: "No Public Key Available"

**Solutions:**
1. Sage may not expose public key via WalletConnect
2. Try alternative method (signature still works)
3. Public key is optional for verification

---

## 🔄 Workflow Diagram

```
User              Telegram           Web App          Sage Wallet      MintGarden
 │                   │                  │                   │               │
 ├─ /verify ────────>│                  │                   │               │
 │                   ├─ Web App button >│                   │               │
 │                   │                  ├─ WC connect ─────>│               │
 │                   │                  │<── approve ───────┤               │
 │                   │                  ├─ sign request ───>│               │
 │                   │                  │<── signature ─────┤               │
 │                   │<─ sendData() ────┤                   │               │
 │                   ├──────────────────────── verify ──────────────────────>│
 │                   │<──────────────────────── verified ────────────────────┤
 │<─ ✅ Verified ────┤                  │                   │               │
 │                   │                  │                   │               │
```

---

## 📊 Performance

### Metrics

| Stage | Time |
|-------|------|
| WalletConnect Init | ~1-2s |
| Connection Approval | User-dependent |
| Signature Request | ~2-5s |
| MintGarden Verification | ~0.5-1s |
| **Total (optimal)** | **~5-10s** |

### Optimization Tips

1. **Cache WalletConnect sessions** — Reconnect faster on repeat use
2. **Batch verifications** — Verify multiple addresses at once
3. **Implement retry logic** — Handle transient network errors
4. **Use CDN** — Serve static assets faster

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

## 📜 License

**MIT License** — Koba42 Corp

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.

---

## 🔗 Links

- **MintGarden API:** https://api.mintgarden.io/docs
- **WalletConnect:** https://docs.walletconnect.com/
- **Telegram Web Apps:** https://core.telegram.org/bots/webapps
- **Sage Wallet:** https://www.sagewallet.io/
- **CHIP-0002:** https://github.com/Chia-Network/chips/blob/main/CHIPs/chip-0002.md

---

## 🌟 Credits

**Built by:** Koba42 Corp  
**Inspired by:** Dracattus Web App WalletConnect implementation  
**Powered by:** MintGarden API, WalletConnect, Sage Wallet, Telegram Bot API

---

<div align="center">

**🌱 Verify with confidence. Own with proof. 🌱**

[![ClawdHub](https://img.shields.io/badge/ClawdHub-chia--walletconnect-green)](https://clawdhub.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![WalletConnect](https://img.shields.io/badge/WalletConnect-v2-orange)](https://walletconnect.com)

</div>
