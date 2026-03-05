---
name: cookidoo
description: Manage Thermomix/Cookidoo meal planning via tmx-cli. Use for recipe search, weekly meal plan management, shopping list generation, favorites, and recipe details. Trigger when the user mentions Cookidoo, Thermomix, Wochenplan, meal plan, Rezept, recipe, or Einkaufsliste for cooking.
---

# Cookidoo / tmx-cli Skill

Manage Cookidoo® (Thermomix) meal plans, recipes, and shopping lists using `tmx-cli` — a pure-Python CLI bundled in this skill at `{baseDir}/tmx_cli.py`.

## Setup

1. **Python 3.9+** required (no external dependencies)
2. **Login**: `python3 {baseDir}/tmx_cli.py login` (OAuth flow with Cookidoo account)
3. **Setup** (optional): `python3 {baseDir}/tmx_cli.py setup` — configure TM version, diet preferences, max cooking time

## Critical Rules

1. **Confirm before destructive actions** (shopping clear, plan remove).
2. **Use `--json`** when parsing output programmatically.
3. **Respect user preferences** — setup config auto-applies to searches.

## CLI Usage

```
python3 {baseDir}/../tmx-cli/tmx_cli.py <resource> <action> [options]
```

## Core Workflows

### Search Recipes
```bash
tmx search "Pasta" --json
tmx search "Kuchen" -n 20 --json              # more results
tmx search "Suppe" -t 30 --json               # max 30 min prep time
tmx search "Salat" -d easy -c vegetarisch --json  # easy + vegetarian
```

Filters: `-t <minutes>`, `-d easy|medium|advanced`, `--tm TM5|TM6|TM7`, `-c <category>`

Categories: vorspeisen, suppen, pasta, fleisch, fisch, vegetarisch, beilagen, desserts, herzhaft-backen, kuchen, brot, getraenke, grundrezepte, saucen, snacks

### Recipe Details
```bash
tmx recipe show <recipe_id> --json   # ingredients, steps, nutrition
```

### Meal Plan
```bash
tmx plan show --json                 # current week plan
tmx plan sync                        # sync from Cookidoo
tmx plan add <recipe_id> <day>       # add recipe (day: mon/tue/wed/thu/fri/sat/sun)
tmx plan remove <recipe_id> <day>    # remove from plan
tmx plan move <recipe_id> <from> <to>  # move between days
```

### Shopping List
```bash
tmx shopping show --json             # current list
tmx shopping from-plan               # generate from meal plan
tmx shopping add <recipe_id>         # add recipe ingredients
tmx shopping add-item "Milch" "1L"   # add custom item
tmx shopping remove <recipe_id>      # remove recipe ingredients
tmx shopping clear                   # clear entire list ⚠️
tmx shopping export                  # export as markdown
tmx shopping export --format json    # export as JSON
```

### Today's Recipes
```bash
tmx today --json                     # what's on the plan today
```

### Favorites
```bash
tmx favorites show --json
tmx favorites add <recipe_id>
tmx favorites remove <recipe_id>
```

## Full Command Reference

For all commands, options, and flags see `{baseDir}/references/commands.md`.
