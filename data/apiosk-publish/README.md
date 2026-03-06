# Apiosk Publisher

Publish and manage paid APIs on `https://gateway.apiosk.com`.

## Quick Start

```bash
# Register (signed request)
./register-api.sh \
  --name "My Weather API" \
  --slug "my-weather-api" \
  --endpoint "https://my-api.com/v1" \
  --price 0.01 \
  --description "Real-time weather data" \
  --listing-group datasets

# List your APIs (signed request)
./my-apis.sh

# Update (signed request)
./update-api.sh --slug my-weather-api --price 0.02

# Deactivate (signed request)
./delete-api.sh --slug my-weather-api
```

## Auth Requirements

Gateway management routes require signed wallet auth headers:

- `x-wallet-address`
- `x-wallet-signature`
- `x-wallet-timestamp`
- `x-wallet-nonce`

Scripts generate these automatically using your key from:

- `~/.apiosk/wallet.json` (preferred, created by `apiosk-skill/setup-wallet.sh`)
- `APIOSK_PRIVATE_KEY` env var
- `--private-key` flag

## Listing Groups (Current)

For discovery and positioning, use these groups:

- `api`
- `datasets`
- `compute`

`register-api.sh --listing-group` maps to `category`:

- `api` -> `data`
- `datasets` -> `dataset`
- `compute` -> `compute`

## Commands

- `register-api.sh` register a new API
- `my-apis.sh` list your APIs and earnings
- `update-api.sh` update endpoint, price, description, active state
- `delete-api.sh` deactivate an API
- `test-api.sh` send a plain probe request via gateway (no payment proof)

## Requirements

- `curl`
- `jq`
- `cast` (Foundry, used for request signatures)

Install Foundry: [https://book.getfoundry.sh/getting-started/installation](https://book.getfoundry.sh/getting-started/installation)
