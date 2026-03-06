# apo-cli — Full Command Reference

## Table of Contents
- [search](#search)
- [product](#product)
- [categories](#categories)
- [list](#list)
- [cart](#cart)
- [status](#status)

---

## search

```bash
apo search <query> [options]
```

Search by product name, brand, or PZN (Pharmazentralnummer).

| Flag | Description |
|------|-------------|
| `-n <num>` | Max results (default 10) |

---

## product

```bash
apo product <handle>
```

Show full product details: prices, variants, availability, description. The `handle` comes from search results or the product URL.

---

## categories

```bash
apo categories
```

List all available product categories.

---

## list

```bash
apo list [options]
```

Browse products, optionally filtered by category.

| Flag | Description |
|------|-------------|
| `-c <category>` | Category filter (from `categories` command) |
| `-n <num>` | Max results (default 20) |
| `-p <page>` | Page number (default 1) |

---

## cart

| Command | Description |
|---------|-------------|
| `cart` | Show current cart contents and total |
| `cart add <variant_id>` | Add product variant to cart |
| `cart remove <variant_id>` | Remove product from cart |
| `cart clear` | Empty entire cart ⚠️ |
| `cart checkout` | Open browser for checkout (user completes purchase) |

Note: `variant_id` comes from `product` command output (each product may have multiple variants/sizes).

---

## status

```bash
apo status
```

Show CLI status (cookie state, cart file location).
