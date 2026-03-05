# krocli

CLI and [OpenClaw](https://openclaw.com) skill for the [Kroger API](https://developer.kroger.com/). Works with all Kroger-family stores: Kroger, Ralphs, Fred Meyer, Harris Teeter, King Soopers, Fry's, QFC, Mariano's, Pick 'n Save, and more.

## Install

```bash
go install github.com/blanxlait/krocli/cmd/krocli@latest
```

Or build from source:

```bash
make build    # → bin/krocli
```

## Setup

krocli works out of the box — no Kroger developer account required. It uses a hosted OAuth proxy so you can start searching immediately.

```bash
krocli products search --term "milk"    # Just works
krocli auth login                       # Browser login for cart/profile
krocli auth status                      # Shows "Mode: hosted"
```

### Bring Your Own Credentials (optional)

If you prefer to use your own Kroger developer app:

1. Go to [developer.kroger.com](https://developer.kroger.com/) and create an app.
   - **Scopes**: `product.compact`, `cart.basic:write`, `profile.compact`
   - **Redirect URI**: `http://localhost:8080/callback`
2. Import your credentials:

```bash
krocli auth credentials set /path/to/creds.json
```

This switches krocli to **local mode**, talking directly to the Kroger API. Remove `~/.config/krocli/credentials.json` to switch back to hosted mode.

## Authentication

There are two auth modes:

- **Client credentials** — automatic, used for product/location searches
- **Authorization code** — required for cart and identity; run `krocli auth login` to complete the browser OAuth flow

```bash
krocli auth login       # Browser OAuth → stores refresh token
krocli auth status      # Show current auth state and mode (hosted/local)
```

## Usage

### Products

```bash
krocli products search --term "milk"
krocli products search --term "bread" --location-id 01400376 --limit 5
krocli products get 0011110838049
```

### Locations

```bash
krocli locations search --zip-code 45202
krocli locations search --zip-code 45202 --radius 25
krocli locations get 01400376
krocli locations chains
krocli locations departments
```

### Cart (requires `auth login`)

```bash
krocli cart add --upc 0011110838049 --qty 2
```

### Identity (requires `auth login`)

```bash
krocli identity profile
```

## Output Formats

| Flag | Format | Destination |
|------|--------|-------------|
| (none) | Human-friendly | stderr |
| `-j` | JSON | stdout |
| `-p` | Plain/TSV | stdout |

Pipe-friendly: `krocli -j products search --term "eggs" | jq '.data[].description'`

## OpenClaw Skill

This repo is also published as an OpenClaw skill on ClawHub. No CLI install needed — any LLM agent with OpenClaw learns the Kroger API directly.

```bash
clawhub install supermarket
```

Then ask things like "search for organic milk at Ralphs" or "find King Soopers near 80202" and the skill handles it via the hosted proxy.

## Development

```bash
make build    # Build binary
make lint     # Run golangci-lint
make clean    # Remove build artifacts
```
