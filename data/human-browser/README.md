# Human Browser — Cloud Stealth Browser for AI Agents

> **No Mac Mini. No local machine. Your agent runs it anywhere.**  
> Residential IPs from 10+ countries. Bypasses Cloudflare, DataDome, PerimeterX.
>
> 🌐 **Product page:** https://humanbrowser.cloud  
> 💬 **Support:** https://t.me/virixlabs

---

## Why your agent needs this

Regular Playwright on a data-center server gets blocked **immediately** by:
- Cloudflare (bot score detection)
- DataDome (fingerprint analysis)
- PerimeterX (behavioral analysis)
- Instagram, LinkedIn, TikTok (residential IP requirement)

Human Browser solves this by combining:
1. **Residential IP** — real ISP address from the target country (not a data center)
2. **Real device fingerprint** — iPhone 15 Pro or Windows Chrome, complete with canvas, WebGL, fonts
3. **Human-like behavior** — Bezier mouse curves, 60–220ms typing, natural scroll with jitter
4. **Full anti-detection** — `webdriver=false`, no automation flags, correct timezone & geolocation

---

## Quick Start

**No setup required** — just call `launchHuman()` and it automatically activates a free trial:

```js
const { launchHuman } = require('./scripts/browser-human');

// 🚀 Zero config — auto-fetches trial credentials from humanbrowser.cloud
const { browser, page, humanType, humanClick, humanScroll, sleep } = await launchHuman();
// Output: 🎉 Human Browser trial activated! (~100MB Romania residential IP)

// Specific country
const { page } = await launchHuman({ country: 'us' }); // US residential IP
const { page } = await launchHuman({ country: 'gb' }); // UK residential IP

// Desktop Chrome (Windows fingerprint)
const { page } = await launchHuman({ mobile: false, country: 'us' });

await page.goto('https://example.com', { waitUntil: 'domcontentloaded' });
await humanScroll(page, 'down');
await humanType(page, 'input[type="email"]', 'user@example.com');
await humanClick(page, 760, 400);
await browser.close();
```

> **Trial exhausted?** Get a paid plan at https://humanbrowser.cloud, then set `PROXY_USER` / `PROXY_PASS` in your `.env`.

---

## Setup

```bash
npm install playwright
npx playwright install chromium --with-deps

# Install via skill manager
clawhub install al1enjesus/human-browser
```

---

## Supported Countries

| Country | Code | Best for |
|---------|------|----------|
| 🇷🇴 Romania | `ro` | Polymarket, Instagram, Binance, Cloudflare |
| 🇺🇸 United States | `us` | Netflix, DoorDash, US Banks, Amazon |
| 🇬🇧 United Kingdom | `gb` | Polymarket, Binance, BBC iPlayer |
| 🇩🇪 Germany | `de` | EU services, German e-commerce |
| 🇳🇱 Netherlands | `nl` | Crypto, Polymarket, Web3 |
| 🇯🇵 Japan | `jp` | Japanese e-commerce, Line |
| 🇫🇷 France | `fr` | EU services, luxury brands |
| 🇨🇦 Canada | `ca` | North American services |
| 🇸🇬 Singapore | `sg` | APAC/SEA e-commerce |
| 🇦🇺 Australia | `au` | Oceania content |

---

## Proxy Providers

### Option 1: Human Browser Managed (recommended)
Buy directly at **humanbrowser.cloud** — we handle everything, from $13.99/mo.  
Supports crypto (USDT/ETH/BTC/SOL) and card. AI agents can auto-purchase.

### Option 2: Bring Your Own Proxy

Plug any residential proxy into Human Browser via env vars.
**Recommended providers** (tested and verified):

| Provider | Quality | Price | Best for |
|---|---|---|---|
| **[Decodo](https://decodo.com)** (ex-Smartproxy) | ⭐⭐⭐⭐⭐ | ~$2.5/GB | Cloudflare, DataDome, all-round. No KYC. |
| **[Bright Data](https://get.brightdata.com/4ihj1kk8jt0v)** | ⭐⭐⭐⭐⭐ | ~$8.4/GB | Enterprise-grade, 72M+ IPs, 195 countries |
| **[IPRoyal](https://iproyal.com)** | ⭐⭐⭐⭐ | ~$1.75/GB | High volume, budget, ethically sourced |
| **[NodeMaven](https://nodemaven.com)** | ⭐⭐⭐⭐ | ~$3.5/GB | High success rate, pay-per-GB, no minimums |
| **[Oxylabs](https://oxylabs.io)** | ⭐⭐⭐⭐⭐ | ~$8/GB | Business-grade, dedicated support |

```env
PROXY_HOST=your-proxy-host
PROXY_PORT=22225
PROXY_USER=your-username
PROXY_PASS=your-password
```

---

## How it compares

| Feature | Regular Playwright | Human Browser |
|---------|-------------------|---------------|
| IP type | Data center → blocked | Residential → clean |
| Bot detection | Fails | Passes all |
| Mouse movement | Instant teleport | Bezier curves |
| Typing speed | Instant | 60–220ms/char |
| Fingerprint | Detectable bot | iPhone 15 Pro |
| Countries | None | 10+ residential |
| Cloudflare | Blocked | Bypassed |
| DataDome | Blocked | Bypassed |

---

→ **Product page + pricing:** https://humanbrowser.cloud  
→ **Support & questions:** https://t.me/virixlabs
