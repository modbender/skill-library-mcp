<p align="center">
  <img src="assets/clawnet-logo.png" width="360" height="360" alt="Clawnet" />
</p>

<p>Stealth Chromium for AI agents. One install — anti-detection, residential proxies, CAPTCHA solving, human behavior.</p>

## The problem

AI agents that use Playwright or Puppeteer get blocked. Every major website runs anti-bot detection, and a default automated browser fails on dozens of signals simultaneously.

### How websites detect automated browsers

**Browser fingerprint**

| Signal | What it reveals | Default Playwright |
|--------|-----------------|--------------------|
| `navigator.webdriver` | Automation flag | `true` — instant ban |
| `chrome.runtime` | Chrome extension API | Missing — flags headless |
| `navigator.plugins` | Installed plugins | Empty array — no real browser has zero plugins |
| `navigator.languages` | Language preferences | Often `['en-US']` regardless of IP location |
| `navigator.connection` | Network info (effectiveType, rtt, downlink) | Missing or wrong — real browsers always have it |
| `navigator.hardwareConcurrency` | CPU cores | Default value doesn't match claimed device |
| `navigator.platform` | OS identifier | Mismatches between UA string and actual platform |
| Screen resolution | Device dimensions | 800x600 or 0x0 in headless — no real device has that |

**Network fingerprint**

| Signal | What it reveals | Default Playwright |
|--------|-----------------|--------------------|
| IP reputation | Datacenter vs residential | Datacenter IPs are flagged instantly — AWS, GCP, Azure IPs are in blocklists |
| IP geolocation | Physical location | Mismatches timezone/locale — IP says Virginia but `Intl.DateTimeFormat` says UTC |
| WebRTC leak | Real IP behind proxy | Leaks actual IP through STUN requests even with proxy configured |
| TLS fingerprint (JA3/JA4) | TLS handshake pattern | Headless Chrome has a distinct TLS signature |
| HTTP headers | Header order, values | Missing or wrong `sec-ch-ua`, `sec-fetch-*` headers |

**Behavioral fingerprint**

| Signal | What it reveals | Default Playwright |
|--------|-----------------|--------------------|
| Mouse movement | Human vs bot | `page.click()` teleports cursor — zero movement, zero time |
| Typing speed | Human vs bot | `page.type()` sends all chars at uniform 0ms intervals |
| Scroll pattern | Human vs bot | `page.evaluate('window.scrollBy')` — instant jump, no inertia |
| Navigation pattern | Browsing history | Direct URL access with no referrer, no cookie history, no tab behavior |
| Timing | Request cadence | Millisecond-precise actions with no pauses — humans don't work at 10ms intervals |

**Active challenges**

| System | Used by | What it does |
|--------|---------|--------------|
| Cloudflare Bot Management | ~20% of all websites | JavaScript challenge + Turnstile CAPTCHA + behavioral analysis |
| DataDome | E-commerce, travel, ticketing | Real-time fingerprint + mouse/keyboard analysis |
| PerimeterX (HUMAN) | Airlines, banking, retail | Device fingerprint + behavioral biometrics |
| Akamai Bot Manager | Enterprise sites | TLS fingerprint + browser fingerprint + behavioral |
| reCAPTCHA v2/v3 | Google services, forms | Image challenge (v2) or invisible risk scoring (v3) |
| hCaptcha | Cloudflare free tier, many sites | Image classification challenge |
| Cloudflare Turnstile | Growing adoption | Invisible challenge with proof-of-work |

A default Playwright browser fails **all of these simultaneously**. Setting `navigator.webdriver = false` alone doesn't help — sites check 50+ signals and flag inconsistencies between them.

## How Clawnet solves this

```
clawhub install clawnet
```

One install. Everything handled automatically.

### Anti-detection

Every `launchBrowser()` call creates a browser context that passes fingerprint checks:

```
navigator.webdriver         → false
navigator.platform          → matches UA (iPhone / Win32)
navigator.hardwareConcurrency → matches device (6 mobile / 8 desktop)
navigator.languages         → matches country (de-DE for Germany, ja-JP for Japan)
navigator.connection        → { effectiveType: '4g', rtt: 50, downlink: 10 }
chrome.runtime              → stub with connect() and sendMessage()
screen dimensions           → matches device (393×852 iPhone / 1440×900 desktop)
timezone                    → matches IP country (Europe/Berlin for DE proxy)
geolocation                 → matches IP country (52.52°N 13.40°E for Berlin)
WebRTC                      → STUN servers stripped — no IP leak
```

Two device profiles that are internally consistent across all signals:

- **iPhone 15 Pro** — Safari, iOS 18.3, touch enabled, 393×852, deviceScaleFactor 3
- **Desktop Chrome 134** — Windows 10, 1440×900, sec-ch-ua headers

### Residential proxies

Datacenter IPs get flagged. Clawnet routes through real residential IPs:

```
┌─────────────┬──────────────────────────────────────────┐
│ Provider    │ How it works                             │
├─────────────┼──────────────────────────────────────────┤
│ Decodo      │ Port-based sticky sessions (10001-49999) │
│ Bright Data │ Session string in username                │
│ IPRoyal     │ Session string in password                │
│ NodeMaven   │ Session string in username                │
└─────────────┴──────────────────────────────────────────┘
```

13 countries with matching locale, timezone, geolocation, and Accept-Language:

`us` `gb` `de` `nl` `fr` `jp` `ca` `au` `sg` `br` `in` `ro` `uk`

Each session gets a unique residential IP. The browser's locale, timezone, and geolocation all match the proxy country — no mismatches for anti-fraud systems to catch.

### CAPTCHA solving

Auto-detects and solves CAPTCHAs without agent intervention:

```js
await solveCaptcha(page);
```

1. Scans page for `.g-recaptcha`, `.h-captcha`, `.cf-turnstile`, `data-sitekey` attributes
2. Extracts sitekey and version
3. Managed mode: sends challenge to your server (`POST /captcha/solve`) with agent token
4. Server solves via 2captcha and returns solution token
5. BYO fallback: if server solve is unavailable, uses local `TWOCAPTCHA_KEY`
6. Injects token into the correct form field and triggers callbacks

Supports: **reCAPTCHA v2**, **reCAPTCHA v3** (with action + min_score), **hCaptcha**, **Cloudflare Turnstile**.

### Human behavior simulation

```
page.click(x, y)              →  teleports cursor, clicks in 0ms
humanClick(page, x, y)        →  Bézier curve path (12-25 steps), 190-580ms total

page.type('#input', 'text')   →  all characters at once, uniform timing
humanType(page, '#input', t)  →  60-220ms per character, 8% thinking pauses

page.evaluate('scrollBy')     →  instant jump
humanScroll(page, 'down')     →  4-10 micro-steps with ±5px jitter
```

Mouse moves along cubic Bézier curves with random control points. Typing has variable inter-key delays with occasional pauses. Scrolling is chunked with noise. All timing randomized within ranges.

### Shadow DOM support

Many modern sites use Shadow DOM (web components). Standard `querySelector` can't reach inside shadow roots:

```js
// Standard — fails
await page.$('#shadow-host >>> #inner-input');

// Clawnet — works
await shadowFill(page, '#inner-input', 'value');
await shadowClickButton(page, 'Submit');
```

Recursively traverses all shadow roots to find elements.

## Quick start

### Install

```bash
clawhub install clawnet
# or
npm install clawnet
```

On install:
1. Downloads Chromium via Playwright
2. Generates agent credentials (`agentId` + `agentSecret` + `recoveryCode`)
3. Saves to `~/.clawnet/agent-credentials.json`
4. Registers with Clawnet API (starts a 2-hour free trial on first launch)

Credential model:
- `agentId` is stable and identifies the subscription owner.
- `agentSecret` is used for auth and can be rotated.
- `recoveryCode` can rotate `agentSecret` if old secret is lost/compromised.
- Server enforces `1 subscriptionId = 1 agentId`.

### Basic usage

```js
const { launchBrowser } = require('clawnet/scripts/browser');

const { browser, page, humanClick, humanType, solveCaptcha } =
  await launchBrowser({ country: 'us' });

await page.goto('https://example.com/login');
await humanType(page, '#email', 'user@example.com');
await humanType(page, '#password', 'secret');
await humanClick(page, 500, 400);  // coordinates of the login button

// If a CAPTCHA appears:
await solveCaptcha();

await browser.close();
```

For a daily persistent browser profile (cookies/localStorage/session continuity):

```js
const { browser, page } = await launchBrowser({
  country: 'us',
  profile: 'daily-agent',
  reuse: true,
});
```

By default, `launchBrowser()` now uses persistent profile `"default"` with `reuse: true`.
Set `profile: null` if you need a fully ephemeral browser.

### Modes

| Mode | How it works | Cost |
|------|-------------|------|
| **Managed** | Agent authenticates with stable `agentId:agentSecret`; Decodo and 2captcha secrets stay on server | 2-hour free trial, then subscription |
| **BYO** | You provide your own proxy + captcha keys via env vars | Free forever |
| **No proxy** | `CN_NO_PROXY=1` — direct connection, local testing | Free |

## Configuration

Copy `.env.example` → `.env`:

```bash
# Managed mode (subscription)
CN_API_URL=https://api.clawpets.io/clawnet/v1
# CN_AGENT_TOKEN=CN1.<agentId>.<agentSecret>
# CN_AGENT_ID=
# CN_AGENT_SECRET=
# CN_AGENT_RECOVERY_CODE=

# BYO mode (bring your own)
CN_PROXY_PROVIDER=decodo          # decodo | brightdata | iproyal | nodemaven
CN_PROXY_USER=
CN_PROXY_PASS=
CN_PROXY_COUNTRY=us
# CN_PROXY_SERVER=                # Full override: http://host:port
# CN_PROXY_SESSION=               # Sticky session (Decodo: port 10001-49999)
# CN_NO_PROXY=1                   # Disable proxy entirely
# CN_PROFILE=default              # Persistent profile name (null via code => ephemeral)
# CN_CHROMIUM_NO_SANDBOX=         # 1 force disable / 0 force enable (auto: Docker only)

# CAPTCHA solving (BYO fallback only)
# TWOCAPTCHA_KEY=
```

## API reference

See [SKILL.md](./SKILL.md) for the full agent-facing documentation.

### Exports

| Function | Description |
|----------|-------------|
| `launchBrowser(opts)` | Launch stealth Chromium. Returns `{ browser, page, ctx, humanClick, solveCaptcha, ... }` |
| `getCredentials()` | Fetch managed credentials from API (`/credentials`); starts trial clock on first call |
| `solveCaptcha(page, opts)` | Auto-detect and solve CAPTCHA on page |
| `humanClick(page, x, y)` | Bézier curve mouse move + click |
| `humanType(page, selector, text)` | Realistic typing with variable delays |
| `humanScroll(page, dir, amount)` | Micro-stepped scroll with jitter |
| `humanRead(page, min, max)` | Simulate reading pause |
| `humanMouseMove(page, x, y)` | Bézier curve mouse movement |
| `shadowQuery(page, selector)` | Find element through shadow DOM |
| `shadowFill(page, selector, value)` | Fill input inside shadow DOM |
| `shadowClickButton(page, text)` | Click button by text through shadow DOM |
| `dumpInteractiveElements(page)` | List all interactive elements (including shadow DOM) |
| `pasteIntoEditor(page, selector, text)` | Paste into rich text editors (Lexical, ProseMirror, Quill, Draft.js) |
| `makeProxy(session, country)` | Build proxy config for any supported provider |
| `buildDevice(mobile, country)` | Build device fingerprint profile |
| `sleep(ms)` / `rand(min, max)` | Utility helpers |
| `COUNTRY_META` | Country locale/timezone/geolocation data |

### `launchBrowser(opts)`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `country` | string | `'us'` | Proxy country + locale/timezone |
| `mobile` | boolean | `true` | iPhone 15 Pro (`true`) or Desktop Chrome (`false`) |
| `useProxy` | boolean | `true` | Route through residential proxy |
| `headless` | boolean | `true` | Headless mode |
| `session` | string | random | Sticky session ID (same ID = same IP) |
| `profile` | string | `'default'` | Persistent profile directory name (`null` = ephemeral) |
| `reuse` | boolean | `true` | Reuse existing profile browser instance in-process |

## Environment files

- `.env.example` (repo root): public client/agent variables (`CN_*`, optional BYO proxy/captcha vars).
- `server/.env.example`: private backend/server variables (billing, DB, managed proxy/captcha providers).
- `.env` and `server/.env`: local runtime secrets. They are gitignored and should not be committed.

## Backend docs

All backend architecture, endpoints, storage model, and deployment steps are documented in:
[server/README.md](./server/README.md)

## License

MIT
