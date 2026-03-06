# BrickLink - Setup Instructions

## Prerequisites

### Required Software

- **Python 3** — For running the BrickLink API CLI

No additional Python packages required. The skill uses only Python standard library modules.

### API Credentials

You need OAuth 1.0 credentials from BrickLink:

1. Log in to your BrickLink account
2. Go to **My BrickLink** → **API Consumer**
3. Create a new API token
4. Save the following credentials:
   - Consumer Key
   - Consumer Secret
   - Token Value
   - Token Secret

## Configuration

### Method 1: Config File (Recommended)

Place OAuth credentials in `~/clawd/bricklink/config.json`:

```json
{
  "oauth": {
    "consumer_key": "YOUR_CONSUMER_KEY",
    "consumer_secret": "YOUR_CONSUMER_SECRET",
    "token_value": "YOUR_TOKEN_VALUE",
    "token_secret": "YOUR_TOKEN_SECRET"
  }
}
```

### Method 2: Environment Variables

Alternatively, set individual environment variables:

```bash
export BRICKLINK_CONSUMER_KEY="YOUR_CONSUMER_KEY"
export BRICKLINK_CONSUMER_SECRET="YOUR_CONSUMER_SECRET"
export BRICKLINK_TOKEN_VALUE="YOUR_TOKEN_VALUE"
export BRICKLINK_TOKEN_SECRET="YOUR_TOKEN_SECRET"
```

The skill will use the config file if it exists, falling back to environment variables if not.

## Permissions

- **Read operations** (get-orders, get-inventories, etc.) work immediately
- **Write operations** (update-order, create-inventory, etc.) execute immediately — double-check parameters before running
- **Order mutations** (update-order, update-order-status, update-payment-status) only work for **store orders** (direction=out, where you are the seller)
- Purchases (direction=in) cannot be modified via API — use the BrickLink website instead
