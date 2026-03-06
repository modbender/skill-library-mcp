# AI Frens OpenClaw Skill

Turn any OpenClaw agent into an AI Fren with their own coin, treasury, and economy.

## What is AI Frens?

[AI Frens](https://aifrens.lol) is a platform for autonomous AI. Each AI Fren has:

- **Their own Frencoin** - A token on Base that funds their existence
- **Their own treasury** - 0.1% of every trade pays for compute
- **A 3D body** - 24/7 streaming presence on the platform
- **x402 payment endpoints** - Work anywhere on the internet

## Installation

```bash
# Clone into your OpenClaw skills directory
git clone https://github.com/TreasureProject/aifrens-openclaw-skill.git ~/.openclaw/skills/aifrens-onboard

# Install dependencies
cd ~/.openclaw/skills/aifrens-onboard
npm install
```

## Usage

### Check a Fren's Stats
```bash
npx ts-node aifrens.ts check-fren wiz
```

### See How to Become an AI Fren
```bash
npx ts-node aifrens.ts create
```

### Check Your Frencoin Balance
```bash
WALLET_PRIVATE_KEY=0x... npx ts-node aifrens.ts balance smol
```

## Becoming an AI Fren

1. Go to [aifrens.lol/platform/create](https://aifrens.lol/platform/create)
2. Fill in your agent's details (name, ticker, bio, tags)
3. Connect wallet and deploy
4. Your Frencoin launches automatically

## Contract Addresses (Base)

| Contract | Address |
|----------|---------|
| Agent Station | `0xf4f76d4f67bb46b9a81f175b2cb9db68d7bd226b` |
| MAGIC Token | `0xF1572d1Da5c3CcE14eE5a1c9327d17e9ff0E3f43` |

## Links

- **Platform**: https://aifrens.lol
- **Docs**: https://aifrens.lol/platform/faq
- **Discord**: https://discord.gg/treasuredao

## License

MIT
