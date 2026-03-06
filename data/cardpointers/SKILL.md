---
name: cardpointers
description: "Query CardPointers card recommendations, wallet cards, and offers via the CardPointers CLI. Use when the user asks about which credit card to use for a purchase or category, listing their cards or wallet, viewing or filtering or searching card offers, checking expiring offers, comparing cards across linked profiles, or any credit card rewards optimization question. Requires a CardPointers+ (Pro) subscription."
homepage: https://cardpointers.com/cli/
metadata: {"clawdbot":{"emoji":"💳","requires":{"bins":["cardpointers","jq"]},"install":[{"id":"brew","kind":"brew","formula":"cardpointers/tap/cardpointers","bins":["cardpointers"],"label":"Install cardpointers (brew)"},{"id":"jq","kind":"brew","formula":"jq","bins":["jq"],"label":"Install jq (brew)"}]}}
---

# CardPointers CLI

Query your CardPointers wallet — cards, offers, recommendations — from the terminal.

## Setup

- **Config:** `~/.cardpointers/config` (JWT token, auto-created on login)
- **Requires:** `curl`, `jq`, `bash`
- **Auth:** Run `cardpointers login` to authenticate (email/password or browser-based Apple/Google/passkey)

## Commands

### recommend — Best card for a purchase

```bash
cardpointers recommend groceries
cardpointers recommend "gas stations"
cardpointers recommend --merchant amazon
cardpointers recommend -m "whole foods" --amount 150
cardpointers recommend gas -p all        # best gas card across all profiles
```

### cards — List wallet cards

```bash
cardpointers cards                       # approved cards (default)
cardpointers cards --status all          # all statuses
cardpointers cards --bank chase          # filter by bank
cardpointers cards -b amex -s all -l 5  # combine filters + limit
```

### offers — List and filter offers

```bash
cardpointers offers                          # active offers
cardpointers offers -s redeemed              # redeemed offers
cardpointers offers --expiring               # expiring within 7 days
cardpointers offers -e 14                    # expiring within 14 days
cardpointers offers --bank amex              # filter by bank
cardpointers offers --card "gold"            # filter by card name
cardpointers offers --category dining        # filter by category
cardpointers offers --type personal          # personal offers only
cardpointers offers --favorite               # favorited offers only
cardpointers offers --sort value --limit 10  # top 10 by value
```

### search — Search offers by keyword

```bash
cardpointers search "whole foods"
cardpointers search "streaming" --favorite
cardpointers search "gas" --limit 5
```

### profiles — List linked profiles

```bash
cardpointers profiles
```

### Utility

```bash
cardpointers status    # account info + connection test
cardpointers ping      # test MCP connection
cardpointers tools     # list available MCP tools
cardpointers login     # authenticate
cardpointers logout    # clear saved token
cardpointers --version # print version
```

## Global Options

All data commands accept these flags:

| Flag | Description |
|------|-------------|
| `--profile, -p` | Query by profile: number (`-p 2`), name (`-p caroline`), or `all`/`any` |
| `--limit, -l` | Cap number of results |
| `--json, -j` | Raw JSON output (for scripting / AI agents) |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CARDPOINTERS_API` | Override API base URL (default: `https://mcp.cardpointers.com`) |
| `CARDPOINTERS_DEBUG` | Set to `1` for verbose output |
| `NO_COLOR` | Disable ANSI colors |

## Reference

- **Card statuses:** approved, applied, denied, closed, all
- **Offer statuses:** active, snoozed, redeemed, expired, expiring_soon, all
- **Offer bank filter (enum):** amex, chase, citi, boa, usbank, wellsfargo
- **Card bank filter:** freeform text (partial match)
- **Offer sort options:** expiring, value, card
- **Cards include** `approval_date` (YYYY-MM-DD)

## Common Use Cases

- "What card should I use at Costco?" → `recommend -m costco`
- "Show my Amex cards" → `cards -b amex`
- "Offers expiring this week?" → `offers -e 7`
- "Any Whole Foods offers?" → `search "whole foods"`
- "Best dining card across all profiles?" → `recommend dining -p all`
- "Top 5 offers by value" → `offers --sort value -l 5`
- "Show redeemed offers as JSON" → `offers -s redeemed -j`
