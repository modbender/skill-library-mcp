---
name: uf2-net
description: "Create, manage, and track short URLs using uf2.net API-first URL
  shortener. Use when: (1) shortening URLs for sharing or tracking, (2) creating
  custom short links with branded slugs, (3) managing existing short links
  (list/delete/stats), (4) tracking click counts on shortened URLs. Links never
  expire and support custom slugs. Service: uf2.net (https://uf2.net) -
  API-first URL shortener for bots and engineers."
---


# uf2.net URL Shortener

Create and manage short URLs via the uf2.net API. This skill provides a CLI wrapper for the uf2.net service (https://uf2.net), an API-first URL shortener designed for automation and bots.

## Quick Start

### 1. Register for API Key

If you don't have a uf2.net account:

```bash
curl -X POST https://uf2.net/api/v1/accounts/register \
  -H "Content-Type: application/json" \
  -d '{"username":"your-username"}'
```

Response includes `api_key` field. **Store this securely** (see Credential Management below).

### 2. Set Environment Variable

```bash
export UF2_API_KEY="uf2_..."
```

**Important:** Do not hardcode API keys in scripts or commit them to version control.

### 3. Common Operations

**Shorten a URL:**
```bash
scripts/uf2.sh create "https://example.com/long/path"
# → {"short_url":"https://uf2.net/abc123",...}
```

**Custom slug:**
```bash
scripts/uf2.sh create "https://github.com/my-repo" "my-repo" "My GitHub Repo"
# → {"short_url":"https://uf2.net/my-repo",...}
```

**List your links:**
```bash
scripts/uf2.sh list 10
# → {"links":[...],"total":42}
```

**Get link stats (public, no auth needed):**
```bash
scripts/uf2.sh get abc123
# → {"code":"abc123","click_count":42,...}
```

**Delete a link:**
```bash
scripts/uf2.sh delete abc123
```

## Credential Management

### Recommended: Environment Variables

Most secure for temporary/session use:
```bash
export UF2_API_KEY="uf2_..."
```

### For Persistent Storage

Choose one based on your security requirements:

**Option 1: Shell profile (user-only access)**
```bash
echo 'export UF2_API_KEY="uf2_..."' >> ~/.zshrc
# or ~/.bashrc for bash
```

**Option 2: OpenClaw secret store (if available)**
```bash
# Store in OpenClaw's secure credential storage
# (consult OpenClaw docs for secret management)
```

**Option 3: System keychain/credential manager**
```bash
# macOS Keychain, Linux Secret Service, Windows Credential Manager
# Use OS-native secure storage
```

**⚠️ Avoid:** Storing keys in plain text files in shared or version-controlled directories.

## Direct API Usage

For operations not covered by the script, use curl directly. See [api.md](references/api.md) for full API reference.

Example:
```bash
curl -X POST https://uf2.net/api/v1/links \
  -H "X-API-Key: $UF2_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","slug":"custom"}'
```

## Service Details

- **Service:** uf2.net (https://uf2.net)
- **Type:** API-first URL shortener for bots and engineers
- **TLS:** Yes (HTTPS only)
- **API Docs:** https://uf2.net/docs (Swagger), https://uf2.net/redoc (ReDoc)
- **Registration:** Open, free tier available
- **Rate Limits:** 20 registrations per IP per hour; reasonable use for authenticated endpoints

## Key Features

- **Never expires** - Links remain active indefinitely
- **Custom slugs** - Brand your short URLs (4-64 chars, lowercase a-z0-9_-)
- **Click tracking** - Monitor usage via click_count
- **Public metadata** - Anyone can view link stats (GET /links/{code})
- **Simple API** - RESTful with JSON responses

## Constraints

- Max URL length: 2048 characters
- Custom slugs are case-insensitive (stored lowercase)
- Slug conflicts return 409 error
- Private/localhost URLs rejected
- Registration rate limit: 20 per IP per hour

## Security Notes

- **API key required:** All authenticated operations require `UF2_API_KEY` header
- **Link visibility:** All created links are publicly accessible (anyone with the short URL can access the target)
- **Metadata visibility:** Link metadata (click counts, original URL) is publicly readable
- **No link expiration:** Links persist indefinitely unless manually deleted
- **Private URL rejection:** The service rejects localhost and private IP ranges

## Resources

- **Script:** [scripts/uf2.sh](scripts/uf2.sh) - CLI wrapper for common operations
- **Reference:** [references/api.md](references/api.md) - Full API documentation
- **Service homepage:** https://uf2.net
- **API docs:** https://uf2.net/docs (Swagger), https://uf2.net/redoc (ReDoc)
