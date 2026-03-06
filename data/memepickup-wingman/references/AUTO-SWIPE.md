# Auto-Swipe Reference — MemePickup Wingman

Consolidated auto-swipe documentation for both OpenClaw and Manus.

## How It Works

Auto-swipe automates the process of reviewing dating profiles:

1. Opens the dating app (native or web)
2. Screenshots each profile
3. Sends the screenshot to `scripts/api.sh analyze` (or `api.py`)
4. The API returns a match score and recommendation
5. Executes the recommended action (swipe, like, comment, skip)
6. Moves to the next profile

**The MemePickup API only provides scoring and recommendations. The actual swiping is performed by the platform (OpenClaw screen interaction or Manus browser automation).**

## Platform Comparison

| Aspect | OpenClaw | Manus |
|--------|----------|-------|
| Method | Native screen interaction | Browser automation |
| App version | Native mobile app | Web version |
| Hinge | Yes | Yes (hinge.co) |
| Tinder | Yes | Yes (tinder.com) |
| Bumble | Yes | Yes (bumble.com) |
| Instagram | Yes | No (no web dating UI) |
| Bot detection risk | Lower (native app behavior) | Higher (web automation patterns) |
| Speed | Fast (native gestures) | Moderate (browser rendering) |
| Login persistence | App stays logged in | May need re-login per session |

## Web URLs for Dating Apps (Manus)

| Platform | URL | Notes |
|----------|-----|-------|
| Hinge | hinge.co | Full web app, all features |
| Tinder | tinder.com | Web version, most features available |
| Bumble | bumble.com | Web version, most features available |
| Instagram | — | No dating-specific web interface |

## Safety Rails

These apply on **both** platforms:

- **Max 30 profiles per session** — prevents excessive API usage and reduces detection risk
- **Random 3-8 second delays** between actions — mimics human browsing patterns
- **Immediate stop on CAPTCHA** — if a CAPTCHA appears, auto-swipe stops and alerts the user
- **Immediate stop on error** — any API error or interaction failure halts the session
- **User can disable anytime** — say "stop" or "pause auto-swipe"

## Ban Risk

**Auto-swiping violates the Terms of Service of all dating platforms.** Users must acknowledge this before enabling.

### Risk by Platform

| Platform | Native (OpenClaw) | Web (Manus) | Notes |
|----------|-------------------|-------------|-------|
| Hinge | Medium | High | Hinge actively monitors automation patterns |
| Tinder | Medium | High | Tinder uses device fingerprinting on web |
| Bumble | Low-Medium | Medium-High | Bumble's web detection is less aggressive |
| Instagram | Low | N/A | DM automation is lower risk than swipe automation |

### Risk Factors

**Lower risk:**
- Longer delays between actions
- Fewer profiles per session
- Mixing swipe right and left (not swiping right on everything)
- Using during normal hours (not 3am)

**Higher risk:**
- Fast, consistent timing between actions
- Swiping right on every profile
- Running many sessions per day
- Web automation (detectable via browser fingerprinting)
- New accounts (less established history)

### Mitigation

- The 3-8 second random delay is designed to mimic natural behavior
- The 30-profile cap keeps sessions short
- Profile analysis produces realistic swipe patterns (mix of right/left/skip)
- If you get a temporary ban, stop using auto-swipe for at least a week

## Rate Limiting

### MemePickup API

- 30 requests per minute
- Each profile analysis = 1 credit
- A full 30-profile session = 30 credits
- Free tier users (5 credits) will exhaust credits quickly — Pro recommended for auto-swipe

### Dating Platform Rate Limits

Dating apps may rate-limit interactions independently of MemePickup:

- **Hinge:** Daily like limit (varies by subscription tier)
- **Tinder:** Daily swipe limit (varies by subscription tier)
- **Bumble:** Daily swipe limit (varies by subscription tier)
- **Instagram:** Daily DM/follow limits

Auto-swipe respects the 30-profile cap but cannot detect platform-imposed limits. If the platform stops responding to actions, the session will halt.

## Credits Used

Each profile analyzed during auto-swipe costs 1 credit. A full 30-profile session uses 30 credits.

| Session Size | Credits | Approximate Time |
|---|---|---|
| 10 profiles | 10 | ~1-2 minutes |
| 20 profiles | 20 | ~2-4 minutes |
| 30 profiles (max) | 30 | ~3-6 minutes |

Time estimates include random delays between actions.
