# Marketplace Discovery

Browse, search, and consume x402 marketplace services.

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/marketplace` | GET | List all public listings |
| `/api/marketplace/search?q=<term>` | GET | Search by keyword |
| `/api/marketplace/featured` | GET | Featured listings |
| `/api/marketplace/<slug>` | GET | Single endpoint details |
| `/api/marketplace/list` | POST | List endpoint (provider) |
| `/api/marketplace/unlist` | POST | Remove from marketplace |

## Categories
`ai`, `data`, `finance`, `utility`, `social`, `gaming`

## Example: Browse All

```bash
python discover_marketplace.py
```

## Example: Consume Found Service

```bash
# Get details for an endpoint
python discover_marketplace.py details weather-api

# Pay and consume
python pay_base.py https://api.x402layer.cc/e/weather-api
```

## Scripts

- `discover_marketplace.py` - Browse/search marketplace
- `list_on_marketplace.py` - List/unlist your endpoint
