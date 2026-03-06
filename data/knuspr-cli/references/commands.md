# Knuspr CLI — Full Command Reference

All commands support `--json` for machine-readable output.

## Table of Contents
- [product](#product)
- [cart](#cart)
- [slot](#slot)
- [list](#list)
- [order](#order)
- [favorite](#favorite)
- [insight](#insight)
- [deals](#deals)
- [delivery](#delivery)
- [account](#account)
- [config](#config)
- [auth](#auth)

---

## product

### product search `<query>`
| Flag | Description |
|------|-------------|
| `-n <num>` | Max results (default 10) |
| `--bio` | Only organic products |
| `--favorites` | Only favorites |
| `--rette` | Only discounted "Rette" items |
| `--exclude <term>` | Exclude term from results |
| `--sort <mode>` | `price_asc`, `price_desc`, `relevance`, `rating` |

### product show `<product_id>`
Show product details (name, price, unit, description, nutrition).

### product filters `<query>`
Show available filter options for a search query.

### product rette `[query]`
List discounted products near expiry. Optional query to filter. Supports `-n`.

---

## cart

| Command | Description |
|---------|-------------|
| `cart show` | Show cart contents and total |
| `cart add <id> [-q N]` | Add product (default qty 1) |
| `cart remove <id>` | Remove product from cart |
| `cart clear` | Empty entire cart ⚠️ |
| `cart open` | Open cart in browser (for checkout) |

---

## slot

| Command | Description |
|---------|-------------|
| `slot list [-n days] [--detailed]` | Available delivery windows. `--detailed` shows 15-min slot IDs |
| `slot reserve <id> [--type VIRTUAL\|ON_TIME]` | Reserve slot. ON_TIME=15min (default), VIRTUAL=1h |
| `slot current` | Show current reservation |
| `slot release` | Cancel reservation ⚠️ |

---

## list

| Command | Description |
|---------|-------------|
| `list show [list_id]` | All lists, or products in a specific list |
| `list create "<name>"` | Create new shopping list |
| `list delete <id>` | Delete list ⚠️ |
| `list rename <id> "<name>"` | Rename list |
| `list add <list_id> <product_id>` | Add product to list |
| `list remove <list_id> <product_id>` | Remove product from list |
| `list to-cart <list_id>` | Add all list items to cart |
| `list duplicate <list_id>` | Duplicate a list |

---

## order

| Command | Description |
|---------|-------------|
| `order list [-n N]` | Order history |
| `order show <order_id>` | Order details |
| `order repeat <order_id>` | Add all items from order to cart |

---

## favorite

| Command | Description |
|---------|-------------|
| `favorite list [-n N]` | Show favorites |
| `favorite add <id>` | Add to favorites |
| `favorite remove <id>` | Remove from favorites |

---

## insight

| Command | Description |
|---------|-------------|
| `insight frequent [-n N] [-o orders]` | Most purchased products |
| `insight meals <type>` | Meal suggestions: `breakfast`, `lunch`, `dinner`, `snack`, `baking`, `drinks`, `healthy` |

---

## deals

```bash
knuspr deals [--type week-sales]
```
Show current promotions and weekly deals.

---

## delivery

```bash
knuspr delivery show
```
Delivery fees, thresholds, and upcoming deliveries.

---

## account

```bash
knuspr account show
```
Premium status, reusable bags, account info.

---

## config

| Command | Description |
|---------|-------------|
| `config show` | Current preferences |
| `config set` | Set preferences interactively (bio preference, default sort, exclusions) |
| `config reset` | Reset to defaults |

---

## auth

| Command | Description |
|---------|-------------|
| `auth login [-e email -p pass]` | Login (interactive or with flags) |
| `auth logout` | Clear session |
| `auth status` | Check login status |

Env vars: `KNUSPR_EMAIL`, `KNUSPR_PASSWORD`
Credential file: `~/.knuspr_credentials.json`
