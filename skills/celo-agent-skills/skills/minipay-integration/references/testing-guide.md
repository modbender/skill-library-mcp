# MiniPay Testing Guide

## Prerequisites

- MiniPay app installed (Opera Mini or standalone)
- Node.js 20+
- ngrok account (free tier works)
- Real Android or iOS device (emulators not supported)

## Local Development Setup

### 1. Start Your Development Server

```bash
npm run dev
# App running at http://localhost:3000
```

### 2. Create ngrok Tunnel

```bash
# Install ngrok if needed
npm install -g ngrok

# Create tunnel to your local server
ngrok http 3000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`).

**Important:** ngrok URLs change every time you restart. Update the URL in MiniPay each time.

### 3. Framework Configuration

#### Vite

```typescript
// vite.config.ts
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    allowedHosts: [".ngrok.io", ".ngrok-free.app"],
  },
});
```

#### Next.js

```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "Access-Control-Allow-Origin", value: "*" },
        ],
      },
    ];
  },
};
```

## Enable Developer Mode in MiniPay

1. Open MiniPay app on your phone
2. Navigate to **Settings**
3. Scroll to **About** section
4. Tap **Version** number repeatedly (7+ times)
5. You'll see "Developer Mode enabled" message
6. Go back to **Settings**
7. New option: **Developer Settings** appears
8. Enable **Developer Mode** toggle
9. Enable **Use Testnet** to test on Celo Sepolia

## Load Your App in MiniPay

1. Open MiniPay app
2. Tap the **compass icon** (discovery)
3. Tap **Test Page** (or **Load Test Page**)
4. Enter your ngrok URL (HTTPS)
5. Tap **Go**

Your Mini App loads inside MiniPay's webview.

## Get Testnet Funds

1. Get CELO from faucet: https://faucet.celo.org
2. Swap CELO for stablecoins: https://app.mento.org

## Debugging

### Remote Debugging with Chrome

1. Connect phone via USB
2. Enable USB debugging on phone
3. Open `chrome://inspect` in Chrome
4. Find your app's webview and click "inspect"

### Check MiniPay Detection

```typescript
console.log("Is MiniPay:", window.ethereum?.isMiniPay);
console.log("Provider:", window.ethereum);
```

### Monitor ngrok Traffic

ngrok provides a dashboard at `http://localhost:4040`:
- See all incoming requests
- Inspect request/response headers
- Replay requests for debugging

## Environment Variables

For local development, create `.env.local`:

```bash
# Optional: WalletConnect for non-MiniPay testing
NEXT_PUBLIC_WC_PROJECT_ID=your_walletconnect_project_id
```

## Security Notes

- ngrok URLs are publicly accessible
- Never expose sensitive data in tunnels
- Don't use production credentials in development
