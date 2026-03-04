# Authentication & Environment Setup

## Getting API Credentials

1. Go to <https://developer.godaddy.com/keys>
2. Create a new API key (choose "Production" or "OTE" for testing)
3. Save your **API Key** and **API Secret** securely

## Environment Variables

Set these in your shell:

```bash
# For production
export GODADDY_API_BASE_URL="https://api.godaddy.com"
export GODADDY_API_KEY="your-key-here"
export GODADDY_API_SECRET="your-secret-here"

# For OTE (test environment)
export GODADDY_API_BASE_URL="https://api.ote-godaddy.com"
export GODADDY_API_KEY="your-ote-key"
export GODADDY_API_SECRET="your-ote-secret"
```

Add to `~/.zshrc` or `~/.bashrc` for persistence:

```bash
echo 'export GODADDY_API_KEY="..."' >> ~/.zshrc
echo 'export GODADDY_API_SECRET="..."' >> ~/.zshrc
echo 'export GODADDY_API_BASE_URL="https://api.godaddy.com"' >> ~/.zshrc
source ~/.zshrc
```

## Authorization Header Format

All API calls use this header:

```
Authorization: sso-key <API_KEY>:<API_SECRET>
```

Example:
```
Authorization: sso-key dGVzdGtleToxMjM0:dGVzdHNlY3JldDo1Njc4
```

## Testing Authentication

Run a simple list domains call:

```bash
./scripts/gd-domains.sh list
```

If auth works, you'll see JSON output. If not, check:
- Environment variables are set correctly
- API key/secret are valid and not expired
- You're using the correct base URL (production vs OTE)
