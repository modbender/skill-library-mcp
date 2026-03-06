# Setup Guide

## Prerequisites

- Python 3.12+
- Poetry
- Git

## Installation

**Important:** The SDK must be installed from GitHub via `git clone`. Do NOT install from PyPI (`pip install wayfinder-paths` will not work).

### 0. Get your API key

Get your Wayfinder API key at **https://strategies.wayfinder.ai** (format: `wk_...`). You will need this during setup.

### 1. Choose an SDK location (recommended)

```bash
# Path to your local clone of wayfinder-paths-sdk
export WAYFINDER_SDK_PATH="${WAYFINDER_SDK_PATH:-$HOME/wayfinder-paths-sdk}"

# Path to your config file
export WAYFINDER_CONFIG_PATH="${WAYFINDER_CONFIG_PATH:-$WAYFINDER_SDK_PATH/config.json}"
```

### 2. Clone the SDK from GitHub

```bash
# Must clone from GitHub — do NOT pip install
if [ ! -d "$WAYFINDER_SDK_PATH" ]; then
  git clone https://github.com/WayfinderFoundation/wayfinder-paths-sdk.git "$WAYFINDER_SDK_PATH"
fi
cd "$WAYFINDER_SDK_PATH"
```

### 3. Install Dependencies

```bash
cd "$WAYFINDER_SDK_PATH"
poetry install
```

### 4. Run Guided Setup

```bash
cd "$WAYFINDER_SDK_PATH"
python3 scripts/setup.py
```

Options:
- `--api-key KEY` — Provide API key non-interactively (key from https://strategies.wayfinder.ai)
- `--non-interactive` — Fail instead of prompting (for CI)

This creates:
- `config.json` with API keys and RPC endpoints
- A `main` wallet for trading
- MCP server configuration

## Bot Wallets (Prefer Seed Phrase)

`scripts/setup.py` creates **random local dev wallets** by default (it writes `private_key_hex` into `config.json`). For a long-running bot, prefer a **single seed phrase** stored in your backend/secret manager so the wallet can be recovered/reprovisioned.

**CRITICAL: NEVER output private keys or seed phrases into the conversation.** These are secrets — they must stay on the machine, never in chat.

If this is the **first time** setting up a bot, the bot/operator flow should:
- Ask the user to **retrieve the seed phrase directly from their machine or secret manager** (recommended), if one already exists. Tell them where/how:
  1. SSH into the bot host and `cd "$WAYFINDER_SDK_PATH"` (default: `$HOME/wayfinder-paths-sdk`).
  2. Confirm the config location: `$WAYFINDER_CONFIG_PATH` (default: `$WAYFINDER_SDK_PATH/config.json`).
  3. Fetch the seed phrase from your secret manager (avoid printing/logging it).
  4. Use it to provision the bot wallet in `config.json` (label `main`) with derived `address` + `private_key_hex`.
- **Only if the user explicitly confirms they cannot access the machine to retrieve it themselves**, offer to generate a new seed phrase and display it once for the user to record, then store it in the backend/secret manager. Do not proactively offer to show it.

**Important:** Never log or paste the seed phrase into chat. Never output private keys into the conversation. Avoid printing secrets on shared servers where shells/logging/audit trails may capture them. If the bot host is lost/rotated and the seed phrase only existed on that box, you can lose access to the wallet forever. Always store the seed phrase in your backend/secret manager and ensure it's recoverable. After you have the seed phrase stored safely, provision the bot wallet into `config.json` under `wallets` (typically label `main`) with the derived `address` and `private_key_hex`.

### 5. API Key

Your API key (from **https://strategies.wayfinder.ai**, format: `wk_...`) should already be configured if you provided it during guided setup. If not:

API key precedence:
1. `config.json` → `system.api_key` (recommended)
2. Environment variable `WAYFINDER_API_KEY`
3. CLI flag `--api-key`

### 6. Verify

```bash
cd "$WAYFINDER_SDK_PATH"
poetry run wayfinder resource wayfinder://strategies
poetry run wayfinder resource wayfinder://wallets
poetry run wayfinder resource wayfinder://balances/main
```

## Configuration File

The main config lives at `$WAYFINDER_CONFIG_PATH` (default: `$WAYFINDER_SDK_PATH/config.json`). It contains:

- **API keys**: Wayfinder API key for pool/token data
- **RPC endpoints**: Chain-specific RPC URLs
- **Wallets**: Wallet labels, addresses, and private keys

### Manual Config

```bash
cd "$WAYFINDER_SDK_PATH"
cp config.example.json "$WAYFINDER_CONFIG_PATH"
# Edit $WAYFINDER_CONFIG_PATH with your settings
```

### Create Additional Wallets

```bash
# Generate test wallets
cd "$WAYFINDER_SDK_PATH"

# Create a labeled wallet
poetry run wayfinder wallets --action create --label my_strategy
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `WAYFINDER_SDK_PATH` | Local path to `wayfinder-paths-sdk` |
| `WAYFINDER_CONFIG_PATH` | Path to `config.json` (default: `$WAYFINDER_SDK_PATH/config.json`) |
| `WAYFINDER_API_KEY` | API key (fallback if not in config.json) |

## Updating

```bash
cd "$WAYFINDER_SDK_PATH"
git pull
poetry install
```

## Development Workflow

Quick setup loop for strategy/adapter development:

```bash
cd "$WAYFINDER_SDK_PATH"
poetry install                  # Install deps
just create-wallets             # Generate local wallets
just validate-manifests         # Validate manifests
just test-smoke                 # Run smoke tests
```

## Troubleshooting

- **"Python 3.10 not supported"** — Ensure Python 3.12+ is installed and poetry uses it
- **"Missing config"** — Run `python3 scripts/setup.py` or create `config.json` manually
- **"api_key not set"** — Check `config.json` has `system.api_key`, or set `WAYFINDER_API_KEY` env var. Key format: `wk_...`
- **"poetry not found"** — Install poetry: `curl -sSL https://install.python-poetry.org | python3 -`
- **"just not found"** — Install just: `cargo install just` or `brew install just`
- **Key not working** — Verify at https://strategies.wayfinder.ai, check for typos/whitespace. Key should start with `wk_`. Verify with: `poetry run python -c "from wayfinder_paths.core.clients.WayfinderClient import WayfinderClient; print('API key configured!')"`
