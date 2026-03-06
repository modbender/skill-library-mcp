---
name: gotchi-channeling
description: Autonomous Aavegotchi Alchemica channeling via Bankr wallet. Daily harvesting from your Aaltar installation on your REALM parcels. No signature required - secure, automated, and frenly!
homepage: https://github.com/aaigotchi/gotchi-channeling
metadata:
  openclaw:
    requires:
      bins:
        - cast
        - jq
        - curl
      env:
        - BANKR_API_KEY
    primaryEnv: BANKR_API_KEY
---

# Gotchi Channeling 🔮

Autonomous Alchemica harvesting for your Aavegotchi parcels. Daily channeling automation that's secure, simple, and signature-free!

## What is Channeling?

**Alchemical Channeling** lets your Aavegotchi harvest Alchemica (FUD, FOMO, ALPHA, KEK) from the Gotchiverse atmosphere using an Aaltar installation on your REALM parcel.

**Rewards:** 20-70+ FUD, 10-35+ FOMO, 5-17+ ALPHA, 2-7+ KEK per channel
**Cooldown:** 24 hours per gotchi
**Requirements:** Aaltar installation, parcel ownership

## Features

✅ **Daily autonomous channeling** - Set it and forget it
✅ **Bankr wallet integration** - No private keys exposed
✅ **Multi-gotchi support** - Channel all your gotchis
✅ **Smart cooldown checking** - Won't waste gas on blocked txs
✅ **Signature-free** - No backend API needed (legacy param ignored)
✅ **Transaction tracking** - Full logs and history
✅ **Reminder system** - Optional notifications

## How It Works

1. **Check cooldown** - Reads last channeled timestamp from contract
2. **Build transaction** - Creates calldata for `channelAlchemica()`
3. **Submit via Bankr** - Secure wallet handles signing & submission
4. **Harvest Alchemica** - FUD, FOMO, ALPHA, KEK minted to your wallet
5. **Wait 24h** - Cooldown resets, ready for next channel

## Setup

### 1. Configure Your Parcels & Gotchis

Create `~/.openclaw/workspace/skills/gotchi-channeling/config.json`:

```json
{
  "realmDiamond": "0x4B0040c3646D3c44B8a28Ad7055cfCF536c05372",
  "rpcUrl": "https://mainnet.base.org",
  "chainId": 8453,
  "channeling": [
    {
      "parcelId": "867",
      "gotchiId": "9638",
      "description": "entry-instead-social + aaigotchi"
    }
  ],
  "enableReminders": true,
  "reminderHourUTC": 9
}
```

**Multiple gotchis example:**

```json
{
  "realmDiamond": "0x4B0040c3646D3c44B8a28Ad7055cfCF536c05372",
  "rpcUrl": "https://mainnet.base.org",
  "chainId": 8453,
  "channeling": [
    {
      "parcelId": "867",
      "gotchiId": "9638",
      "description": "Parcel #867 + Gotchi #9638"
    },
    {
      "parcelId": "867",
      "gotchiId": "10052",
      "description": "Parcel #867 + Gotchi #10052"
    },
    {
      "parcelId": "1234",
      "gotchiId": "21785",
      "description": "Parcel #1234 + Gotchi #21785"
    }
  ]
}
```

### 2. Verify Bankr Configuration

```bash
# Check Bankr is configured
cat ~/.openclaw/skills/bankr/config.json

# Should contain:
# {
#   "apiKey": "your-bankr-api-key"
# }
```

### 3. Test Single Channel

```bash
# Channel one gotchi manually
cd ~/.openclaw/workspace/skills/gotchi-channeling
./scripts/channel.sh 9638 867
```

## Usage

### Manual Channeling

**Single gotchi:**
```bash
channel.sh <gotchi-id> <parcel-id>
channel.sh 9638 867
```

**Check if ready:**
```bash
check-cooldown.sh <gotchi-id>
check-cooldown.sh 9638
```

**Channel all configured gotchis:**
```bash
channel-all.sh
```

### Conversational Interface

**Simple commands:**
```
User: "Channel my gotchi"
AAI: ✅ Gotchi #9638 channeled on Parcel #867!
     Earned: 135.20 FUD, 67.60 FOMO, 33.80 ALPHA, 13.52 KEK
     Next channel: 2026-02-22 03:25 UTC

User: "Channel all gotchis"
AAI: 👻 Channeling all configured gotchis...
     ✅ #9638 → 250.12 Alchemica
     ⏰ #10052 → Wait 8h 23m
     ✅ #21785 → 187.45 Alchemica
     
     Total harvested: 437.57 Alchemica

User: "When can I channel?"
AAI: 👻 Channeling Status:
     #9638 → Ready now! ✅
     #10052 → Ready in 3h 42m
     #21785 → Ready in 15h 8m
```

### Automated Daily Channeling

**Set up cron job:**

```bash
# Channel all gotchis daily at 9 AM UTC
0 9 * * * cd ~/.openclaw/workspace/skills/gotchi-channeling && ./scripts/channel-all.sh >> /tmp/channeling.log 2>&1
```

**Or use OpenClaw scheduler:**
```bash
# Add to your workspace cron config
{
  "schedule": "0 9 * * *",
  "task": "cd ~/.openclaw/workspace/skills/gotchi-channeling && ./scripts/channel-all.sh",
  "description": "Daily Gotchi channeling at 9 AM UTC"
}
```

## Contract Details

### REALM Diamond (Base)
**Address:** `0x4B0040c3646D3c44B8a28Ad7055cfCF536c05372`

### Function: channelAlchemica

```solidity
function channelAlchemica(
    uint256 _realmId,      // Parcel ID (e.g., 867)
    uint256 _gotchiId,     // Gotchi ID (e.g., 9638)
    uint256 _lastChanneled, // Last channel timestamp (pass 0)
    bytes memory _signature // Legacy param - IGNORED (pass 0x)
) external whenNotPaused gameActive
```

**Parameters:**
- `_realmId` - Your REALM parcel token ID
- `_gotchiId` - Your Aavegotchi token ID
- `_lastChanneled` - Pass `0` (contract will validate)
- `_signature` - Pass `0x` (legacy param, now ignored)

**Cooldown:** 24 hours (43200 seconds)

**Requirements:**
- Must own the parcel (or have access rights)
- Aaltar must be equipped on parcel
- 24 hours must have passed since last channel
- Gotchi must exist and you must own it

### Alchemica Token Addresses (Base)

- **FUD:** `0x2028b4043e6722ea164946c82fe806c4a43a0ff4`
- **FOMO:** `0xa32137bfb57d2b6a9fd2956ba4b54741a6d54b58`
- **ALPHA:** `0x15e7cac885e3730ce6389447bc0f7ac032f31947`
- **KEK:** `0xe52b9170ff4ece4c35e796ffd74b57dec68ca0e5`

## Reward Calculation

Alchemica amount depends on your gotchi's **Kinship score**.

**Formula:**
```
baseAmount = parcelBonus + aaltarLevel
actualAmount = baseAmount * (kinship / 100)
```

**Typical rewards per channel:**
- **FUD:** 135.20 (20-70 range)
- **FOMO:** 67.60 (10-35 range)
- **ALPHA:** 33.80 (5-17 range)
- **KEK:** 13.52 (2-7 range)

**Total:** ~250 Alchemica tokens per channel

**Maximize rewards:**
- ✅ Keep kinship high (pet your gotchi daily!)
- ✅ Upgrade your Aaltar installation
- ✅ Choose parcels with Alchemica boosts

## Scripts

### channel.sh
Single gotchi channeling with full output

**Usage:**
```bash
./scripts/channel.sh <gotchi-id> <parcel-id>
```

**Output:**
- Checks cooldown
- Builds transaction
- Submits via Bankr
- Shows reward amounts
- Displays transaction hash

### channel-all.sh
Batch channel all configured gotchis

**Usage:**
```bash
./scripts/channel-all.sh
```

**Features:**
- Reads from config.json
- Checks each gotchi cooldown
- Skips if not ready
- Batches ready gotchis
- Shows summary report

### check-cooldown.sh
Query on-chain cooldown status

**Usage:**
```bash
./scripts/check-cooldown.sh <gotchi-id>
```

**Output:**
```
👻 Gotchi #9638 Channeling Status
==================================
Last channeled: 2026-02-21 03:25:17 UTC
Next available: 2026-02-22 03:25:17 UTC
Time remaining: 0h 0m (Ready! ✅)
```

### channel-status.sh
Multi-gotchi status dashboard

**Usage:**
```bash
./scripts/channel-status.sh
```

**Output:**
```
🔮 Gotchi Channeling Status
============================

#9638 (Parcel #867)
✅ Ready to channel!
Last: 24h 12m ago

#10052 (Parcel #867)
⏰ Wait 3h 42m
Last: 20h 18m ago

#21785 (Parcel #1234)
⏰ Wait 15h 8m
Last: 8h 52m ago

Summary: 1 ready, 2 waiting
```

## Troubleshooting

**"Access Right - Only Owner"**
- You must own the parcel or have access rights
- Check parcel ownership on BaseScan
- Verify you're using the correct wallet

**"Gotchi can't channel yet"**
- 24 hour cooldown hasn't passed
- Use `check-cooldown.sh` to see exact time
- Wait until cooldown completes

**"Must equip Altar"**
- Your parcel needs an Aaltar installation
- Check installations on https://gv3d.gotchiverse.io/
- Equip an Aaltar before channeling

**"Transaction failed"**
- Check you have ETH for gas on Base
- Verify contract address is correct
- Ensure Bankr wallet is funded

**"No Alchemica received"**
- Check transaction on BaseScan
- Look for Transfer events
- Verify token balances in your wallet

## Security

✅ **Bankr-only integration** - No private keys used
✅ **Secure transaction signing** - Remote signing by Bankr
✅ **No key exposure** - Keys never loaded into memory
✅ **API key authentication** - Protected Bankr access
✅ **Read-only cooldown checks** - Safe on-chain queries
✅ **Transaction logging** - Full audit trail

## Monitoring

**Check channeling history:**
```bash
# View recent channels
cat /tmp/channeling.log | tail -50

# Count successful channels
grep "SUCCESS" /tmp/channeling.log | wc -l

# Calculate total Alchemica harvested
grep "Earned:" /tmp/channeling.log | awk '{sum+=$2} END {print sum " total Alchemica"}'
```

**Track token balances:**
```bash
# Check Alchemica balances
./scripts/check-balances.sh
```

## FAQ

**Q: How often can I channel?**
A: Once every 24 hours per gotchi.

**Q: Do I need different parcels for different gotchis?**
A: No! Multiple gotchis can channel from the same parcel (each has its own 24h cooldown).

**Q: What if I have multiple Aaltars?**
A: Each Aaltar has its own cooldown. You can configure multiple parcel+gotchi combinations.

**Q: Does the signature parameter matter?**
A: No! It's a legacy parameter that's now ignored. Always pass `0x`.

**Q: Can I channel someone else's gotchi?**
A: No. You must own both the parcel and the gotchi (or have access rights).

**Q: What happens to the Alchemica?**
A: It's minted directly to your wallet as ERC20 tokens on Base.

**Q: How much does it cost?**
A: ~$0.01-0.05 in gas per channel (Base has low fees).

**Q: Can I automate this?**
A: Yes! Use cron or OpenClaw scheduler for daily automation.

## Changelog

### v1.0.0 (2026-02-21)
- ✅ Initial release
- ✅ Signature-free channeling (legacy param ignored)
- ✅ Bankr wallet integration
- ✅ Multi-gotchi support
- ✅ Automated daily channeling
- ✅ Cooldown checking
- ✅ Transaction logging
- ✅ Reward tracking

## Support

- **Contract:** 0x4B0040c3646D3c44B8a28Ad7055cfCF536c05372
- **Chain:** Base (8453)
- **Docs:** https://docs.gotchiverse.io/
- **Discord:** https://discord.gg/aavegotchi

---

**Made with 💜 by AAI 👻**

*Channel your way to Alchemica riches!*

LFGOTCHi! 🦞🔮💎
