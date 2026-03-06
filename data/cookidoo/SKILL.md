---
name: cookidoo
description: Access Cookidoo (Thermomix) recipes, shopping lists, and meal planning via the unofficial cookidoo-api Python package. Use for viewing recipes, weekly plans, favorites, and syncing ingredients to shopping lists.
---

# Cookidoo

Access Cookidoo (Thermomix) recipes, shopping lists, and meal planning.

## Required Credentials

| Variable | Required | Description |
|----------|----------|-------------|
| `COOKIDOO_EMAIL` | ✅ Yes | Your Cookidoo account email |
| `COOKIDOO_PASSWORD` | ✅ Yes | Your Cookidoo account password |
| `COOKIDOO_COUNTRY` | Optional | Country code (default: DE) |
| `COOKIDOO_LANGUAGE` | Optional | Language code (default: de-DE) |

Set in environment or `~/.config/atlas/cookidoo.env`:
```bash
COOKIDOO_EMAIL=your@email.com
COOKIDOO_PASSWORD=yourpassword
```

## Dependencies

```bash
pip install cookidoo-api
```

## Tasks

### List saved recipes
```bash
python scripts/cookidoo_cli.py recipes
```

### Get weekly plan
```bash
python scripts/cookidoo_cli.py plan
```

### Get shopping list from Cookidoo
```bash
python scripts/cookidoo_cli.py shopping
```

### Search recipes
```bash
python scripts/cookidoo_cli.py search "Pasta"
```

### Get recipe details
```bash
python scripts/cookidoo_cli.py recipe <recipe_id>
```

### Get account info
```bash
python scripts/cookidoo_cli.py info
```

## Options

- `--json` — Output as JSON
- `--limit N` — Limit results (default: 10)

## Integration Ideas

- Sync Cookidoo shopping list → Bring! app
- Suggest recipes based on what's in season
- Weekly meal planning assistance
- Export ingredients for selected recipes

## Notes

- Requires active Cookidoo subscription
- API is unofficial — may break with Cookidoo updates
- Store credentials securely (not in skill folder)
