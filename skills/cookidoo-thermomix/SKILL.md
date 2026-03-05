---
name: cookidoo
description: >
  Interact with Cookidoo (Thermomix recipe platform) via the unofficial cookidoo-api.
  Search recipes, manage meal planning calendar, shopping lists, collections, and custom recipes.
  Use when the user mentions "Cookidoo", "Thermomix recipes", "meal planning", "Wochenplan",
  "Einkaufsliste Thermomix", "Cookidoo Rezepte", "was kochen", or wants to manage their
  Thermomix/Cookidoo account programmatically.
---

# Cookidoo Integration

Unofficial integration with the Cookidoo platform (Vorwerk/Thermomix) using the
[cookidoo-api](https://github.com/miaucl/cookidoo-api) Python library.

## Setup

No external dependencies — uses only Python stdlib (urllib, json). Works with Python 3.7+.

### Environment variables (required)

```
COOKIDOO_EMAIL=user@example.com
COOKIDOO_PASSWORD=secret
```

### Optional config

```
COOKIDOO_COUNTRY=ch        # Default: ch (Switzerland)
COOKIDOO_LANGUAGE=de-CH    # Default: de-CH
```

Supported countries/languages: run `get_country_options()` / `get_language_options()` from the library.

## CLI Script

All operations via `scripts/cookidoo.py`:

```bash
python scripts/cookidoo.py <command> [args]
```

### Commands

| Command | Description |
|---|---|
| `login` | Test credentials, show user info |
| `user-info` | Get account info |
| `subscription` | Check active subscription status |
| `recipe <id>` | Get recipe details (e.g. `r59322`) |
| `calendar [date]` | Show meal plan for week (default: today) |
| `calendar-add <date> <id> [...]` | Add recipe(s) to calendar (date: YYYY-MM-DD) |
| `calendar-remove <date> <id>` | Remove recipe from calendar |
| `shopping-list` | Show full shopping list (ingredients + additional items) |
| `shopping-add <id> [...]` | Add recipe ingredients to shopping list |
| `shopping-remove <id> [...]` | Remove recipe ingredients from shopping list |
| `shopping-clear` | Clear entire shopping list |
| `additional-items` | List additional (manual) shopping items |
| `additional-add <item> [...]` | Add manual items to shopping list |
| `additional-remove <id> [...]` | Remove additional items by ID |
| `collections` | List custom and managed collections |
| `collection-add <name>` | Create custom collection |
| `collection-remove <id>` | Delete custom collection |

### Recipe IDs

Recipe IDs look like `r59322` or `r907015`. Find them on cookidoo.ch/de URLs or via the API.

## Authentication

The API uses OAuth password grant (same as the Thermomix app). Tokens refresh automatically per session. No API key needed — just Cookidoo account credentials.

## Limitations

- No official API — based on reverse-engineering the Android app
- Recipe search not directly exposed in the library (browse on cookidoo.ch and extract IDs)
- Some features require an active Cookidoo Premium subscription (custom recipes, etc.)
- Rate limiting: be gentle, avoid rapid bulk requests
