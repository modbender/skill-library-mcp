---
name: apo-cli
description: Search and order pharmacy products from apohealth.de via apo-cli. Use for medication search (by name or PZN), product details, category browsing, and cart management. Trigger when the user mentions Apotheke, pharmacy, Medikament, medication, PZN, apohealth, or health products.
---

# apohealth.de / apo-cli Skill

Search pharmacy products and manage cart on apohealth.de using `apo-cli` — a pure-Python CLI bundled in this skill at `{baseDir}/apo_cli.py`.

## Setup

1. **Python 3.9+** required (no external dependencies)
2. No login needed — apohealth.de works without authentication

## Critical Rules

1. **NEVER complete a purchase** — Only build cart. User must checkout themselves.
2. **Always provide the cart URL** when interacting via chat: `https://www.apohealth.de/cart/<variant_id>:<qty>,<variant_id>:<qty>,...` — the user cannot open a browser from the agent, so they need a clickable link.
3. **Confirm before destructive actions** (cart clear).
4. **Show prices** when adding to cart so the user stays informed.
5. **PZN search** — Users may provide a PZN (Pharmazentralnummer) directly; pass it as the search query.

## CLI Usage

```
python3 {baseDir}/apo_cli.py <resource> <action> [options]
```

## Core Workflows

### Search Products
```bash
python3 {baseDir}/apo_cli.py search "Ibuprofen 400"       # by name
python3 {baseDir}/apo_cli.py search "04114918"             # by PZN
python3 {baseDir}/apo_cli.py search "Nasenspray" -n 20     # more results
```

### Product Details
```bash
python3 {baseDir}/apo_cli.py product <handle>   # prices, variants, description
```

### Browse Categories
```bash
python3 {baseDir}/apo_cli.py categories                        # list all
python3 {baseDir}/apo_cli.py list --category bestseller         # browse category
python3 {baseDir}/apo_cli.py list --category schmerzen -n 10    # with limit
```

### Cart
```bash
python3 {baseDir}/apo_cli.py cart                    # show cart
python3 {baseDir}/apo_cli.py cart add <variant_id>   # add product
python3 {baseDir}/apo_cli.py cart remove <variant_id> # remove product
python3 {baseDir}/apo_cli.py cart clear              # clear cart ⚠️
python3 {baseDir}/apo_cli.py cart checkout           # open browser for checkout
```

### Status
```bash
python3 {baseDir}/apo_cli.py status                  # CLI status info
```

## Full Command Reference

For all commands, options, and flags see `{baseDir}/references/commands.md`.
