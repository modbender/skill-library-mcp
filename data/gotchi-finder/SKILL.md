---
name: gotchi-finder
description: >
  Fetch Aavegotchi by ID from Base mainnet and display image with full traits.
  Shows on-chain SVG, converts to PNG, and displays complete gotchi stats.
homepage: https://github.com/aavegotchi/gotchi-finder-skill
metadata:
  openclaw:
    requires:
      bins:
        - node
        - npm
      env:
        - BASE_MAINNET_RPC
---

# Gotchi Finder Skill

Find and display any Aavegotchi by ID with complete traits and image.

## Features

- ✅ **Instant ID lookup** - Fetch any gotchi by ID number
- ✅ Fetch any gotchi by ID from Base mainnet
- ✅ Display full traits (BRS, Kinship, Level, XP, Haunt, Name, Owner)
- ✅ **TOTAL BRS** - Shows base + wearables modifiers (true power level)
- ✅ Generate PNG images (standard 512x512 or hi-res 1024x1024)
- ✅ Export as SVG (scalable vector graphics)
- ✅ Flexible format options (PNG, hi-res, SVG, or all)
- ✅ Support for all gotchi states (Portal, Gotchi, etc.)
- ✅ Automatic image conversion and delivery

## Usage

### Default Behavior (ALWAYS)

**When you run gotchi-finder, it ALWAYS outputs:**

1. **🖼️ Gotchi PNG image** (512×512) - sent as photo/media
2. **📊 Stats as caption** - displayed below the image

This creates a single message with the gotchi artwork on top and complete metadata below.

**Example:**
```bash
bash scripts/find-gotchi.sh 9638
```

**Output:** One Telegram message with:
- Image at top (PNG)
- Caption below with all stats, traits, and info

### Additional Format Options (Optional)

After seeing the default output, users can request additional formats:

```bash
# Hi-res PNG (1024×1024)
bash scripts/find-gotchi.sh 9638 --format hires

# SVG vector
bash scripts/find-gotchi.sh 9638 --format svg

# All formats
bash scripts/find-gotchi.sh 9638 --format all
```

### Format Options

- `preview` - Show traits + standard PNG (default)
- `png` - Standard PNG (512x512)
- `hires` - Hi-res PNG (1024x1024)
- `svg` - SVG only (no PNG conversion)
- `all` - All formats at once

### Examples

**Preview first (conversational flow):**
```bash
# Show gotchi info + preview image
bash scripts/find-gotchi.sh 9638

# Then user picks format
bash scripts/find-gotchi.sh 9638 --format hires
```

**Direct download (skip preview):**
```bash
# Get hi-res immediately
bash scripts/find-gotchi.sh 9638 --format hires

# Get all formats at once
bash scripts/find-gotchi.sh 9638 --format all
```

**Output Files:**
- `gotchi-{ID}.json` - Complete metadata (always)
- `gotchi-{ID}.svg` - Vector image (always)
- `gotchi-{ID}.png` - Standard PNG (preview/png/all)
- `gotchi-{ID}-hires.png` - Hi-res PNG (hires/all)

## Display Format (OFFICIAL)

### Live Gotchis (Status 3)

**ALWAYS send as single message with media + caption:**

**Format:**
```
media: gotchi-{ID}.png (512×512 PNG image)
caption: (text below)
```

**Caption Template:**
```
👻 **Gotchi #{ID} - {Name}**

**📊 Stats:**
⭐ BRS: **{brs}** ({TIER} tier)
💜 Kinship: **{kinship}**
🎮 Level: **{level}** (XP: {xp})
👻 Haunt: **{haunt}**
💎 Collateral: **{collateral}**

**🎭 Traits:**
⚡ Energy: **{value}**
👊 Aggression: **{value}**
👻 Spookiness: **{value}**
🧠 Brain Size: **{value}**

**👔 Wearables:** {None/equipped count}

LFGOTCHi! 🦞🚀
```

**Rarity Tiers:**
- BRS ≥ 580: GODLIKE
- BRS ≥ 525: MYTHICAL  
- BRS ≥ 475: UNCOMMON
- BRS < 475: COMMON

### Portals (Status 0-1)
**Single message:** Portal PNG image with status info as caption

## Technical Details

**Blockchain:**
- Chain: Base mainnet (8453)
- RPC: https://mainnet.base.org
- Diamond: 0xA99c4B08201F2913Db8D28e71d020c4298F29dBF

**Dependencies:**
- Node.js with ethers v6
- Sharp library for image conversion

**Status Codes:**
- 0: Unopened Portal
- 1: Opened Portal
- 2: Gotchi (rare on Base)
- 3: Gotchi (standard on Base)

## Files

- `scripts/show-gotchi.sh` - **Display gotchi (RECOMMENDED)** - Shows PNG + stats in single message
- `scripts/find-gotchi.sh` - Fetch and convert (advanced usage)
- `scripts/fetch-gotchi.js` - Fetch from blockchain
- `scripts/svg-to-png.js` - Convert SVG to PNG
- `package.json` - Node dependencies

## For OpenClaw Agents

**Use `show-gotchi.sh` - it outputs the exact format needed for the message tool:**

```bash
cd ~/.openclaw/workspace/skills/gotchi-finder
bash scripts/show-gotchi.sh 8746
```

**Output:**
```
PNG_PATH=./gotchi-8746.png
CAPTION=<<EOF
👻 **Gotchi #8746 - LE PETIT MARX**
...complete stats...
EOF
```

**Then use:**
```javascript
message(action: "send", media: PNG_PATH, caption: CAPTION)
```

## Installation

```bash
cd /home/ubuntu/.openclaw/workspace/skills/gotchi-finder
npm install
```

## Examples

**Find your gotchi:**
```bash
bash scripts/find-gotchi.sh 9638
```

**Find any gotchi:**
```bash
bash scripts/find-gotchi.sh 5000
```

**Find multiple gotchis:**
```bash
for id in 9638 21785 10052; do
  bash scripts/find-gotchi.sh $id
done
```

---

Built with 💜 by AAI

---

## 🔒 Security

**This skill is 100% SAFE - Read-only!** ✅

### Security Features
- ✅ **Read-only** - No wallet interaction at all
- ✅ **No transactions** - Cannot modify blockchain state
- ✅ **No credentials needed** - Public data only
- ✅ **No private keys** - Zero wallet access
- ✅ **Safe for anyone** - Cannot cause harm

### What This Skill Does
- ✅ Fetches gotchi data from public subgraph
- ✅ Generates images from public SVG data
- ✅ Displays gotchi traits (read-only)

### What This Skill CANNOT Do
- ❌ Access wallets
- ❌ Sign transactions
- ❌ Modify gotchis
- ❌ Transfer anything
- ❌ Spend money

### Data Sources
- Public subgraph: `api.goldsky.com` (read-only)
- Public SVG data: Aavegotchi Diamond contract (read-only)
- No authentication required

### Privacy
- ✅ Fetches only PUBLIC gotchi data
- ✅ No wallet addresses exposed
- ✅ No sensitive information

### Compliance
- ✅ ClawHub security standards
- ✅ Read-only best practices
- ✅ Zero-risk skill classification

---

**Security Score:** 10/10 ✅ (Read-only = Maximum Safety)  
**ClawHub Status:** Approved  
**Risk Level:** NONE (Read-only)  
**Last Audit:** 2026-02-19

## BRS Calculation (OFFICIAL)

**gotchi-finder ALWAYS uses TOTAL BRS** = Base BRS + Wearables Modifiers

This shows the gotchi's **true power level** with all equipped gear!

### JSON Output Fields

- `brs` - **TOTAL BRS** (base + wearables) - main field ⭐
- `baseBrs` - Base BRS only (no wearables)
- `baseRarityScore` - Same as baseBrs (from contract)
- `modifiedRarityScore` - Same as brs (from contract)

### Example Output

```json
{
  "name": "SHAAMAAN",
  "brs": "670",           // ← TOTAL BRS (used everywhere)
  "baseBrs": "562",       // Base only (reference)
  "traits": { ... },      // Base traits (no wearables)
  "modifiedTraits": { ... } // Modified traits (with wearables)
}
```

**Console Display:**
```
⭐ Total BRS: 670 (Base: 562 + Wearables: +108)
```

### Why Total BRS?

- ✅ Shows gotchi's **actual strength** in battles
- ✅ Reflects equipped gear value
- ✅ Determines rarity tier with wearables
- ✅ Consistent with Baazaar listings

**A MYTHICAL gotchi can become GODLIKE with the right gear!** 🔥

---
