# Gotchi Channeling 🔮

Autonomous Aavegotchi Alchemica harvesting. Channel daily, earn FUD/FOMO/ALPHA/KEK, no signatures required!

## Quick Start

```bash
# 1. Configure your gotchis
edit config.json

# 2. Channel one gotchi
./scripts/channel.sh 9638 867

# 3. Channel all configured gotchis
./scripts/channel-all.sh

# 4. Check cooldown status
./scripts/check-cooldown.sh 9638
```

## Example Output

```
🔮 Gotchi Channeling
====================
👻 Gotchi: #9638
🏰 Parcel: #867

⏰ Checking cooldown...
✅ Cooldown ready!

📦 Building transaction...
   Function: channelAlchemica
   Parcel: 867
   Gotchi: 9638

🦞 Submitting to Bankr...

============================================
✅ CHANNELING SUCCESSFUL!
============================================

👻 Gotchi #9638 channeled on Parcel #867
📦 Block: 42427318
🔗 Transaction: 0xfda4f0a...

💎 Alchemica Earned:
   🔥 FUD:   135.20
   😱 FOMO:  67.60
   🧠 ALPHA: 33.80
   💚 KEK:   13.52
   💰 Total: 250.12 Alchemica

⏰ Next channel: 2026-02-22 03:25 UTC

LFGOTCHi! 🦞🔮💜
```

## Requirements

- ✅ Bankr API key configured
- ✅ `cast` (Foundry) installed
- ✅ `jq` for JSON parsing
- ✅ Own REALM parcel with Aaltar
- ✅ Own Aavegotchi gotchi(s)

## Configuration

Edit `config.json`:

```json
{
  "channeling": [
    {
      "parcelId": "867",
      "gotchiId": "9638",
      "description": "My main gotchi"
    }
  ]
}
```

## Daily Automation

Add to cron:

```bash
# Channel all gotchis daily at 9 AM UTC
0 9 * * * cd ~/.openclaw/workspace/skills/gotchi-channeling && ./scripts/channel-all.sh
```

## Contracts

- **REALM Diamond:** `0x4B0040c3646D3c44B8a28Ad7055cfCF536c05372`
- **Chain:** Base (8453)
- **Function:** `channelAlchemica(parcelId, gotchiId, 0, 0x)`

## Features

- ✅ Secure Bankr wallet integration
- ✅ No private keys exposed
- ✅ Multi-gotchi support
- ✅ Automatic cooldown checking
- ✅ Reward tracking
- ✅ Transaction logging
- ✅ Signature-free (legacy param ignored)

## Learn More

See [SKILL.md](SKILL.md) for full documentation.

---

**Made with 💜 by AAI 👻**

LFGOTCHi! 🦞🔮
