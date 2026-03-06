---
name: fatsecret
description: FatSecret nutrition API integration for food search, nutritional lookup, barcode scanning, recipe search, and food diary logging. Use when user needs to find nutritional information for foods, search the food database, scan product barcodes, look up calories/macros/micronutrients, search for healthy recipes, or log meals to their FatSecret diary.
metadata:
  credentials:
    required:
      - name: FATSECRET_CONSUMER_KEY
        description: FatSecret API Consumer Key (get from platform.fatsecret.com)
      - name: FATSECRET_CONSUMER_SECRET
        description: FatSecret API Consumer Secret
    optional:
      - name: FATSECRET_PROXY
        description: SOCKS5 proxy URL if FatSecret requires IP whitelisting (e.g., socks5://127.0.0.1:1080)
      - name: FATSECRET_CONFIG_DIR
        description: Custom config directory (default ~/.config/fatsecret). Use for persistent storage in containers.
---

# FatSecret Nutrition API

Complete integration with FatSecret for food data lookup AND diary logging.

## ⚠️ Authentication Methods

This skill supports **two authentication methods** for different use cases:

| Method | Use Case | User Login Required | Capabilities |
|--------|----------|---------------------|--------------|
| **OAuth2** (client_credentials) | Read-only access | ❌ No | Food search, barcode lookup, recipes |
| **OAuth1** (3-legged) | Full access | ✅ Yes (one-time PIN) | All above + diary logging |

### Which to use?
- **Just searching foods?** → OAuth2 (simpler, no user login)
- **Logging to user's diary?** → OAuth1 (requires user authorization)

## 🚀 Quick Start

### 1. Get API Credentials
1. Go to https://platform.fatsecret.com
2. Register an application
3. Copy your **Consumer Key** and **Consumer Secret**

### 2. Save Credentials
```bash
mkdir -p ~/.config/fatsecret
cat > ~/.config/fatsecret/config.json << EOF
{
  "consumer_key": "YOUR_CONSUMER_KEY",
  "consumer_secret": "YOUR_CONSUMER_SECRET"
}
EOF
```

### 3. Install Dependencies
```bash
cd /path/to/fatsecret-skill
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4a. For Read-Only (OAuth2) - No user login needed
```bash
# Search works immediately
./scripts/fatsecret-cli.sh search "chicken breast"
```

### 4b. For Diary Logging (OAuth1) - One-time user authorization
```bash
# Run authentication flow
./scripts/fatsecret-cli.sh auth

# Follow prompts:
# 1. Visit the authorization URL
# 2. Log in with FatSecret account
# 3. Authorize the app
# 4. Enter the PIN shown

# Now you can log foods
./scripts/fatsecret-cli.sh quick egg 3 Breakfast
```

## 📋 CLI Commands

| Command | Auth Required | Description |
|---------|---------------|-------------|
| `search <query>` | OAuth2 | Search foods |
| `barcode <code>` | OAuth2 | Barcode lookup |
| `recipes <query>` | OAuth2 | Search recipes |
| `auth` | - | Run OAuth1 authentication |
| `log` | OAuth1 | Add food to diary (interactive) |
| `quick <food> [qty] [meal]` | OAuth1 | Quick log to diary |

## 🤖 Agent Integration

### For OpenClaw Agents

```python
from scripts.fatsecret_agent_helper import (
    get_authentication_flow,
    complete_authentication_flow,
    save_user_credentials
)

# Check authentication status
state = get_authentication_flow()

if state["status"] == "need_credentials":
    # Ask user for Consumer Key/Secret
    # Save with: save_user_credentials(key, secret)
    pass

elif state["status"] == "need_authorization":
    # Show authorization URL to user
    url = state["authorization_url"]
    # User visits URL, authorizes, gets PIN
    # Complete with: complete_authentication_flow(pin)
    pass

elif state["status"] == "already_authenticated":
    # Ready to use diary functions
    from scripts.fatsecret_diary_simple import quick_log
    quick_log("egg", quantity=3, meal="Breakfast")
```

### Agent Helper Functions

| Function | Description |
|----------|-------------|
| `get_authentication_flow()` | Check status, returns next step |
| `save_user_credentials(key, secret)` | Save API credentials |
| `complete_authentication_flow(pin)` | Complete OAuth1 with PIN |
| `quick_log(food, qty, meal)` | Log food to diary |
| `log_food(food_id, serving_id, grams_or_ml, meal, name)` | Precise logging |
| `search_food(query, tokens)` | Search foods |

### ⚠️ IMPORTANT: How `grams_or_ml` Works

The `grams_or_ml` parameter (called `number_of_units` in FatSecret API) is the **ACTUAL amount**, not a multiplier!

```python
# ❌ WRONG - This logs only 1.56 grams (7 kcal)!
log_food(food_id, serving_100g_id, 1.56, "Breakfast", "Cookies")

# ✅ CORRECT - This logs 156 grams (741 kcal)
log_food(food_id, serving_100g_id, 156, "Breakfast", "Cookies")
```

**Examples:**
| What you want | Serving type | grams_or_ml value |
|---------------|--------------|-------------------|
| 156g of cookies | "100g" serving | `156` |
| 200ml of milk | "100ml" serving | `200` |
| 3 eggs | "1 large egg" serving | `3` |
| 2 slices of bread | "1 slice" serving | `2` |

## 🔐 Credential Storage

All credentials and tokens are stored locally:

| File | Contents | Created By |
|------|----------|------------|
| `$CONFIG_DIR/config.json` | Consumer Key/Secret | User (manual) |
| `$CONFIG_DIR/oauth1_access_tokens.json` | OAuth1 access tokens | `auth` command |
| `$CONFIG_DIR/token.json` | OAuth2 token (auto-refreshed) | OAuth2 client |

Where `$CONFIG_DIR` is `~/.config/fatsecret` by default, or the value of `FATSECRET_CONFIG_DIR` if set.

**To revoke access:** Delete the config folder and revoke app access from your FatSecret account settings.

### 🐳 Container/Docker Environments

In containerized environments (Docker, OpenClaw sandbox), `~/.config/` may not persist across restarts. Use `FATSECRET_CONFIG_DIR` to point to a persistent volume:

```bash
# Set env var to persistent directory
export FATSECRET_CONFIG_DIR="/home/node/clawd/config/fatsecret"

# Or prefix commands
FATSECRET_CONFIG_DIR="/persistent/path" ./scripts/fatsecret-cli.sh auth
```

**OpenClaw example** - add to your shell init or AGENTS.md:
```bash
export FATSECRET_CONFIG_DIR="/home/node/clawd/config/fatsecret"
```

## 🌐 Proxy Configuration (Optional)

Some FatSecret API plans require IP whitelisting. If needed, set a proxy:

```bash
# Environment variable
export FATSECRET_PROXY="socks5://127.0.0.1:1080"

# Or in config.json
{
  "consumer_key": "...",
  "consumer_secret": "...",
  "proxy": "socks5://127.0.0.1:1080"
}
```

**If you don't need a proxy:** The skill works without it. Proxy is only required if FatSecret blocks your IP.

## 🌍 Open Food Facts (Alternative)

For European products, use the free Open Food Facts API (no authentication):

```python
from scripts.openfoodfacts_client import OpenFoodFactsClient

off = OpenFoodFactsClient(country="it")
products = off.search("barilla")
product = off.get_product("8076800105735")  # Barcode
```

## 📁 File Structure

```
fatsecret/
├── SKILL.md                      # This documentation
├── README.md                     # GitHub/ClawHub readme
├── requirements.txt              # Python: requests, requests[socks]
├── scripts/
│   ├── fatsecret-cli.sh          # Main CLI (bash wrapper)
│   ├── fatsecret_auth.py         # OAuth1 3-legged authentication
│   ├── fatsecret_agent_helper.py # Helper functions for agents
│   ├── fatsecret_diary_simple.py # Diary logging (OAuth1)
│   ├── fatsecret_client.py       # OAuth2 client (read-only)
│   └── openfoodfacts_client.py   # Open Food Facts client
└── examples/
    └── agent_usage_example.py    # Agent integration example
```

## ⚠️ Security Notes

1. **Credentials are stored locally** in `~/.config/fatsecret/`
2. **OAuth1 tokens don't expire** unless you revoke them
3. **OAuth1 grants full access** to your FatSecret diary (read + write)
4. **To uninstall safely:** Delete `~/.config/fatsecret/` and revoke app from FatSecret account

## 🔗 References

- FatSecret API: https://platform.fatsecret.com/docs
- OAuth1 Guide: https://platform.fatsecret.com/docs/guides/authentication/oauth1/three-legged
- Open Food Facts: https://wiki.openfoodfacts.org/API
## Changelog

### v1.0.1 (2026-02-20)
- Fixed OAuth2 client - now uses OAuth1 for all operations (food search + diary)
- Unified authentication: single OAuth1 flow works for both read and write operations
- Removed broken OAuth2 implementation
