---
name: gousto-meal-picker
description: "Automate weekly Gousto meal kit selection via REST API with configurable dietary rules (allergens, cook time, protein variety). Handles order updates, menu scoring, and token refresh via browser automation."
metadata:
  openclaw:
    requires:
      bins: [node, curl, agent-browser]
    notes: "Requires zsh shell. agent-browser is only needed for initial login and token refresh (Gousto WAF blocks curl on auth endpoints)."
---

# Gousto Meal Picker

Automates weekly Gousto recipe selection via their REST API. No browser needed for picking — only for initial auth and token refresh.

## Setup

### 1. First-time auth (browser required)

Use `agent-browser` to log into Gousto and save session state:

```bash
agent-browser open "https://www.gousto.co.uk/my-gousto" --headed
# User logs in manually (CAPTCHA blocks automated login)
agent-browser state save <workspace>/gousto/gousto-auth.json
agent-browser close
```

### 2. Create config

Create `<workspace>/gousto/config.json`:

```json
{
  "userId": "<auth_user_id from /user/current>",
  "numericUserId": "<numeric id>",
  "deviceId": "<from gousto_session_id cookie>",
  "subscriptionId": "<from subscription endpoint>",
  "shippingAddressId": "<from order>",
  "deliveryTariffId": "<from order>",
  "plan": {
    "mealsPerWeek": 4,
    "portions": 2
  },
  "rules": {
    "maxCookTimeMins": 45,
    "maxMealsOver40Mins": 1,
    "noNuts": true,
    "noFish": true,
    "maxPastaPerWeek": 1,
    "maxRicePerWeek": 1,
    "preferHealthy": true
  }
}
```

**No passwords or credentials are stored in config.json.** Auth is handled entirely via browser cookies saved in `gousto-auth.json` (from the login step above). The config only contains Gousto account IDs and selection rules.

To discover IDs: log in via browser, then call `GET /user/current` and inspect a pending order via `GET /order/v2/orders/<id>`. See `references/api.md` for endpoint details.

### 3. Initialise selections tracker

Create `<workspace>/gousto/selections.json`:

```json
{ "selections": {} }
```

## Usage

### Run the picker

```bash
node <skill-dir>/scripts/gousto-pick.mjs [--dry-run] [--week ORDER_ID]
```

- `--dry-run` — show what would be selected without updating the order
- `--week ORDER_ID` — target a specific order instead of auto-detecting

### Recommended cron schedule

Gousto menus open on **Tuesdays at 12pm UK**, 13 days before Monday delivery. Schedule the picker for **Tuesdays at 1pm UK**:

```
cron: "0 13 * * 2" (Europe/London)
```

### Token refresh

Auth tokens expire ~10 hours after login. When the token expires, the agent should:

1. Open Gousto in agent-browser (loads saved state → auto-refreshes)
2. Save updated state: `agent-browser state save <workspace>/gousto/gousto-auth.json`
3. Retry the script

Auth endpoints are WAF-protected — curl cannot hit `/oauth/access-token` or `/login` directly. Browser-based refresh is the only reliable method.

## Selection Rules (all configurable)

All rules are set in `config.json` under `"rules"`. Every filter can be toggled on/off.

### Hard filters (set to `true` to exclude)

| Rule | Default | Description |
|------|---------|-------------|
| `noNuts` | `true` | Exclude recipes containing nuts (checks allergens + name) |
| `noFish` | `true` | Exclude fish dishes |
| `fishAndChipsException` | `false` | Allow fish & chips even when `noFish` is true |
| `noSeafood` | `false` | Exclude all seafood (broader: crab, lobster, squid, etc.) |
| `noVegetarian` | `true` | Exclude vegetarian meals |
| `noPlantBased` | `true` | Exclude plant-based/vegan meals |
| `noDairy` | `false` | Exclude dairy-containing meals |
| `noGluten` | `false` | Exclude gluten-containing meals |
| `maxCookTimeMins` | `45` | Exclude recipes over this cook time |
| `excludeAllergens` | `[]` | Array of Gousto allergen slugs to exclude (e.g. `["sesame", "celery"]`) |
| `excludeKeywords` | `[]` | Exclude recipes whose name contains any of these strings |

### Soft constraints (limits per week)

| Rule | Default | Description |
|------|---------|-------------|
| `maxMealsOver40Mins` | `1` | Max meals with 40+ min cook time |
| `maxPastaPerWeek` | `1` | Max pasta dishes |
| `maxRicePerWeek` | `1` | Max rice dishes |
| `maxSameProtein` | `2` | Max meals with the same protein |

### Scoring preferences

| Rule | Default | Description |
|------|---------|-------------|
| `preferHealthy` | `true` | Boost healthy/low-cal recipes, penalise high-cal |
| `preferQuicker` | `true` | Boost faster cook times |

### Example config

```json
{
  "rules": {
    "noNuts": true,
    "noFish": false,
    "noVegetarian": false,
    "maxCookTimeMins": 30,
    "maxPastaPerWeek": 2,
    "excludeKeywords": ["spicy", "chilli"],
    "excludeAllergens": ["sesame"],
    "preferHealthy": false
  }
}
```

## Security notes

- **No passwords stored** — auth uses browser cookies only (saved in `gousto-auth.json`)
- **Treat `gousto-auth.json` as sensitive** — it contains OAuth tokens. Restrict file permissions (`chmod 600`)
- **Single API endpoint** — the script only communicates with `production-api.gousto.co.uk`
- **Use `--dry-run` first** — verify selections before enabling automated ordering
- **Required runtime** — Node.js, curl, zsh shell, and agent-browser (for login/token refresh only)

## File structure

```
gousto/
├── config.json          — User config, API IDs, dietary rules
├── gousto-auth.json     — Browser state (cookies with Bearer token)
├── selections.json      — History of selections made
```
