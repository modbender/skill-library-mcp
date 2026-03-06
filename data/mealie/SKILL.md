---
name: mealie
description: Interact with a self‑hosted Mealie instance (recipe manager & meal planner) via its REST API. Use for adding, updating, retrieving recipes, meal plans and generating shopping lists. Trigger when the user mentions their Mealie URL, wants to import a recipe, create a meal plan or fetch a shopping list.
---

# Mealie Skill

## When to use
- The user provides a Mealie base URL (e.g., `https://mealie.example.com`) and/or an API token and asks to add/import a recipe, create or modify a meal plan, fetch a shopping list, or query existing recipes.
- The user wants to automate meal‑planning tasks from the command line or through a script.

## Required environment variables
```bash
export MEALIE_URL="https://mealie.example.com"   # base URL of the instance
export MEALIE_TOKEN="<your‑jwt‑api‑token>"       # bearer token obtained from Mealie UI (Settings → API Keys)
```
Both variables must be set in the shell where the skill runs.

## Provided script
The skill bundles a small Bash helper (`scripts/mealie.sh`) that wraps the most common Mealie API calls using `curl`.

```bash
#!/usr/bin/env bash
# mealie.sh – simple wrapper for Mealie REST API
# Requires MEALIE_URL and MEALIE_TOKEN env vars
set -euo pipefail

cmd=$1; shift
case "$cmd" in
  add-recipe)
    # Usage: mealie.sh add-recipe <path‑to‑json>
    curl -s -X POST "$MEALIE_URL/api/recipes" \
      -H "Authorization: Bearer $MEALIE_TOKEN" \
      -H "Content-Type: application/json" \
      --data @${1}
    ;;
  get-recipe)
    # Usage: mealie.sh get-recipe <recipe‑id>
    curl -s "$MEALIE_URL/api/recipes/${1}" \
      -H "Authorization: Bearer $MEALIE_TOKEN" | jq '.'
    ;;
  create-plan)
    # Usage: mealie.sh create-plan <json‑payload>
    curl -s -X POST "$MEALIE_URL/api/mealplan" \
      -H "Authorization: Bearer $MEALIE_TOKEN" \
      -H "Content-Type: application/json" \
      --data @${1}
    ;;
  get-shopping)
    # Usage: mealie.sh get-shopping <plan‑id>
    curl -s "$MEALIE_URL/api/mealplan/${1}/shopping-list" \
      -H "Authorization: Bearer $MEALIE_TOKEN" | jq '.'
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    exit 1
    ;;
esac
```
Make it executable:
```bash
chmod +x scripts/mealie.sh
```

## How to use from the chat
You can ask me to run a specific operation, e.g.:
- "Add this recipe to Mealie." → I will ask you for the JSON representation of the recipe and then run `scripts/mealie.sh add-recipe`.
- "Show me the shopping list for my current week plan." → I will call `scripts/mealie.sh get-shopping <plan‑id>` and return the formatted list.
- "Search for a recipe called *Spaghetti Bolognese*." → I will query the API (`GET /api/recipes?search=Spaghetti%20Bolognese`) and return matches.

## Extending the skill
If you need additional endpoints (e.g., tags, categories, batch import), just add new case blocks to `mealie.sh` or create separate scripts under `scripts/` and reference them in this README.

---

**Note:** The skill does not store the API token in any file; it relies on the environment variables you provide. Keep the token secret and rotate it regularly via the Mealie UI.
