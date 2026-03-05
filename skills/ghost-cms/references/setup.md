# Ghost CMS Setup & Authentication

## Getting Your API Credentials

### Step 1: Create Custom Integration

1. Log into your Ghost admin dashboard
2. Navigate to **Settings → Integrations**
3. Scroll to "Custom Integrations"
4. Click **+ Add custom integration**
5. Name it (e.g., "Moltbot" or "Navi")

### Step 2: Copy Credentials

After creating the integration, you'll see:
- **Admin API Key** - Long string starting with hexadecimal characters + a colon + more hex
- **API URL** - Your blog's API endpoint (format depends on hosting - see "Finding Your Blog URL" below)

**Important:** The Admin API Key has two parts separated by a colon:
- `{key_id}:{key_secret}`
- You need the entire string

### Step 3: Store Credentials Securely

**Option A: Configuration files** (recommended)

```bash
mkdir -p ~/.config/ghost
echo "YOUR_ADMIN_API_KEY" > ~/.config/ghost/api_key
echo "YOUR_GHOST_URL" > ~/.config/ghost/api_url
chmod 600 ~/.config/ghost/api_key ~/.config/ghost/api_url
```

**Option B: Environment variables**

```bash
export GHOST_ADMIN_KEY="YOUR_ADMIN_API_KEY"
export GHOST_API_URL="YOUR_GHOST_URL"

# See "Finding Your Blog URL" section below for URL format examples
```

Add these to your `~/.zshrc` or `~/.bashrc` for persistence.

## Finding Your Blog URL

Your Ghost API URL depends on your hosting type. The skill works with **all Ghost installations** (Ghost(Pro) and self-hosted).

### Ghost(Pro) Hosted

**Standard Ghost(Pro) subdomain:**
```bash
export GHOST_API_URL="https://yourblog.ghost.io"
```
- Find it in Settings → General → Publication info
- Uses default HTTPS port (443) - no port number needed

**Custom domain on Ghost(Pro):**
```bash
export GHOST_API_URL="https://blog.yourdomain.com"
```
- If you've connected a custom domain to Ghost(Pro)
- Still uses default port (443)

### Self-Hosted Ghost

**Production with reverse proxy (recommended):**
```bash
export GHOST_API_URL="https://blog.yourdomain.com"
```
- Nginx/Apache handles SSL and forwards to Ghost
- Ghost runs internally (usually on localhost:2368)
- Users access via standard HTTPS port (443)
- No port number needed in URL

**Development/Local (Ghost default port):**
```bash
export GHOST_API_URL="http://localhost:2368"
```
- Ghost's default port is **2368**
- Direct connection to Ghost (no reverse proxy)
- HTTP acceptable for local development
- Include port number

**Custom port deployment:**
```bash
# With SSL
export GHOST_API_URL="https://ghost.example.com:8080"

# Without SSL (not recommended for production)
export GHOST_API_URL="http://192.168.1.100:3000"
```
- If Ghost runs on non-standard port
- Always include `:PORT` in URL

### URL Format Rules

**Always:**
- ✅ Include protocol (`http://` or `https://`)
- ✅ Use your actual domain/IP
- ✅ Include `:PORT` if Ghost runs on non-standard port

**Never:**
- ❌ Include trailing slash
- ❌ Include `/ghost/api/admin` (added automatically by scripts)
- ❌ Use HTTP over public networks (security risk)

### Security: HTTP vs HTTPS

**Production (HTTPS required):**
- Use `https://` for all production deployments
- Admin API keys transmitted over encrypted connection
- Protects credentials from network sniffing
- Configure SSL via reverse proxy (Nginx/Apache) or use Ghost(Pro)

**Development (HTTP acceptable):**
- `http://localhost:2368` is fine for local development
- Never use HTTP for remote connections
- Admin API keys would be transmitted in plaintext

**Best practice for self-hosted:**
1. Run Ghost on localhost:2368 (internal only)
2. Set up Nginx/Apache as reverse proxy
3. Configure SSL certificate (Let's Encrypt)
4. Proxy handles HTTPS → forwards to Ghost internally
5. Use `https://yourdomain.com` as API URL (no port)

## Testing Authentication

Test your credentials with a simple API call:

```bash
GHOST_KEY=$(cat ~/.config/ghost/api_key)
GHOST_URL=$(cat ~/.config/ghost/api_url)

# Split the key into id and secret
KEY_ID=$(echo $GHOST_KEY | cut -d: -f1)
KEY_SECRET=$(echo $GHOST_KEY | cut -d: -f2)

# Create JWT token (requires jwt-cli or python)
# Simple test: just try to fetch site info
curl "${GHOST_URL}/ghost/api/admin/site/" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

If successful, you'll get JSON with your site information.

## Troubleshooting

### "401 Unauthorized"
- Check that you copied the entire Admin API Key (both parts, with colon)
- Verify the key hasn't been revoked in Ghost admin
- Ensure you're using the Admin API key, not Content API key
- Check key format: `{hex_id}:{hex_secret}`

### "404 Not Found"
- Verify your API URL is correct (check for trailing slashes)
- Confirm you're using `/ghost/api/admin/` in the path
- Check if your Ghost version supports Admin API (v2.0+)
- Verify Ghost is actually running on the specified URL/port

### "Connection refused" / "ECONNREFUSED"
- **Check port:** Ghost default is 2368, verify your configuration
- **Self-hosted:** Confirm Ghost is running (`ghost status` or check process)
- **Firewall:** Ensure port is open if accessing remotely
- **URL format:** Include port if not using standard (443/80)
  ```bash
  # Wrong: https://localhost (tries port 443)
  # Right:  http://localhost:2368
  ```

### "SSL certificate error" / "UNABLE_TO_VERIFY_LEAF_SIGNATURE"
- **Development:** Use `http://` instead of `https://` for localhost
- **Self-signed cert:** Add cert to trusted store or use HTTP for local testing
- **Production:** Verify SSL certificate is valid (check with browser first)
- **Let's Encrypt:** Ensure certificate hasn't expired

### "Invalid token"
- The Admin API Key must be split into ID and Secret
- JWT token generation requires proper encoding
- Check system time is accurate (JWT expiration)
- Verify the Admin API Key format (colon-separated hex values)

### "Timeout" errors
- **Port blocked:** Check firewall/security groups
- **Ghost not running:** Verify Ghost service is active
- **Wrong URL:** Double-check GHOST_API_URL
- **Network issues:** Test connectivity (`curl $GHOST_API_URL`)

## API Versions

Ghost uses versioned APIs. This skill targets:
- **Admin API v5.0** (current stable)
- Minimum Ghost version: **5.0+**

Check your Ghost version in Settings → About.

## Rate Limits

Ghost Admin API rate limits:
- **500 requests per hour** per integration
- Resets hourly
- Exceeding limit returns 429 status

Best practices:
- Cache frequently-accessed data
- Batch operations when possible
- Use webhooks for real-time updates instead of polling
