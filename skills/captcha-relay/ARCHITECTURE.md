# CAPTCHA Relay v2 — Architecture

## Overview

Token-based CAPTCHA relay: extract sitekey from automated browser, serve a relay page with the real CAPTCHA widget, human solves on phone, token relayed back and injected via CDP.

## Flow

```
Agent Browser → CAPTCHA detected
       ↓
  Extract type + sitekey (CDP page target)
       ↓
  Start relay HTTP server (random port)
       ↓
  Start tunnel (localtunnel / cloudflared / Tailscale)
       ↓
  Send URL to human (Telegram inline button)
       ↓
  Human opens on phone → solves CAPTCHA widget
       ↓
  Token POSTed to /token → written to /tmp/captcha-relay-token.txt
       ↓
  Inject token into browser page (CDP page target)
       ↓
  Cleanup (stop server + tunnel)
```

## File Structure

```
skills/captcha-relay/
├── SKILL.md              # Skill manifest
├── ARCHITECTURE.md       # This file
├── TAILSCALE.md          # Tailscale setup guide
├── package.json
├── index.js              # Main orchestrator (CLI + module)
├── lib/
│   ├── cdp.js            # CDP client (WebSocket, page targets)
│   ├── detect.js         # CAPTCHA detection + sitekey extraction
│   ├── server.js         # HTTP relay server
│   ├── tunnel.js         # Tunnel management (localtunnel, cloudflared)
│   ├── inject.js         # Token injection back into browser
│   └── templates/        # HTML relay pages
│       ├── recaptcha-v2.html
│       ├── hcaptcha.html
│       └── turnstile.html
└── fallback/
    └── screenshot.js     # Screenshot grid fallback (v1 style)
```

## Key Modules

### detect.js
Connects to CDP via page target (not browser-level WS URL). Evaluates JS to find CAPTCHA widgets by class/data-sitekey attributes and iframe src parsing.

### server.js
Minimal HTTP server (no Express). Serves templated CAPTCHA page on GET /, receives token on POST /token. Writes token to `/tmp/captcha-relay-token.txt` and resolves a Promise.

### tunnel.js
Tries localtunnel (via `npx localtunnel`) first, falls back to cloudflared, then local IP. Returns `{ url, process, isLocal, method }`.

### inject.js
Connects to CDP page target and injects token via:
- Setting textarea value (`#g-recaptcha-response`, etc.)
- Dispatching input events
- Calling registered callbacks (data-callback attr, `___grecaptcha_cfg` internal, etc.)

### Templates
Each HTML template loads the provider's JS SDK, renders the widget with the extracted sitekey, and POSTs the token back to `/token` on solve. Dark theme, mobile-optimized.

## Domain Matching

| Provider | Client Domain Check | Token Relay Status |
|----------|--------------------|--------------------|
| reCAPTCHA v2 | Yes — but **works anyway** for many sites | ✅ Tested working |
| hCaptcha | No client check | ✅ Should work reliably |
| Turnstile | Yes | ⚠️ Untested |

**Lesson learned**: reCAPTCHA v2 token relay works better than expected. Tested with Google's demo — the widget renders on any domain and the token is accepted.

## Lessons Learned (v2 Development)

### Tunneling
- **cloudflared**: Too heavy for constrained machines (ARM, low-RAM). Binary is large and resource-hungry.
- **localhost.run**: Free tier has broken TLS certificates. Unusable.
- **localtunnel**: Works well via `npx localtunnel`. Free, no install. Downside: shows a splash/interstitial page on first visit ("Click to Continue"). Minor UX annoyance.
- **Tailscale**: Recommended for production. No tunnel needed — devices on the same Tailnet can reach the relay server directly via Tailscale IP. No splash pages, always-on. See TAILSCALE.md.

### CDP Connection
- Must use **page-level** WebSocket URL from `/json/list`, not the browser-level URL from `/json/version`. The browser-level connection can't evaluate JS in page context.

### Token Injection
- Setting textarea value alone isn't enough — must also trigger the callback. Walking `___grecaptcha_cfg.clients` tree to find the callback function works for reCAPTCHA v2.

## Dependencies

- `ws` — WebSocket client for CDP
- `sharp` — image processing (screenshot fallback mode)
- `localtunnel` — tunnel (via npx, not installed)
- `cloudflared` — system binary (optional fallback)
