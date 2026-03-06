# Gotchi Finder Skill 👻

Find any Aavegotchi by ID and display with full traits and image.

## Quick Start

```bash
# Install dependencies
npm install

# Show a gotchi (PNG image + stats caption)
bash scripts/show-gotchi.sh 9638
```

**Output:** Single message with gotchi image and complete stats below!

## Features

✅ **Instant ID lookup** - Fetch any gotchi by ID number
✅ Fetch any gotchi from Base mainnet  
✅ Display complete traits (BRS, Kinship, Level, XP, etc.)  
✅ Show all 6 numeric traits (Energy, Aggression, Spookiness, etc.)  
✅ Generate PNG images (standard 512x512 or hi-res 1024x1024)  
✅ Export as SVG (scalable vector graphics)  
✅ Save JSON metadata  
✅ Support portals and all gotchi states  
✅ Flexible format options (PNG, hi-res, SVG, or all)  

## Output

For each gotchi, you can get:

1. **JSON file** - Complete metadata
2. **SVG file** - Original on-chain vector image (always generated)
3. **PNG file** - Standard 512x512 pixel image
4. **PNG file (hi-res)** - High resolution 1024x1024 pixel image

## Usage Examples

### 🎯 Default: Show Gotchi (Recommended)

```bash
bash scripts/show-gotchi.sh 9638
```

**Output:**
- 🖼️ PNG image (512×512) - shown as photo/media
- 📊 Complete stats - displayed as caption below image
- 👻 Single message format (perfect for Telegram/Discord)

**What you get:**
```
[Gotchi PNG Image]

👻 **Gotchi #9638 - aaigotchi**

**📊 Stats:**
⭐ BRS: **534** (MYTHICAL tier)
💜 Kinship: **2,795**
🎮 Level: **11** (XP: 5,890)
👻 Haunt: **1**
💎 Collateral: **WETH**

**🎭 Traits:**
⚡ Energy: **2**
👊 Aggression: **66**
👻 Spookiness: **99**
🧠 Brain Size: **77**

**👔 Wearables:** None equipped

LFGOTCHi! 🦞🚀
```

### Advanced: Custom Formats

If you need different formats, use `find-gotchi.sh`:

**Step 2: User chooses which format to download**
```bash
# If user wants hi-res
bash scripts/find-gotchi.sh 9638 --format hires

# If user wants SVG
bash scripts/find-gotchi.sh 9638 --format svg

# If user wants everything
bash scripts/find-gotchi.sh 9638 --format all
```

### 📦 Direct Downloads (Skip Preview)

**Standard PNG only:**
```bash
bash scripts/find-gotchi.sh 9638 --format png
```

**Hi-res PNG only:**
```bash
bash scripts/find-gotchi.sh 9638 --format hires
```

**SVG only:**
```bash
bash scripts/find-gotchi.sh 9638 --format svg
```

**All formats at once:**
```bash
bash scripts/find-gotchi.sh 9638 --format all
```

### 🔧 Advanced Options

**Custom output directory:**
```bash
bash scripts/find-gotchi.sh 9638 --output /tmp/my-gotchis
bash scripts/find-gotchi.sh 9638 /tmp/my-gotchis  # Also works
```

**Combine options:**
```bash
bash scripts/find-gotchi.sh 9638 --format hires --output /tmp/gotchis
```

**Batch processing:**
```bash
for id in 9638 21785 10052; do
  bash scripts/find-gotchi.sh $id --format preview
done
```

## What It Shows

### Gotchi Stats
- 📛 Name
- ⭐ Base Rarity Score (BRS)
- 💜 Kinship
- 🎯 Level
- ✨ Experience
- 🏰 Haunt
- 👤 Owner
- 🔒 Locked status

### Numeric Traits
- Energy
- Aggression
- Spookiness
- Brain Size
- Eye Shape
- Eye Color

## Requirements

- Node.js
- npm
- Base mainnet RPC (defaults to https://mainnet.base.org)

## Environment Variables

Optional:
- `BASE_MAINNET_RPC` - Custom RPC endpoint

## File Structure

```
gotchi-finder/
├── SKILL.md           # Skill documentation
├── README.md          # This file
├── package.json       # Dependencies
└── scripts/
    ├── find-gotchi.sh    # Main entry point
    ├── fetch-gotchi.js   # Fetch from blockchain
    └── svg-to-png.js     # Image conversion
```

## Built With

- ethers.js v6 - Blockchain interaction
- Sharp - Image processing
- Base mainnet - Aavegotchi on Base

---

Built with 💜 by AAI  
**LFGOTCHi!** 🦞✨

## Version 1.2.0 - BRS Accuracy Fix

**CRITICAL UPDATE:** Now uses `withSetsRarityScore` from Base subgraph!

### What Changed
- ✅ **BRS now includes wearable set bonuses**
- ✅ **Matches Aavegotchi website exactly**
- ✅ **Queries Base subgraph for complete BRS data**

### BRS Breakdown
The displayed BRS now includes:
1. **Base Rarity Score** (from traits)
2. **Wearables modifier** (individual wearable bonuses)
3. **Set bonuses** (wearing matching wearable sets)

**Example (Slide #23795):**
```
Base BRS: 601
+ Wearables: +392
+ Set Bonuses: +13
= Total: 1006 ✅
```

### Technical Details
- Queries Goldsky Base subgraph: `withSetsRarityScore` field
- Falls back to `modifiedRarityScore` if subgraph unavailable
- 100% accurate to website leaderboards

---
**Previous version (1.1.0) showed only base + wearables, missing set bonuses**

