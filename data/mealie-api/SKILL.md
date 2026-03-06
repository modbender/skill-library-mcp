---
name: mealie
description: Interact with Mealie recipe manager (recipes, shopping lists, meal plans). Self-hosted recipe and meal planning API client.
metadata:
  openclaw:
    emoji: 🍳
    requires:
      bins: [node]
      env: [MEALIE_URL, MEALIE_API_TOKEN]
---

# Mealie Skill

API client for [Mealie](https://mealie.io), a self-hosted recipe manager and meal planner. Manage recipes, shopping lists, and meal plans.

## Environment Variables

Set these in your agent's `.env` (`~/.openclaw/.env`) or create a skill-level `.env` at `~/.openclaw/skills/mealie/.env`:

- `MEALIE_URL` — Your Mealie instance URL (e.g., `https://recipes.example.com`)
- `MEALIE_API_TOKEN` — Your API token (create at `/user/profile/api-tokens` in Mealie)

The script only reads `MEALIE_URL` and `MEALIE_API_TOKEN` from `.env` files — other variables are ignored.

## Getting an API Token

1. Log into your Mealie instance
2. Go to User Profile → API Tokens
3. Create a new token with a descriptive name
4. Copy the token to your `.env`

## Commands

### Recipes

```bash
node ~/.openclaw/skills/mealie/scripts/mealie.js recipes              # List all recipes
node ~/.openclaw/skills/mealie/scripts/mealie.js recipe <slug>        # Get recipe details
node ~/.openclaw/skills/mealie/scripts/mealie.js search "query"       # Search recipes
node ~/.openclaw/skills/mealie.js create-recipe <url>                 # Import recipe from URL
node ~/.openclaw/skills/mealie.js delete-recipe <slug>                # Delete recipe
```

### Shopping Lists

```bash
node ~/.openclaw/skills/mealie/scripts/mealie.js lists                # List shopping lists
node ~/.openclaw/skills/mealie.js list <id>                           # Show list items
node ~/.openclaw/skills/mealie.js add-item <listId> "item" [qty]      # Add item
node ~/.openclaw/skills/mealie.js check-item <listId> <itemId>        # Mark checked
node ~/.openclaw/skills/mealie.js uncheck-item <listId> <itemId>      # Mark unchecked
node ~/.openclaw/skills/mealie.js delete-item <listId> <itemId>       # Delete item
```

### Meal Plans

```bash
node ~/.openclaw/skills/mealie/scripts/mealie.js mealplan [days]      # Show meal plan (default 7 days)
node ~/.openclaw/skills/mealie.js add-meal <date> <recipeSlug> [meal] # Add meal to plan
node ~/.openclaw/skills/mealie.js delete-meal <planId>                # Remove meal from plan
```

### Other

```bash
node ~/.openclaw/skills/mealie.js stats                               # Show statistics
node ~/.openclaw/skills/mealie.js tags                                # List all tags
node ~/.openclaw/skills/mealie.js categories                          # List all categories
```

## Examples

```bash
# List all recipes
node ~/.openclaw/skills/mealie/scripts/mealie.js recipes

# Search for pasta recipes
node ~/.openclaw/skills/mealie/scripts/mealie.js search "pasta"

# Get a specific recipe
node ~/.openclaw/skills/mealie/scripts/mealie.js recipe spaghetti-carbonara

# Add milk to shopping list
node ~/.openclaw/skills/mealie/scripts/mealie.js add-item abc123 "Milk" "1 gallon"

# Show this week's meal plan
node ~/.openclaw/skills/mealie/scripts/mealie.js mealplan 7

# Add a recipe to Tuesday's dinner
node ~/.openclaw/skills/mealie/scripts/mealie.js add-meal 2026-02-17 chicken-tacos dinner
```

## API Details

- Uses Bearer token authentication
- All endpoints are under `/api/`
- Pagination is supported on list endpoints (use `--page` and `--per-page` flags)
- Recipe slugs are URL-friendly identifiers (e.g., `spaghetti-carbonara`)

Based on [Mealie API docs](https://docs.mealie.io).
