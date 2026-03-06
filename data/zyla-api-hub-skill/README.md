# Zyla API Hub Skill for OpenClaw

Turn your OpenClaw AI agent into a real-world operator.
Power it with 10,000+ production-ready APIs from [Zyla API Hub](https://zylalabs.com) — instant access to weather, finance, translation, email validation, geolocation, and more, all through one unified API key, pay-as-you-go pricing, and zero vendor lock-in.

## Installation

```bash
openclaw plugins install @zyla-labs/zyla-api-hub
```

Or install via ClawHub:

```bash
clawhub install zyla-api-hub-skill
```

## Quick Setup

### Option A: Automatic (recommended)

1. Type `/zyla connect` in your OpenClaw chat
2. Browser opens to Zyla API Hub — register or log in
3. API key is captured automatically and saved to your config
4. Done! Start using APIs immediately.

### Option B: Manual

1. Visit [https://zylalabs.com/openclaw/connect](https://zylalabs.com/openclaw/connect)
2. Register or log in
3. Copy your API key
4. Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "zyla-api-hub-skill": {
        "enabled": true,
        "apiKey": "YOUR_API_KEY_HERE",
        "env": {
          "ZYLA_API_KEY": "YOUR_API_KEY_HERE"
        }
      }
    }
  }
}
```

## Usage

Just ask your agent naturally:

- "What's the weather in New York?"
- "Convert 100 USD to EUR"
- "Validate this email: test@example.com"
- "Find me a recipe API"

### Slash Commands

| Command | Description |
|---------|-------------|
| `/zyla connect` | Link your Zyla account (opens browser) |
| `/zyla status` | Check plan and usage stats |

### CLI Scripts

```bash
# Search for APIs
npx tsx scripts/zyla-catalog.ts search "weather"

# Call an API
npx tsx scripts/zyla-api.ts call --api 781 --endpoint 1234 --params '{"zip":"10001"}'

# Check health
npx tsx scripts/zyla-api.ts health
```

## Pricing

**Pay-as-you-go** — no monthly fee. You only pay per API call based on each API's rate. Billing happens at the end of each cycle via Stripe.

## Updating Popular APIs

The SKILL.md includes a "Popular APIs" section with the top 20 APIs embedded for instant access. To regenerate it from the live catalog:

```bash
npx tsx scripts/generate-popular.ts
```

Then paste the output between the `<!-- POPULAR_APIS_START -->` and `<!-- POPULAR_APIS_END -->` markers in SKILL.md.

## Development

```bash
cd openclaw-skill
npm install
npm run catalog    # Test catalog browsing
npm run api        # Test API calls
```

## License

MIT
