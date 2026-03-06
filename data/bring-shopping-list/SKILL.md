---
name: bring-shopping-list
description: Use when asked about the shopping list, groceries, "add to shopping list", "what's on the list", "remove from list", or any shopping/grocery related request. Integrates with the Bring! shopping list app.
argument-hint: "[add|remove|list] [items...]"
user-invocable: false
metadata:
  openclaw:
    requires:
      env:
        - BRING_EMAIL
        - BRING_PASSWORD
      bins:
        - uv
    primaryEnv: BRING_EMAIL
---

# Bring! Shopping List

Manage a Bring! shopping list — add items, remove items, mark items as completed, and check what's on the list.

## Setup

1. Install [uv](https://docs.astral.sh/uv/) if not already installed
2. Set environment variables for your Bring! account:
   ```bash
   export BRING_EMAIL="your-email@example.com"
   export BRING_PASSWORD="your-password"
   ```
   Or add them to a `.env` file in your project root.

> If you use Google login for Bring!, go to your Bring! account settings and set a separate password first.

## Usage

All commands use `bring.py` in this skill's directory. Adjust the path based on where you installed the skill.

### With uv (recommended)

```bash
uv run --with bring-api --with python-dotenv python bring.py list --json
uv run --with bring-api --with python-dotenv python bring.py add "Milk" "Eggs" "Butter:Irish"
uv run --with bring-api --with python-dotenv python bring.py remove "Milk"
uv run --with bring-api --with python-dotenv python bring.py complete "Eggs"
```

### With pip

```bash
pip install -r requirements.txt
python bring.py list --json
python bring.py add "Milk" "Eggs" "Butter:Irish"
python bring.py remove "Milk"
python bring.py complete "Eggs"
```

## Handling Requests

1. Parse the user's message for:
   - Items to add ("add milk and eggs to the list")
   - Items to remove ("remove milk from the list")
   - Checking the list ("what's on the shopping list?")
   - Item details/specs ("milk, but low fat" -> `Milk:low fat`)

2. Run the appropriate CLI command

3. Confirm the action naturally

## Notes

- Requires `BRING_EMAIL` and `BRING_PASSWORD` environment variables
- Items can have optional specs via colon syntax: `name:specification`
- Uses the first (default) shopping list in the account
- Dependencies (`bring-api`, `python-dotenv`) are handled inline by `uv run --with`, or via `pip install -r requirements.txt`
