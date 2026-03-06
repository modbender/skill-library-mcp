# Cookidoo Skill for OpenClaw

Access Cookidoo (Thermomix) recipes, shopping lists, and meal planning via the unofficial [cookidoo-api](https://pypi.org/project/cookidoo-api/) Python package.

## Installation

### Via ClawHub
```bash
clawhub install @thekie/cookidoo
```

### Manual
Copy the skill folder to `~/.openclaw/skills/cookidoo/`

## Required Credentials

| Variable | Required | Description |
|----------|----------|-------------|
| `COOKIDOO_EMAIL` | ✅ Yes | Your Cookidoo account email |
| `COOKIDOO_PASSWORD` | ✅ Yes | Your Cookidoo account password |
| `COOKIDOO_COUNTRY` | Optional | Country code (default: DE) |
| `COOKIDOO_LANGUAGE` | Optional | Language code (default: de-DE) |

Set credentials in environment or create `~/.config/atlas/cookidoo.env`:
```bash
COOKIDOO_EMAIL=your@email.com
COOKIDOO_PASSWORD=yourpassword
```

## Dependencies

```bash
pip install cookidoo-api
```

## Usage

### List saved recipes
```bash
python scripts/cookidoo_cli.py recipes
```

### Search recipes
```bash
python scripts/cookidoo_cli.py search "Pasta"
```

### Get recipe details
```bash
python scripts/cookidoo_cli.py recipe <recipe_id>
```

### Get shopping list
```bash
python scripts/cookidoo_cli.py shopping
```

### Options
- `--json` — Output as JSON
- `--limit N` — Limit results (default: 10)

## Notes

- Requires an active Cookidoo subscription
- Uses the unofficial cookidoo-api — may break with Cookidoo updates
- Store credentials securely, never commit them to git

## License

MIT
