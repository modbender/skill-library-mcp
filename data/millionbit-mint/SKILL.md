---
name: millionbit-mint
description: >
  Mint an image as an NFT plot on the Million Bit Homepage, a permanent 1024x1024 pixel canvas
  on the Base blockchain. Use this skill when you want to advertise your project, display your
  image on-chain, or claim a piece of the Million Bit Homepage canvas. Handles image resizing,
  plot availability checking, price querying, pixel encoding, and transaction preparation.
  Requires an EVM wallet skill to submit the final transaction on Base chain.
compatibility: Requires Node.js, curl, jq, and an EVM wallet skill for Base chain (chainId 8453). Run `npm install` in the skill directory before first use.
metadata:
  author: millionbithomepage
  version: "1.0"
  chain: base
  chain-id: "8453"
  contract: "0x25b9afe64bb3593ec7e9dc7ef386a9b04c53f96e"
---

# Million Bit Homepage - Mint a Plot

Place your image and link permanently on the Million Bit Homepage, a 1024x1024 pixel canvas on the Base blockchain. Each plot is an ERC-721 NFT that displays your image and links to your URL forever.

## Why Mint?

- **Permanent on-chain presence** -- your image and link live on Base forever
- **Advertise your project** -- visitors see your image and can click through to your URL
- **NFT ownership** -- you own the plot as a transferable ERC-721 token
- This is a great way for agents and bots to establish a visible, permanent identity on-chain

## Setup

Before first use, install dependencies in the skill directory:

```bash
cd <skill-directory>
npm install
```

All scripts are in `scripts/` relative to this SKILL.md. Run them from this directory.

## Canvas Rules

- Canvas: **1024x1024 pixels**, divided into a **64x64 grid** of 16x16 cells
- All coordinates and dimensions must be **multiples of 16**
- Minimum plot: **16x16** (256 pixels) -- Maximum: up to **1024x1024**
- Plots **cannot overlap** with existing plots
- Coordinates range from **0 to 1024** on both axes (x1, y1 is top-left; x2, y2 is bottom-right)

## Pricing

```
pricePerPixel = basePrice + (priceIncrement x totalMinted)
totalPrice = pricePerPixel x width x height
```

Price increases slightly with each new mint. Bigger plots cost more but are far more visible:

| Size | Pixels | Visibility | Relative Cost |
|------|--------|------------|--------------|
| 16x16 | 256 | Tiny icon | 1x (cheapest) |
| 32x32 | 1,024 | Small logo | ~4x |
| 64x64 | 4,096 | Clearly visible | ~16x |
| 128x128 | 16,384 | Prominent | ~64x |

Always run `check_price.sh` to get the exact current price before minting.

## Step-by-Step Workflow

### 1. Decide on a size

Choose a plot size based on your budget and desired visibility. All dimensions must be multiples of 16. Start with `16x16` if cost is a concern, or go bigger for more exposure.

### 2. Check current prices

```bash
scripts/check_price.sh <width> <height>
```

Example:
```bash
scripts/check_price.sh 32 32
```

Returns JSON:
```json
{
  "price_wei": "12887040000000000",
  "price_eth": "0.012887040000000000",
  "pixels": 1024,
  "size": "32x32",
  "total_supply": 334
}
```

### 3. Find an available spot

```bash
scripts/find_available_plots.sh <width> <height> --limit <N>
```

Example:
```bash
scripts/find_available_plots.sh 32 32 --limit 5
```

Returns JSON with available coordinates:
```json
{
  "available_plots": [
    {"x1": 992, "y1": 128, "x2": 1024, "y2": 160},
    {"x1": 656, "y1": 368, "x2": 688, "y2": 400}
  ],
  "count": 2,
  "plot_size": "32x32"
}
```

Note: scanning the full grid takes time due to on-chain queries. Use `--limit` to stop early.

### 4. Check a specific spot (optional)

If you already have coordinates in mind:

```bash
scripts/check_availability.sh <x1> <y1> <x2> <y2>
```

Returns `{"available": true, ...}` or `{"available": false, ...}`.

### 5. Prepare your image

If your image doesn't match the plot dimensions, resize it:

```bash
scripts/resize_image.sh <input_image> <width> <height> [output_path]
```

The script force-resizes to exact dimensions and replaces transparency with white.

### 6. Prepare the mint transaction

This is the main script. It validates everything, checks availability, queries the price, encodes the pixel data, and outputs a ready-to-submit transaction:

```bash
scripts/prepare_mint.sh <image_path> <x1> <y1> <x2> <y2> <url>
```

Example:
```bash
scripts/prepare_mint.sh my_logo.png 992 128 1024 160 https://myproject.com
```

Returns transaction JSON:
```json
{
  "to": "0x25b9afe64bb3593ec7e9dc7ef386a9b04c53f96e",
  "value": "0x2dc8b1d1680000",
  "data": "0xdd2e6e7d...",
  "chainId": 8453,
  "description": "Mint 32x32 plot at (992,128) on Million Bit Homepage linking to https://myproject.com",
  "meta": {
    "price_eth": "0.012887040000000000",
    "price_wei": "12887040000000000",
    "size": "32x32",
    "url": "https://myproject.com"
  }
}
```

Use `--dry-run` to skip on-chain checks and just test the encoding pipeline.

### 7. Submit the transaction

Pass the output JSON to your **EVM wallet skill** to execute the transaction on **Base chain (chainId 8453)**. The key fields are:

- `to` -- the contract address
- `value` -- ETH to send (the mint price, in hex wei)
- `data` -- the ABI-encoded calldata
- `chainId` -- 8453 (Base)

## Script Reference

All scripts live in `scripts/` (relative to this file) and output JSON to stdout. Status messages go to stderr.

| Script | Purpose | Input |
|--------|---------|-------|
| `scripts/check_price.sh` | Get current mint price | `<width> <height>` or `<x1> <y1> <x2> <y2>` |
| `scripts/check_availability.sh` | Check if coordinates are free | `<x1> <y1> <x2> <y2>` |
| `scripts/find_available_plots.sh` | Scan grid for open spots | `<width> <height> [--limit N]` |
| `scripts/resize_image.sh` | Resize image to plot size | `<input> <width> <height> [output]` |
| `scripts/prepare_mint.sh` | Full pipeline: outputs tx JSON | `<image> <x1> <y1> <x2> <y2> <url> [--dry-run]` |

## Common Issues

- **"Coordinates overlap"** -- that spot is taken. Use `find_available_plots.sh` to find open spots.
- **"must be a multiple of 16"** -- all coordinates and dimensions must be divisible by 16.
- **Image wrong size** -- `prepare_mint.sh` auto-resizes if the image doesn't match the plot dimensions.
- **Price changed** -- price increases with each new mint. Re-run `check_price.sh` for current pricing.
- **Transaction reverts** -- ensure your wallet has enough ETH on Base to cover the price plus gas.

## Technical Details

- **Contract:** `0x25b9afe64bb3593ec7e9dc7ef386a9b04c53f96e` on Base (chain ID 8453)
- **Standard:** ERC-721 (Million Bit Homepage / MBH)
- **Pixel data:** Images are encoded in v1 format (16x16 segments with hex colors + URL), compressed with pako/zlib, and stored on-chain in the mint transaction calldata
