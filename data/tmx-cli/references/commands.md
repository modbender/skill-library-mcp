# tmx-cli — Full Command Reference

All commands support `--json` for machine-readable output.

## Table of Contents
- [search](#search)
- [recipe](#recipe)
- [plan](#plan)
- [shopping](#shopping)
- [today](#today)
- [favorites](#favorites)
- [categories](#categories)
- [status](#status)
- [cache](#cache)
- [setup](#setup)
- [login](#login)

---

## search

```bash
tmx search <query> [options]
```

| Flag | Description |
|------|-------------|
| `-n <num>` | Max results (default 10) |
| `-t <minutes>` | Max preparation time |
| `-d <level>` | Difficulty: `easy`, `medium`, `advanced` |
| `--tm <version>` | Thermomix version: `TM5`, `TM6`, `TM7` |
| `-c <category>` | Category filter (see below) |

**Categories:** vorspeisen, suppen, pasta, fleisch, fisch, vegetarisch, beilagen, desserts, herzhaft-backen, kuchen, brot, getraenke, grundrezepte, saucen, snacks

---

## recipe

| Command | Description |
|---------|-------------|
| `recipe show <id>` | Full recipe details: ingredients, steps, nutrition, timing |

---

## plan

| Command | Description |
|---------|-------------|
| `plan show` | Display current week plan |
| `plan sync` | Sync plan from Cookidoo servers |
| `plan add <id> <day>` | Add recipe to day (mon/tue/wed/thu/fri/sat/sun) |
| `plan remove <id> <day>` | Remove recipe from day ⚠️ |
| `plan move <id> <from> <to>` | Move recipe between days |

---

## shopping

| Command | Description |
|---------|-------------|
| `shopping show` | Display shopping list |
| `shopping from-plan` | Generate list from current meal plan |
| `shopping add <recipe_id>` | Add recipe ingredients to list |
| `shopping add-item "<name>" "<amount>"` | Add custom item (no recipe) |
| `shopping remove <recipe_id>` | Remove recipe ingredients |
| `shopping clear` | Clear entire list ⚠️ |
| `shopping export [--format md\|json]` | Export list (default: markdown) |

---

## today

```bash
tmx today
```
Show today's planned recipes.

---

## favorites

| Command | Description |
|---------|-------------|
| `favorites show [-n N]` | List favorites |
| `favorites add <id>` | Add recipe to favorites |
| `favorites remove <id>` | Remove from favorites |

---

## categories

| Command | Description |
|---------|-------------|
| `categories show` | List all categories |
| `categories sync` | Sync categories from Cookidoo |

---

## status

```bash
tmx status
```
Show login status, cache info, and config.

---

## cache

| Command | Description |
|---------|-------------|
| `cache clear` | Clear local cache |

---

## setup

```bash
tmx setup
```
Interactive onboarding: configure Thermomix version, diet preferences (vegetarisch, vegan, etc.), and max cooking time. Preferences auto-apply to searches.

---

## login

```bash
tmx login
```
OAuth login flow with Cookidoo account. Opens browser for authentication.

Credentials stored in `secrets/cookidoo.env` (COOKIDOO_EMAIL, COOKIDOO_PASSWORD).
