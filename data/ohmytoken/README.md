# ohmytoken

> Your AI spending, visualized as pixel art. In real-time.

![ohmytoken](https://ohmytoken.dev/preview.png)

OpenClaw skill that turns your LLM token consumption into a mesmerizing pixel bead board at [ohmytoken.dev](https://ohmytoken.dev).

## Install

```bash
openclaw skill install @0x5446/ohmytoken
```

## Configure

Get your free API key at [ohmytoken.dev](https://ohmytoken.dev), then add to `openclaw.json`:

```json
{
  "skills": {
    "ohmytoken": {
      "config": { "api_key": "omt_your_key_here" }
    }
  }
}
```

That's it. Open [ohmytoken.dev](https://ohmytoken.dev) and watch the beads drop.

## Features

- Every model gets a unique color (Claude=coral, GPT=green, Gemini=blue...)
- 7 board shapes including a cat head
- 10 achievements to unlock
- Leaderboards, gallery, share cards with QR codes
- Daily/monthly/yearly views
- Embeddable SVG badges for GitHub READMEs

## Links

- [ohmytoken.dev](https://ohmytoken.dev) — Dashboard
- [GitHub](https://github.com/0x5446/ohmytoken-oss) — Source code
