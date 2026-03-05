# FatSecret Skill for OpenClaw

Complete FatSecret nutrition API integration with food search, barcode lookup, recipes, and **diary logging**.

## ✨ Features

- 🔍 **Food Search** - Search FatSecret's extensive database
- 📦 **Barcode Lookup** - Scan product barcodes
- 🍳 **Recipe Search** - Find healthy recipes
- 📝 **Diary Logging** - Log meals to your FatSecret account
- 🤖 **Agent Ready** - Helper functions for OpenClaw agents
- 🇪🇺 **Open Food Facts** - European product database (free, no auth)

## 🔐 Authentication

| Method | Use Case | User Login |
|--------|----------|------------|
| OAuth2 | Read-only (search, barcode) | ❌ No |
| OAuth1 | Full access (+ diary logging) | ✅ Yes (one-time) |

## ⚡ Quick Start

### 1. Install
```bash
clawhub install fatsecret
cd skills/fatsecret
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure
Get credentials from https://platform.fatsecret.com

```bash
mkdir -p ~/.config/fatsecret
cat > ~/.config/fatsecret/config.json << EOF
{
  "consumer_key": "YOUR_KEY",
  "consumer_secret": "YOUR_SECRET"
}
EOF
```

### 3. Use

**Search (works immediately):**
```bash
./scripts/fatsecret-cli.sh search "chicken breast"
```

**Diary logging (requires one-time auth):**
```bash
./scripts/fatsecret-cli.sh auth  # Follow prompts
./scripts/fatsecret-cli.sh quick egg 3 Breakfast
```

## 📋 CLI Commands

```bash
./scripts/fatsecret-cli.sh search "oatmeal"     # Search foods
./scripts/fatsecret-cli.sh barcode 0041270003490 # Barcode lookup
./scripts/fatsecret-cli.sh recipes "low carb"   # Recipe search
./scripts/fatsecret-cli.sh auth                  # OAuth1 setup
./scripts/fatsecret-cli.sh log                   # Interactive diary
./scripts/fatsecret-cli.sh quick egg 3 Breakfast # Quick log
```

## 🤖 Agent Integration

```python
from scripts.fatsecret_agent_helper import (
    get_authentication_flow,
    save_user_credentials,
    complete_authentication_flow
)
from scripts.fatsecret_diary_simple import quick_log

# Check status
state = get_authentication_flow()

# Handle authentication flow
if state["status"] == "need_credentials":
    save_user_credentials(consumer_key, consumer_secret)
elif state["status"] == "need_authorization":
    # Show state["authorization_url"] to user, get PIN
    complete_authentication_flow(pin)

# Log food
quick_log("egg", quantity=3, meal="Breakfast")
```

## 🔧 Optional: Proxy Setup

Only needed if FatSecret blocks your IP:

```bash
export FATSECRET_PROXY="socks5://127.0.0.1:1080"
```

## 🐳 Container Environments

In Docker/containers, `~/.config/` may not persist. Use `FATSECRET_CONFIG_DIR`:

```bash
export FATSECRET_CONFIG_DIR="/persistent/path/fatsecret"
```

## 📁 Files

All stored in `$FATSECRET_CONFIG_DIR` (default: `~/.config/fatsecret`):

- `config.json` - Your API credentials
- `oauth1_access_tokens.json` - OAuth1 tokens (after auth)
- `token.json` - OAuth2 token (auto-refreshed)

**To uninstall:** Delete the config folder and revoke app from FatSecret account.

## 📄 License

MIT

## 🔗 Links

- [FatSecret API](https://platform.fatsecret.com)
- [Open Food Facts](https://openfoodfacts.org)