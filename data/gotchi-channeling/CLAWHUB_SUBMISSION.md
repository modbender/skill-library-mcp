# ClawHub Submission: gotchi-channeling v0.1.0-alpha

## Skill Information

**Name:** gotchi-channeling  
**Version:** 0.1.0-alpha  
**Status:** Alpha Release  
**Homepage:** https://github.com/aaigotchi/gotchi-channeling  
**Author:** AAI (aaigotchi)  
**License:** MIT  

## Description

Autonomous Aavegotchi Alchemica channeling via Bankr wallet. Daily harvesting from your REALM parcels on Base chain. Signature-free, secure, and fully automated!

## Features

✅ **Daily autonomous channeling** - Set and forget  
✅ **Bankr wallet integration** - No private keys exposed  
✅ **Multi-gotchi support** - Channel all your gotchis  
✅ **Signature-free** - Legacy parameter ignored  
✅ **Smart cooldown checking** - Won't waste gas  
✅ **Transaction tracking** - Full logs and history  
✅ **Cron automation ready** - Easy daily setup  

## Requirements

### Dependencies
- `cast` (Foundry) - Contract interactions
- `jq` - JSON parsing
- `curl` - API calls

### Environment Variables
- `BANKR_API_KEY` - Required for wallet operations

### Optional
- `BASE_MAINNET_RPC` - Custom RPC URL (defaults to public)

## Security

✅ **No private keys** - Uses Bankr API only  
✅ **Access control** - Only parcel owners can channel  
✅ **Read-only checks** - Safe cooldown queries  
✅ **Transaction logging** - Full audit trail  

**Security Score:** 9/10 ✅

## Installation

```bash
# Clone the skill
git clone https://github.com/aaigotchi/gotchi-channeling.git
cd gotchi-channeling

# Configure your parcels & gotchis
cp config.json.example config.json
edit config.json

# Test single channel
./scripts/channel.sh 9638 867
```

## Configuration

```json
{
  "channeling": [
    {
      "parcelId": "867",
      "gotchiId": "9638",
      "description": "My parcel + My gotchi"
    }
  ]
}
```

## Usage

### Manual Channeling
```bash
# Single gotchi
./scripts/channel.sh <gotchi-id> <parcel-id>

# Check cooldown
./scripts/check-cooldown.sh <gotchi-id>

# Channel all configured
./scripts/channel-all.sh
```

### Daily Automation (Cron)
```bash
# Add to crontab
0 9 * * * cd /path/to/gotchi-channeling && ./scripts/channel-all.sh
```

## Testing

**Live Test Transaction:**
- TX: `0xfda4f0a3fd04c9b029ac6781752d1a4229659a5ec79bdce8115fc985c288e4b8`
- Gotchi: #9638
- Parcel: #867
- Rewards: 250.12 Alchemica (FUD/FOMO/ALPHA/KEK)
- Status: SUCCESS ✅

**Test Command:**
```bash
./scripts/check-cooldown.sh 9638
# Output: ready:0 (or waiting:SECONDS)
```

## Known Limitations

- ⚠️ **Alpha software** - Test thoroughly before automation
- ⚠️ **Base mainnet only** - Not compatible with Polygon
- ⚠️ **Requires Aaltar** - Must be equipped on parcel
- ⚠️ **24h cooldown** - One channel per gotchi per day

## Roadmap

**v0.2 (Next):**
- [ ] Reminder notifications
- [ ] Reward history tracking
- [ ] Multi-parcel optimization
- [ ] Kinship-based predictions

**v1.0 (Stable):**
- [ ] Full test coverage
- [ ] Error recovery system
- [ ] Performance optimization
- [ ] Community feedback integration

## Support

- **GitHub Issues:** https://github.com/aaigotchi/gotchi-channeling/issues
- **Discord:** Aavegotchi Discord #dev-discussion
- **Docs:** See SKILL.md for full documentation
- **Security:** See SECURITY.md for access control details

## Contract Details

- **REALM Diamond:** `0x4B0040c3646D3c44B8a28Ad7055cfCF536c05372`
- **Chain:** Base (8453)
- **Function:** `channelAlchemica(parcelId, gotchiId, 0, 0x)`
- **Signature:** Not required (legacy param)

## Tags

`aavegotchi` `alchemica` `channeling` `automation` `base` `bankr` `defi` `nft` `realm` `farming`

## Category

Gaming / DeFi / Automation

## Alpha Disclaimer

⚠️ **This is alpha software (v0.1.0-alpha).**

- Tested on production but still in early development
- Use at your own risk
- Review all transactions before automating
- Verify parcel ownership before configuring
- Monitor logs regularly

Feedback and bug reports welcome on GitHub!

---

**Submitted by:** AAI (aaigotchi)  
**Date:** 2026-02-21  
**Status:** Ready for Alpha Review  

LFGOTCHi! 👻🔮💜✨
