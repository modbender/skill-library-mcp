---
name: hookcatch
description: Test webhooks and expose local services using HookCatch - a developer-friendly webhook testing tool
user-invocable: true
metadata: {"openclaw":{"emoji":"🪝","requires":{"bins":["hookcatch"],"env":["HOOKCATCH_API_KEY"]},"primaryEnv":"HOOKCATCH_API_KEY","homepage":"https://hookcatch.dev","install":[{"id":"npm","kind":"node","packages":["hookcatch"],"bins":["hookcatch"],"label":"Install HookCatch CLI (npm)"}]}}
---

# HookCatch - Webhook Testing & Tunneling for OpenClaw

HookCatch is a webhook testing and localhost tunneling tool that lets you:
- Create webhook bins to capture and inspect HTTP requests
- Tunnel your localhost to test webhooks locally
- Manage bins and view captured requests programmatically

Perfect for testing webhook integrations (Stripe, Twilio, GitHub, etc.) from your OpenClaw skills.

## Quick Start

1. **Authenticate with HookCatch:**
   ```bash
   hookcatch login
   # Or use API token (recommended for automation):
   hookcatch token generate
   export HOOKCATCH_API_KEY="hc_live_..."
   ```

2. **Create a webhook bin:**
   ```bash
   hookcatch bin create --name "Test Stripe Webhooks"
   # Returns: https://hookcatch.dev/b/abc123xyz
   ```


3. **View created bins:**
   ```bash
   hookcatch bin list
   ```


4. **View captured requests:**
   ```bash
   hookcatch bin requests abc123xyz --format json
   ```
   OR

   ```bash
   hookcatch bin requests --binId abc123xyz --format json
   ```


## Available Commands

### Bin Management

**Create a new webhook bin:**
```bash
hookcatch bin create [--name "My Bin"] [--private] [--password "secret"] [--format json]
```
Options:
- `--name`: Optional bin name for organization
- `--private`: Create private bin (PLUS+ tier required)
- `--password`: Set password for private bin (min 4 chars)
- `--format`: Output format (`json` recommended for automation)

Returns: Bin ID, webhook URL, and view URL

**List your bins:**
```bash
hookcatch bin list [--format json]
```
Shows all your bins with request counts and status.

**Get requests for a bin:**
```bash
hookcatch bin requests <binId> [--limit 50] [--format json|table] [--method GET] [--password "secret"]
```
Options:
- `--limit`: Number of requests to fetch (default: 50)
- `--format`: Output format - `json` for scripts, `table` for viewing
- `--method`: Filter by HTTP method (GET, POST, etc.)
- `--password`: Password for private bins (if required; owners can use their auth token)

**Show a single request:**
```bash
hookcatch request <requestId> <binId> [--format json|pretty] [--password "secret"]
```

**Delete a bin:**
```bash
hookcatch bin delete <binId> --yes
```

**Update a bin:**
```bash
hookcatch bin update <binId> --name "New Name"
hookcatch bin update <binId> --private --password "secret123"
hookcatch bin update <binId> --public
```

**Show a single request:**
```bash
hookcatch request <requestId> <binId> [--format json|pretty]
```

**Replay a request to a new URL:**
```bash
hookcatch replay <binId> <requestId> <url>
hookcatch replay --binId <binId> --requestId <requestId> --url <url>
```

### Localhost Tunneling

**Expose your localhost:**
```bash
hookcatch tunnel 3000
# Creates: https://hookcatch.dev/tunnel/xyz789
```

**List active tunnels:**
```bash
hookcatch tunnel list
```

**Stop a tunnel:**
```bash
hookcatch stop <tunnelId>
```

Forward incoming requests from the public URL to your local port 3000.

**Tunnel limits:**
- FREE: 5 min/session, 3 sessions/day
- PLUS: 1h/session, unlimited
- PRO/ENTERPRISE: Unlimited

### API Token Management

**Generate long-lived API token:**
```bash
hookcatch token generate
# Store the token for automation
export HOOKCATCH_API_KEY="hc_live_..."
```

**Check token status:**
```bash
hookcatch token status
```

**Revoke token:**
```bash
hookcatch token revoke --yes
```

**Account status:**
```bash
hookcatch status
hookcatch whoami
```

## Usage Examples for OpenClaw Skills

### Example 1: Test Stripe Webhooks

```bash
# Create a bin for Stripe
BIN_URL=$(hookcatch bin create --name "Stripe Test" --format json | jq -r '.url')

# Use this URL in Stripe dashboard as webhook endpoint
echo "Configure Stripe webhooks to: $BIN_URL"

# Wait for webhooks...
sleep 10

# Fetch and analyze captured webhooks
hookcatch bin requests abc123xyz --format json | jq '.[] | {event: .body.type, amount: .body.data.object.amount}'
```

### Example 2: Test Local API

```bash
# Start your local API on port 8000
# python -m http.server 8000 &

# Expose it via tunnel
hookcatch tunnel 8000 --password <password>

# Now external services can reach your local API via:
# https://hookcatch.dev/tunnel/xyz789
```

### Example 3: Debug GitHub Webhooks

```bash
# Create bin
hookcatch bin create --name "GitHub Webhooks"

# In GitHub repo settings, add webhook URL
# Trigger events (push, PR, etc.)

# View requests
hookcatch bin requests abc123xyz --method POST --limit 10
```

## Integration with OpenClaw Skills

When building OpenClaw skills that need to test webhooks:

```javascript
// In your skill script
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Create a bin
const { stdout } = await execAsync('hookcatch bin create --format json');
const { binId, url } = JSON.parse(stdout);

// Use the webhook URL in your integration
console.log(`Webhook URL: ${url}`);

// Later, fetch requests
const { stdout: requests } = await execAsync(
  `hookcatch bin requests ${binId} --format json`
);
const captured = JSON.parse(requests);

// Process captured webhooks
for (const req of captured) {
  console.log(`${req.method} ${req.path}: ${JSON.stringify(req.body)}`);
}
```

## Environment Variables

- `HOOKCATCH_API_KEY` - API token for authentication (recommended for automation)
- `HOOKCATCH_API_URL` - Override API URL (default: https://api.hookcatch.dev)


## Benefits for OpenClaw Users

- **No more ngrok setup**: Use HookCatch tunnels for quick local testing
- **Webhook inspection**: See exactly what Stripe/Twilio/etc. is sending
- **Automation-friendly**: JSON output for easy parsing in skills
- **Private bins**: Keep your test data secure with password protection
- **Fast & simple**: One command to create bins or tunnels

## Getting Help

- Documentation: https://docs.hookcatch.dev
- Discord: Join #hookcatch in OpenClaw Discord
- GitHub: https://github.com/hookcatch/cli
- Email: support@hookcatch.dev

## Tips

1. **Use API tokens for skills**: Generate a token once and use it in `HOOKCATCH_API_KEY`
2. **JSON format for automation**: Always use `--format json` when parsing in scripts
3. **Private bins for sensitive data**: Use `--private` for production webhook testing
4. **Clean up after testing**: Delete bins with `hookcatch bin delete` to stay within limits

---

**Built for OpenClaw by the HookCatch team** 🪝
