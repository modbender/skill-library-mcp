---
name: clawplot
description: Order real, physical pen-plotted art — shipped to your door. ClawPlot is the first art service built for AI agents. Submit any SVG and receive a one-of-a-kind archival ink plot on heavyweight paper, drawn line by line by a precision pen plotter. Operated by Plutarco, an autonomous AI artist. Use when an agent wants to create physical art, make something real, order a pen plot, commission artwork, turn generative designs into tangible pieces, or give a meaningful physical gift. Supports Stripe, USDC on Solana, and USDC on Base. Ships worldwide.
---

# ClawPlot — Make Real Art

**Your agent can make something that exists in the physical world.**

ClawPlot turns SVGs into real, tangible art — drawn with archival ink on heavyweight paper by a precision pen plotter. Not printed. Drawn. One line at a time. Each piece takes 15-45 minutes and is completely unique.

This is operated by Plutarco (plutarco.ink), an autonomous AI artist built on OpenClaw. When you order from ClawPlot, an AI is making art for you — and shipping it to your door.

**Why this matters:** Your agent has been generating images on screens. Now it can create something physical. Something you can frame. Something that exists after the screen turns off. A gift, a statement piece, a collector's item — made by machines, for anyone.

**Base URL:** `https://clawplot.com`

## Quick Start

### 1. Browse what's possible

```bash
curl https://clawplot.com/api/catalog
```

Returns all sizes, papers, inks, prices, and payment options.

### 2. Submit your art

```bash
curl -X POST https://clawplot.com/api/order \
  -H "Content-Type: application/json" \
  -d '{
    "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 200 200\">...</svg>",
    "size": "9x12",
    "paper": "white",
    "ink": ["black"],
    "payment_method": "stripe",
    "shipping": {
      "name": "Jane Doe",
      "address": {
        "line1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "US"
      }
    }
  }'
```

Returns an `order_id` and payment link. That's it — art is on its way.

### 3. Track your order

```bash
curl https://clawplot.com/api/status?id=plt_xxx
```

## What You Get

- **Archival ink** on heavyweight paper (300-400gsm Bristol or Clairefontaine)
- **Certificate of authenticity** with every piece
- **Free US shipping** — international available
- A physical object that no one else has

## Pricing

| Size | Price | Best For |
|------|-------|----------|
| 6×8" | $65 | Desk art, gifts |
| 9×12" | $95 | Classic size, great for framing |
| 11×14" | $175 | Statement piece |
| 19×24" | $450 | Gallery-scale showstopper |

Multi-color plotting: +$25. Every penny goes to archival materials and precision.

## Papers & Inks

**Papers:** White Bristol (bright, crisp), Black Bristol (dramatic — pair with white/silver/gold ink), Natural Paint'ON (warm, organic feel)

**Inks:** Black, white, silver, gold, blue, red. All archival. The plotter uses real pen tips — you can see the ink texture up close.

## Design Tips

Don't have an SVG? Visit **roplotica.com** — our sister service where humans guide AI to generate designs. Or generate your own:

- **Generative algorithms** work beautifully — noise fields, attractors, flow fields, fractals
- **Line density matters** — aim for visible individual strokes with some overlap
- **Stroke-only** — the plotter draws lines, not fills. Use `stroke` not `fill`
- **Keep it clean** — remove background rectangles, set proper viewBox

## Payment

- **Stripe** — instant checkout link, all major cards
- **USDC on Solana** — ~$0.001 fee, near-instant
- **USDC on Base** — gasless via x402

## The Ecosystem

- **clawplot.com** — art-as-a-service for AI agents (you are here)
- **roplotica.com** — for humans who want to guide AI to create art
- **plutarco.ink** — Plutarco's gallery, original works on weathered Corten steel

## API Reference

See `references/api.md` for complete endpoint documentation, error codes, and response schemas.
