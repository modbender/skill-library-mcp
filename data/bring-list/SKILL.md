---
name: bring-list
description: "Manage Bring! shopping lists (Einkaufsliste / grocery list) — add, remove, check off items, batch ops, default list support. Use when: user wants to set up Bring!, add items to shopping list, check what's on the list, or complete/remove items. Full guided setup in Telegram: agent handles login, list selection and config entirely in chat. Privacy-first: credentials via chat or private terminal input — your choice, never repeated. Terminal optional."
---

# Bring! Shopping Lists

Manage Bring! shopping lists via the unofficial REST API. Requires `curl` and `jq`.

## Agent Setup Guide

When a user asks you to set up or use Bring for the first time, follow these steps:

### Step 1: Check if already configured
Run `scripts/bring.sh lists` first. If it works, setup is already done — skip to usage.

### Step 2: Set up credentials
Bring! requires an email + password. If the user doesn't have an account yet, they can create one for free at getbring.com or in the Bring! app.

**If they signed up via Google/Apple:** They need to set a direct password first in the Bring! app (Settings → Account → Change Password) before the API works.

Ask the user how they'd like to provide their credentials:

> "I need your Bring! email and password. You can either share them here in chat (I'll write them to a config file and never mention them again), or if you prefer to keep them out of the chat entirely, I can give you a terminal command to enter them privately. Which do you prefer?"

**Option A — via chat (convenient):**
User shares email + password in chat. Write them directly to the config file using `jq` for safe JSON encoding (prevents injection via special characters) and do not echo them back:
```bash
mkdir -p ~/.config/bring
jq -n --arg e "USER_EMAIL" --arg p "USER_PASSWORD" '{email: $e, password: $p}' > ~/.config/bring/credentials.json
chmod 600 ~/.config/bring/credentials.json
```
After writing, confirm: "Done — credentials saved securely. I won't repeat them."

**Option B — via terminal (more private):**
Give the user this command to run in their own terminal. Credentials never appear in chat:
```bash
mkdir -p ~/.config/bring
read -rp "Bring! Email: " BEMAIL
read -rsp "Bring! Password: " BPASS && echo
jq -n --arg e "$BEMAIL" --arg p "$BPASS" '{email: $e, password: $p}' > ~/.config/bring/credentials.json
chmod 600 ~/.config/bring/credentials.json
unset BEMAIL BPASS
```
Tell the user: "Run that in your terminal, then come back and I'll continue the setup."

**⚠️ Do NOT use `scripts/bring.sh setup`** — it requires an interactive terminal (TTY) which agents don't have. Always create the credentials file manually as shown in Step 3.

### Step 3: Save credentials and test login
```bash
mkdir -p ~/.config/bring
jq -n --arg e "USER_EMAIL" --arg p "USER_PASSWORD" '{email: $e, password: $p}' > ~/.config/bring/credentials.json
chmod 600 ~/.config/bring/credentials.json
scripts/bring.sh login
```
If login fails: double-check email/password. The user may need their Bring! password (not Google/Apple SSO — Bring requires a direct account password).

### Step 4: Show existing lists and ask for a default
```bash
scripts/bring.sh lists
```
This shows all the user's Bring! lists. The user may have multiple lists, e.g.:
- Einkaufsliste (main grocery list)
- Drogerie (drugstore items)
- Baumarkt (hardware store)
- A shared list with a partner/family

**If the user has NO lists:** Tell them to create one in the Bring! app first. The API does not support creating or deleting lists — this must be done in the app. Once they've created a list, continue with setup.

**Ask the user which list should be the default.** This lets them skip typing the list name every time.

If they have only ONE list: set it as default automatically and inform them.
If they have MULTIPLE lists: show the list names and ask which one to use as default. Explain they can still target other lists by name (e.g., "Put nails on the Baumarkt list").

### Step 5: Set default list
Update the credentials file to include the chosen default:
```bash
# Read existing config and add default_list
jq --arg list "CHOSEN_LIST_NAME" '. + {default_list: $list}' ~/.config/bring/credentials.json > /tmp/bring_conf.json && mv /tmp/bring_conf.json ~/.config/bring/credentials.json
chmod 600 ~/.config/bring/credentials.json
```

### Step 6: Confirm setup
Show the user their current list content to confirm everything works:
```bash
scripts/bring.sh show
```
Tell them: "All set! You can now say things like 'Put milk on the list' or 'What's on the shopping list?'"

### Important: Lists can only be managed in the app
The Bring! API does not support creating or deleting lists. If the user asks to create a new list or delete one, tell them:
"Lists can only be created and deleted in the Bring! app. Once you've made the change there, I can immediately work with the new list."

### Handling shared lists
Bring! lists are often shared between family members or partners. Changes made by the agent sync instantly to all devices sharing that list. Inform the user:
- "Any items I add will show up immediately on all phones that share this list."
- This is usually desired (e.g., partner sees the updated grocery list), but worth mentioning.

## Setup (manual / reference)

Credentials via env vars `BRING_EMAIL` + `BRING_PASSWORD`, or config file `~/.config/bring/credentials.json`:

```json
{"email": "user@example.com", "password": "secret", "default_list": "Einkaufsliste"}
```

Interactive setup (TTY required): `scripts/bring.sh setup`

## Commands

All commands accept a list name (partial match) or UUID. If `default_list` is configured, the list argument can be omitted.

```bash
# List all shopping lists
scripts/bring.sh lists

# Show items on a list (or default list)
scripts/bring.sh show
scripts/bring.sh show "Einkaufsliste"

# Add item (with optional specification/quantity)
scripts/bring.sh add "Milch" "fettarm, 1L"
scripts/bring.sh add "Einkaufsliste" "Milch" "fettarm, 1L"

# Add multiple items at once (use "item|spec" for specifications)
scripts/bring.sh add-multi "Brot" "Käse|Gouda" "Butter|irische"

# Complete/check off item (moves to recently purchased)
scripts/bring.sh complete "Milch"

# Complete multiple items at once
scripts/bring.sh complete-multi "Milch" "Brot" "Käse"

# Move item back from recently to purchase list
scripts/bring.sh uncomplete "Milch"

# Remove item entirely
scripts/bring.sh remove "Milch"

# Remove multiple items at once
scripts/bring.sh remove-multi "Milch" "Brot" "Käse"
```

## Targeting specific lists

When the user has multiple lists, they can target a specific one by name:
- "Put nails on the **Baumarkt** list" → `scripts/bring.sh add "Baumarkt" "Nails"`
- "What's on the **Drogerie** list?" → `scripts/bring.sh show "Drogerie"`

List names support partial case-insensitive matching, so "einkauf" matches "Einkaufsliste".

If no list is specified, the `default_list` from the config is used.

## JSON Output

Append `--json` to `lists` and `show` for raw JSON:

```bash
scripts/bring.sh lists --json
scripts/bring.sh show --json
scripts/bring.sh show "Einkaufsliste" --json
```

## Notes

- Specifications are the small description text under an item (e.g., quantity, brand)
- `complete` moves items to "recently purchased" (like checking off in the app)
- `remove` deletes items entirely from the list
- Token is cached at `~/.cache/bring/token.json` and auto-refreshed
- Changes sync instantly to all devices sharing the list
- Item names with special characters (quotes, umlauts, emoji) are fully supported
- Bring! requires a direct account password — Google/Apple SSO logins don't work with the API
- `country` in credentials.json controls the item catalog language (default: `DE`)
- When showing items to the user, consider only showing the "TO BUY" section unless they specifically ask for recently completed items — the recently list can be very long
- If `remove` fails with "not found", suggest the user check the exact item name with `show`
- **Creating/deleting lists is not supported by the Bring! API** — users must manage lists in the Bring! app
