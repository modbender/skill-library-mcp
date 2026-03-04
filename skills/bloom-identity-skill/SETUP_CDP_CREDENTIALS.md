# Setup CDP Credentials

## Problem
Agent Kit requires credentials in **JSON file format**, not environment variables.

## Solution

### Step 1: Get Your CDP API Key

1. Visit https://portal.cdp.coinbase.com/
2. Go to API Keys
3. Create new API key or use existing
4. **Download the JSON file** (important!)

### Step 2: Place the JSON File

The downloaded file should be named `coinbase_cloud_api_key.json`:

```bash
# Place in project root
./coinbase_cloud_api_key.json
```

**Example format:**
```json
{
  "name": "organizations/YOUR_ORG_ID/apiKeys/YOUR_KEY_ID",
  "privateKey": "-----BEGIN EC PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END EC PRIVATE KEY-----\n"
}
```

### Step 3: Verify

```bash
# Check file exists
ls coinbase_cloud_api_key.json

# Test the skill
npm run build
node dist/index.js --user-id test-user
```

### Step 4: Secure the File

```bash
# Add to .gitignore (already done)
echo "coinbase_cloud_api_key.json" >> .gitignore

# Set file permissions (read-only)
chmod 400 coinbase_cloud_api_key.json
```

---

## Common Issues

### "file not found at coinbase_cloud_api_key.json"
- ✅ File must be in project root (same directory as package.json)
- ✅ File must be named exactly `coinbase_cloud_api_key.json`
- ✅ File must be valid JSON format

### "Invalid configuration"
- ✅ Check JSON format is valid
- ✅ Ensure privateKey includes BEGIN/END lines
- ✅ Verify API key is active in CDP portal

---

## Environment Variables (Don't Work)

These DON'T work for Agent Kit:
```bash
# ❌ These are ignored by Agent Kit
CDP_API_KEY_ID=...
CDP_API_KEY_SECRET=...
```

Agent Kit only reads from JSON file.

---

## Security Notes

⚠️ **Never commit this file to git**
⚠️ **Keep the private key secure**
⚠️ **Use different keys for dev/prod**

The file is already in `.gitignore` to prevent accidental commits.

---

## For Production

Use environment-specific key files:

```bash
# Development
coinbase_cloud_api_key.json

# Production (on server)
/secure/path/coinbase_cloud_api_key.json

# Set file path via env var (if Agent Kit supports it)
CDP_KEY_FILE=/secure/path/coinbase_cloud_api_key.json
```
