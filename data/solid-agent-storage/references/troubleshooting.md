# Troubleshooting

## Common Errors

### "No passphrase provided"

**Cause:** The `INTERITION_PASSPHRASE` environment variable is not set.

**Fix:**
```bash
export INTERITION_PASSPHRASE="your-passphrase-here"
```

### "No credentials found for agent X"

**Cause:** No WebID and Pod have been provisioned for this agent, or credentials are stored under a different name.

**Fix:**
1. Check existing agents: `scripts/status.sh`
2. Provision a WebID and Pod: `scripts/provision.sh --name <agent-name>`

### "Invalid passphrase — cannot decrypt credentials"

**Cause:** The `INTERITION_PASSPHRASE` value doesn't match the one used when the agent was provisioned.

**Fix:** Use the same passphrase that was set when `provision.sh` was first run. If you've lost the passphrase, you'll need to re-provision the agent's WebID and Pod (which creates new identity and storage).

### "Token request failed: 401"

**Cause:** The client credentials stored for this agent are invalid or the CSS server has been reset.

**Fix:** Re-provision the agent's WebID and Pod with `scripts/provision.sh --name <agent-name>`.

### Expired token (HTTP 401 on curl requests)

**Cause:** The Bearer token has expired. Tokens last 600 seconds (10 minutes).

**Fix:** Run `scripts/get-token.sh --agent <name>` to get a fresh token. As a rule of thumb, re-fetch if more than 8 minutes have elapsed since your last token request.

### "HTTP 404 Not Found"

**Cause:** The resource doesn't exist at that URL.

**Fix:**
- Check the URL is correct (including trailing slashes for containers)
- Write data to the URL first before reading it
- Container URLs must end with `/`

### "HTTP 409 Conflict"

**Cause:** Trying to create a resource that already exists, or a naming conflict.

**Fix:** Use PUT to overwrite, or choose a different URL.

### "ECONNREFUSED"

**Cause:** The Solid server is not running.

**Fix:**
1. Start the server: `docker-compose up -d`
2. Verify it's running: `curl http://localhost:3000/`
3. Check `SOLID_SERVER_URL` matches the server address

## Data Format Issues

### Turtle syntax errors

If writing Turtle data and getting 400 errors, check:
- Prefixes are declared with `@prefix`
- Statements end with `.`
- URIs are wrapped in `<angle-brackets>`
- Strings are wrapped in `"double-quotes"`

### Content-Type missing or wrong on curl requests

The server rejects PUT and PATCH requests without a `Content-Type` header. Always include one:
- Turtle: `-H "Content-Type: text/turtle"`
- Plain text: `-H "Content-Type: text/plain"`
- JSON: `-H "Content-Type: application/json"`
- JSON-LD: `-H "Content-Type: application/ld+json"`
- SPARQL Update: `-H "Content-Type: application/sparql-update"`

### Missing trailing slash on container URLs

Container URLs **must** end with `/`. If you GET or PUT to a container path without a trailing slash, you'll get unexpected results (404 or creating a resource instead of a container).

```bash
# Wrong — this is a resource URL
curl -s -H "Authorization: Bearer $TOKEN" "${POD_URL}memory"

# Correct — this is a container URL
curl -s -H "Authorization: Bearer $TOKEN" "${POD_URL}memory/"
```
