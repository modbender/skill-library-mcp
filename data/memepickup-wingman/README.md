# MemePickup Wingman — Agent Skill

Compatible with: **OpenClaw** | **Manus**

Your AI wingman for dating, powered by MemePickup. Get pickup lines, reply suggestions, profile analysis, and dating coaching.

## What It Does

- **Pickup Lines** — Generate lines at different intensity levels (Sweet > Playful > Bold > Chaotic)
- **Reply Help** — Get 3 reply suggestions at different intensities for any dating conversation
- **Screenshot Analysis** — Share a conversation screenshot, get replies + wingman advice
- **Profile Analysis** — Score dating profiles against your preferences (Hinge, Tinder, Bumble, Instagram)
- **Coaching** — Timing advice, double-texting warnings, reading the room
- **Date Planning** — Personalized ideas based on your conversation context

## Setup

### 1. Get a MemePickup API Key

Open the MemePickup app on your phone:

1. Go to **Profile** > **Wingman API**
2. Tap **Generate API Key**
3. Copy the key (starts with `mp_`)

Don't have the app? Download MemePickup from the [App Store](https://apps.apple.com/app/memepickup).

### 2. Install the Skill

#### OpenClaw

```bash
npx clawhub@latest install memepickup/memepickup-wingman
```

#### Manus

Import from GitHub, upload the skill as a zip, or build from chat:

- **GitHub import:** `github.com/samcraw1/rork-memepickup-app-3` (directory: `memepickup-wingman`)
- **Zip upload:** Download this directory and upload to Manus
- **From chat:** Tell Manus to install the MemePickup Wingman skill

### 3. Add Your API Key

#### OpenClaw

Add your key to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "memepickup-wingman": {
        "enabled": true,
        "apiKey": "mp_your_api_key_here"
      }
    }
  }
}
```

Or set it as an environment variable:

```bash
export MEMEPICKUP_API_KEY="mp_your_api_key_here"
```

See `references/OPENCLAW-SETUP.md` for detailed configuration.

#### Manus

Tell Manus your API key in chat, or run in the sandbox terminal:

```bash
export MEMEPICKUP_API_KEY="mp_your_api_key_here"
```

See `references/MANUS-SETUP.md` for detailed setup including browser automation and Telegram integration.

### 4. Done

The wingman is now live. Try:

```
Give me a pickup line
```

```
Help me reply to this [screenshot]
```

```
Analyze this Hinge profile [screenshot]
```

## Credit Usage

Each action uses MemePickup credits from your account:

| Action | Credits |
|--------|---------|
| Pickup line | 1 |
| Reply suggestion (per call) | 1 |
| Screenshot analysis | 1 |
| Profile analysis | 1 |
| Coaching / nudges | 0 (local) |
| Date planning | 0 (local) |

**Free tier:** 5 lifetime credits
**Pro subscribers:** Unlimited

Upgrade to Pro in the MemePickup app for unlimited credits.

## Platform Support

Profile analysis supports platform-specific recommendations:

| Platform | Analysis | Actions |
|----------|----------|---------|
| **Hinge** | Prompts, photos, vitals | Like with comment, Rose, Skip |
| **Tinder** | Bio, photos | Swipe right/left, Superlike |
| **Bumble** | Bio, photos, badges | Swipe right/left, Superswipe |
| **Instagram** | Bio, posts, stories | Follow & DM, Follow only, Skip |

### Auto-Swipe Differences

| Capability | OpenClaw | Manus |
|---|---|---|
| How it works | Native screen interaction | Browser automation (web versions) |
| Hinge | Yes (native app) | Yes (hinge.co) |
| Tinder | Yes (native app) | Yes (tinder.com) |
| Bumble | Yes (native app) | Yes (bumble.com) |
| Instagram | Yes (native app) | No (no web dating UI) |

See `references/AUTO-SWIPE.md` for details on auto-swipe behavior, rate limits, and ban risks.

## Troubleshooting

### Both Platforms

**"Invalid or revoked API key" error?**
- Regenerate your key in MemePickup: Profile > Wingman API > Generate Key
- Make sure you're copying the full key including the `mp_` prefix

**Generic pickup lines?**
- The AI generates unique lines each time. Try adjusting intensity (0.0-1.0)

**Rate limited?**
- API is limited to 30 requests per minute
- Free tier is 5 lifetime credits. Upgrade to Pro for unlimited.

### OpenClaw

**Skill not activating?**
- Check that `MEMEPICKUP_API_KEY` is set in `~/.openclaw/openclaw.json` or as env var
- Run `openclaw skills list` to confirm the skill is loaded

### Manus

**Skill not found?**
- Re-import from GitHub or re-upload the zip
- Verify the skill appears in your Team Skill Library

**Browser automation not working?**
- Make sure you're logged into the web version of the dating app in Manus's browser
- Instagram auto-swipe is not available on Manus (no web dating interface)

**Telegram integration issues?**
- Manus Telegram agents are a new feature — availability may vary
- Fallback: use the Manus desktop app or sandbox directly

## Privacy

- Conversation data and screenshots are sent to MemePickup's API for processing and discarded after generating suggestions — not stored or used for training
- Profile screenshots are processed by OpenAI Vision and not retained
- See [MemePickup Privacy Policy](https://memepickup.com/privacy) for details

## Support

- In-app: MemePickup > Profile > Help & Support
- Email: support@memepickup.com
