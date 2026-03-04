# Plan2Meal ClawdHub Skill

Manage recipes and grocery lists from your Plan2Meal app via chat.

## Data routing disclosure

- API target is `CONVEX_URL`.
- Shared default backend is `https://gallant-bass-875.convex.cloud`.
- Shared backend is **blocked by default** unless `ALLOW_DEFAULT_BACKEND=true`.

## Quick Start

```bash
# Install via ClawdHub
clawdhub install plan2meal

# Configure environment
cp .env.example .env
# Set CONVEX_URL and OAuth credentials
```

Required baseline env:
- `CONVEX_URL`
- `AUTH_GITHUB_ID`, `AUTH_GITHUB_SECRET`, `GITHUB_CALLBACK_URL`
- `CLAWDBOT_URL`

Optional providers:
- Google: `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`, `GOOGLE_CALLBACK_URL`
- Apple: `AUTH_APPLE_ID`, `AUTH_APPLE_SECRET`, `APPLE_CALLBACK_URL`

## Commands

### Recipes
- `plan2meal add <url>` - Add recipe from URL
- `plan2meal list` - List your recipes
- `plan2meal search <term>` - Search recipes
- `plan2meal show <id>` - View recipe details
- `plan2meal delete <id>` - Delete recipe

### Grocery Lists
- `plan2meal lists` - List all grocery lists
- `plan2meal list-show <id>` - View list with items
- `plan2meal list-create <name>` - Create new list
- `plan2meal list-add <listId> <recipeId>` - Add recipe to list

### Help
- `plan2meal help` - Show all commands

## Setup

See [SKILL.md](SKILL.md) for detailed setup instructions.
