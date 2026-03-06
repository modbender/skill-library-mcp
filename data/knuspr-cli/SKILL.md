---
name: knuspr
description: Manage grocery shopping on Knuspr.de via the knuspr-cli. Use for product search, cart management, delivery slot reservation, shopping lists, order history, deals, favorites, and meal suggestions. Trigger when the user mentions Knuspr, groceries, Einkauf, Lebensmittel, Warenkorb, Lieferslot, or shopping list tasks.
---

# Knuspr CLI Skill

Interact with Knuspr.de (German grocery delivery) using `knuspr-cli` — a pure-Python CLI bundled in this skill at `{baseDir}/knuspr_cli.py`.

## Setup

1. **Python 3.8+** required (no external dependencies)
2. **Login**: `python3 {baseDir}/knuspr_cli.py auth login` (or set `KNUSPR_EMAIL` + `KNUSPR_PASSWORD` env vars)
3. **Minimum order**: €39

## Critical Rules

1. **NEVER complete a purchase** — Only build cart + reserve slot. Always tell the user to review and checkout themselves via `cart open` or the Knuspr website/app.
2. **Always use `--json`** for parsing output programmatically.
3. **Confirm before destructive actions** (cart clear, list delete, slot release).
4. **Show prices and totals** when adding to cart so the user stays informed.

## CLI Usage

```
python3 {baseDir}/knuspr_cli.py <resource> <action> [options]
```

## Core Workflows

### Search & Add to Cart
```bash
# Search products (use --json for parsing)
python3 {baseDir}/knuspr_cli.py product search "Hafermilch" --json
python3 {baseDir}/knuspr_cli.py product search "Käse" --bio --sort price_asc --json
python3 {baseDir}/knuspr_cli.py product search "Joghurt" --rette --json  # discounted items

# Add to cart
python3 {baseDir}/knuspr_cli.py cart add <product_id> -q <quantity>
python3 {baseDir}/knuspr_cli.py cart show --json  # verify cart & total
```

### Delivery Slots
```bash
python3 {baseDir}/knuspr_cli.py slot list --detailed --json  # show available slots with IDs
python3 {baseDir}/knuspr_cli.py slot reserve <slot_id>       # reserve a 15-min ON_TIME slot
python3 {baseDir}/knuspr_cli.py slot reserve <slot_id> --type VIRTUAL  # 1-hour window
python3 {baseDir}/knuspr_cli.py slot current --json          # check current reservation
python3 {baseDir}/knuspr_cli.py slot release                 # cancel reservation (ask first!)
```

### Shopping Lists
```bash
python3 {baseDir}/knuspr_cli.py list show --json             # all lists
python3 {baseDir}/knuspr_cli.py list show <list_id> --json   # products in a list
python3 {baseDir}/knuspr_cli.py list create "Wocheneinkauf"
python3 {baseDir}/knuspr_cli.py list add <list_id> <product_id>
python3 {baseDir}/knuspr_cli.py list to-cart <list_id>       # move entire list to cart
python3 {baseDir}/knuspr_cli.py list duplicate <list_id>     # duplicate a list
```

### Order History & Reorder
```bash
python3 {baseDir}/knuspr_cli.py order list --json
python3 {baseDir}/knuspr_cli.py order show <order_id> --json
python3 {baseDir}/knuspr_cli.py order repeat <order_id>      # add all items to cart
```

## Full Command Reference

For all commands, options, and flags see `{baseDir}/references/commands.md`.
