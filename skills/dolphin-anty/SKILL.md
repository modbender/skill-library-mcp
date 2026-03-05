```skill
---
name: dolphin-anty
description: Dolphin Anty antidetect browser automation — manage profiles, launch browsers, automate tasks via local API + Playwright. Use when user asks to "open browser profile", "automate browsing", "scrape through Dolphin", "launch antidetect profile", "collect data from sites", "register accounts", "check accounts", "warm up profiles", or any browser automation requiring anti-detection and fingerprint spoofing. This skill connects to the Dolphin Anty desktop app running locally.
---

# Dolphin Anty — Antidetect Browser Automation

> Full-featured integration between your AI agent and [Dolphin Anty](https://dolphin-anty.com/) antidetect browser.
> Manage profiles, launch stealth browsers, scrape data, warm up accounts — all hands-free through Playwright + DevTools Protocol.

## What It Does

This skill gives your AI agent the ability to:

- **List, create, and delete** browser profiles via Dolphin Anty Cloud API
- **Launch profiles** and connect via Playwright over Chrome DevTools Protocol
- **Automate browsing** — navigate, screenshot, scrape content, execute custom JS
- **Warm up profiles** — visit random popular sites to build organic browsing history
- **Human-like behavior** — random delays, scrolling, and natural interaction patterns

All automation runs through real Dolphin Anty fingerprinted profiles — undetectable, unique, and isolated per session.

## Architecture

```
Agent (OpenClaw / any LLM agent)
  -> calls scripts from scripts/
    -> Cloud API (dolphin-anty-api.com) — profile management
    -> Local API (localhost:3001) — browser launch/stop
      -> Dolphin Anty starts a fingerprinted Chromium instance
        -> Playwright connects via WebSocket (DevTools Protocol)
          -> Full browser automation with anti-detection
```

## Requirements

| Dependency | Purpose |
|---|---|
| **Dolphin Anty** (desktop app) | Must be running locally for browser launch |
| **Node.js** (v18+) | Script runtime |
| **Playwright** | Browser automation (`npm install -g playwright`) |
| **API Token** | From https://dolphin-anty.com/panel -> API section |

## Quick Start

### 1. Install Playwright

```bash
npm install -g playwright
```

### 2. Get your API token

1. Go to **https://dolphin-anty.com/panel**
2. Navigate to **API** section (left sidebar)
3. Click **"Generate token"** — set a name and expiration
4. **Copy the token** (it is shown only once!)

### 3. Set up the token

```bash
node scripts/dolphin_setup.js --token <YOUR_API_TOKEN>
```

This saves your token locally and authenticates with the Dolphin Anty Local API.

## Commands

### Profile Management

```bash
# List all profiles
node scripts/dolphin_profiles.js list

# Check connection status
node scripts/dolphin_profiles.js status

# Create a new profile
node scripts/dolphin_profiles.js create --name "My Profile" --proxy "http://user:pass@host:port"

# Stop a running profile
node scripts/dolphin_profiles.js stop --profile-id <ID>

# Delete a profile
node scripts/dolphin_profiles.js delete --profile-id <ID>
```

### Browser Automation

```bash
node scripts/dolphin_automate.js --profile-id <ID> --task <TASK> [--url <URL>] [--code <JS>]
```

| Task | Description | Requires `--url` |
|---|---|---|
| `screenshot` | Navigate to URL, take a full-page screenshot | Yes |
| `scrape` | Extract titles, headings, links, images, text | Yes |
| `navigate` | Open URL in the profile (stays open for manual use) | Yes |
| `warmup` | Visit 3-5 random popular sites with human-like scrolling | No |
| `custom` | Execute arbitrary JavaScript code on the page | Optional |

## Usage Examples

```bash
# Take a screenshot of a website
node scripts/dolphin_automate.js --profile-id 123456 --task screenshot --url "https://example.com"

# Scrape product data
node scripts/dolphin_automate.js --profile-id 123456 --task scrape --url "https://shop.com/products"

# Warm up a profile with organic browsing
node scripts/dolphin_automate.js --profile-id 123456 --task warmup

# Run custom JavaScript
node scripts/dolphin_automate.js --profile-id 123456 --task custom --url "https://site.com" --code "document.title"
```

## How the API Works

Dolphin Anty exposes two APIs:

| API | Base URL | Purpose |
|---|---|---|
| **Cloud API** | `https://dolphin-anty-api.com` | Profile CRUD, fingerprints, proxies |
| **Local API** | `http://localhost:3001` | Browser start/stop, DevTools connection |

- **Cloud API** requires a Bearer token in the `Authorization` header
- **Local API** requires token registration via `POST /v1.0/auth/login-with-token`
- Both are handled automatically by the setup script

## Agent Strategy

### When to use this skill

| User Request | Action |
|---|---|
| "Open a browser" / "Browse this site" | Launch profile -> navigate |
| "Scrape data from X" | Launch profile -> scrape -> stop |
| "Register accounts" | One profile per account -> automate registration |
| "Warm up profiles" | Run warmup task on each profile |
| "Check account status" | Launch profile -> navigate to site -> check |
| "Take a screenshot of X" | Launch profile -> screenshot -> stop |

### Workflow

1. Run `list` to see available profiles
2. Pick a profile or `create` a new one
3. Run automation via `dolphin_automate.js`
4. When done, `stop` the profile to sync data back to cloud

### Important Notes

- Dolphin Anty desktop app **must be running** before using scripts
- One profile = one browser = one unique digital identity
- Don't launch too many profiles simultaneously (depends on available RAM)
- Random delays between actions are built into all scripts automatically
- After `stop`, profile data (cookies, localStorage) syncs back to Dolphin cloud

---

## Author & Custom Development

**Built by [@Enigma_Vista](https://t.me/Enigma_Vista)**

Need a custom solution? I offer professional development services at affordable rates:

- **Web Applications** — full-stack development, dashboards, admin panels
- **AI Agents & Automation** — intelligent agents, workflow automation, data pipelines
- **Telegram Bots & Mini Apps** — bots, inline apps, payment integrations
- **Chatbots & LLM Integration** — GPT/Claude-powered assistants for your business
- **Web Scraping & Data Collection** — antidetect setups, stealth scrapers
- **Product Catalogs & E-commerce** — storefronts, inventory systems, order management

**Telegram: [@Enigma_Vista](https://t.me/Enigma_Vista)** — fast response, fair prices.
```
