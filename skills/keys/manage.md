# Key Management

Guide user through these commands. Never ask them to paste keys in chat.

## Add a Key

### macOS
```bash
security add-generic-password -s "keys:SERVICE" -a "$USER" -w "THE-API-KEY"
```

### Linux (requires libsecret-tools)
```bash
secret-tool store --label="SERVICE API Key" service keys:SERVICE
# Prompts for the key value securely
```

## Update a Key

### macOS
```bash
security delete-generic-password -s "keys:SERVICE" -a "$USER"
security add-generic-password -s "keys:SERVICE" -a "$USER" -w "NEW-API-KEY"
```

### Linux
```bash
secret-tool clear service keys:SERVICE
secret-tool store --label="SERVICE API Key" service keys:SERVICE
```

## Remove a Key

### macOS
```bash
security delete-generic-password -s "keys:SERVICE" -a "$USER"
```

### Linux
```bash
secret-tool clear service keys:SERVICE
```

## Verify a Key Exists

```bash
# This should return the key (or error if not found)
# macOS
security find-generic-password -s "keys:SERVICE" -a "$USER" -w

# Linux
secret-tool lookup service keys:SERVICE
```

## Add New Service to Broker

Edit `keys-broker.sh` and add to `ALLOWED_URLS`:

```bash
declare -A ALLOWED_URLS=(
    ["openai"]="^https://api\.openai\.com/"
    ["anthropic"]="^https://api\.anthropic\.com/"
    ["myservice"]="^https://api\.myservice\.com/"  # Add this
)
```

## Common Services

| Service | Key format | Get key at |
|---------|-----------|------------|
| openai | sk-... | platform.openai.com/api-keys |
| anthropic | sk-ant-... | console.anthropic.com/settings/keys |
| stripe | sk_live_... | dashboard.stripe.com/apikeys |
| github | ghp_... | github.com/settings/tokens |
