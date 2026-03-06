# HookCatch Skill for OpenClaw

This OpenClaw skill enables your AI assistant to test webhooks and expose local services using [HookCatch](https://hookcatch.dev).

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install hookcatch
```

### Manual Installation

1. Install the HookCatch CLI globally:
   ```bash
   npm install -g hookcatch
   ```

2. Install the OpenClaw skill wrapper (optional, provides better AI formatting):
   ```bash
   npm install -g @hookcatch/openclaw-skill
   ```

3. Copy this skill directory to your OpenClaw workspace:
   ```bash
   cp -r skills/hookcatch ~/.openclaw/skills/
   ```

4. Set up authentication:
   ```bash
   hookcatch login
   # Or generate an API token:
   hookcatch token generate
   export HOOKCATCH_API_KEY="hc_live_..."
   ```

5. Add the API key to your OpenClaw config (`~/.openclaw/openclaw.json`):
   ```json
   {
     "skills": {
       "entries": {
         "hookcatch": {
           "enabled": true,
           "apiKey": "hc_live_..."
         }
       }
     }
   }
   ```

## Usage

The skill provides two ways to interact with HookCatch:

1. **Direct CLI** (use `hookcatch` command directly)
2. **Skill Wrapper** (use `hookcatch-skill` for AI-optimized output)

The wrapper automatically:
- Formats output as JSON for better AI parsing
- Maps `HOOKCATCH_API_KEY` → `HOOKCATCH_TOKEN`
- Provides structured error messages
- Validates authentication before commands

## What is HookCatch?

HookCatch is a webhook testing and localhost tunneling tool that lets you:
- **Create webhook bins** to capture and inspect HTTP requests
- **Tunnel localhost** to test webhooks locally without deploying
- **Manage bins programmatically** via CLI

Perfect for testing integrations with Stripe, Twilio, GitHub, SendGrid, and any other webhook-based services.

## Usage Examples

### Create a Webhook Bin

Ask OpenClaw:
> "Create a HookCatch bin for testing Stripe webhooks"

OpenClaw will:
1. Run `hookcatch bin create --name "Stripe Test"`
2. Return the webhook URL: `https://hookcatch.dev/b/abc123xyz`
3. You can use this URL in your Stripe dashboard

### View Captured Requests

Ask OpenClaw:
> "Show me the last 10 requests to bin abc123xyz"

OpenClaw will:
1. Run `hookcatch bin requests abc123xyz --limit 10 --format json`
2. Parse and display the captured webhooks
3. Show method, path, headers, body for each request

If the bin is private:
```bash
hookcatch bin requests abc123xyz --password "secret123" --format json
```

To inspect a single request in detail:
```bash
hookcatch request <requestId> <binId> --format json
```

To inspect a single request in detail:
```bash
hookcatch request <requestId> <binId> --format json
```

### Expose Localhost

Ask OpenClaw:
> "Expose my local server on port 3000"

OpenClaw will:
1. Run `hookcatch tunnel 3000`
2. Return the public URL: `https://hookcatch.dev/tunnel/xyz789`
3. Forward requests to your local port 3000

## Configuration

### Environment Variables

- `HOOKCATCH_API_KEY` - Your API token (get with `hookcatch token generate`)
- `HOOKCATCH_API_URL` - Override API URL (default: https://api.hookcatch.dev)

### OpenClaw Config

In `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "hookcatch": {
        "enabled": true,
        "apiKey": "hc_live_...",
        "env": {
          "HOOKCATCH_API_KEY": "hc_live_..."
        }
      }
    }
  }
}
```

## Why HookCatch for OpenClaw?

1. **Better than ngrok**: No complex setup, works instantly
2. **Webhook inspection**: See exactly what services are sending
3. **Automation-friendly**: JSON output for easy parsing
4. **OpenClaw-optimized**: Designed for AI assistant workflows
5. **Free tier**: Generous limits for personal projects

## Commands Available to OpenClaw

- `hookcatch bin create` - Create webhook bin
- `hookcatch bin list` - List your bins
- `hookcatch bin requests <binId>` - Get captured requests
- `hookcatch bin update <binId>` - Update bin settings (name/private/password)
- `hookcatch bin delete <binId>` - Delete a bin
- `hookcatch request <requestId> <binId>` - Show a single request
- `hookcatch replay <binId> <requestId> <url>` - Replay a request to a target URL
- `hookcatch tunnel <port>` - Expose localhost
- `hookcatch tunnel list` - List active tunnels
- `hookcatch stop <tunnelId>` - Stop an active tunnel
- `hookcatch token generate` - Generate API token
- `hookcatch token status` - Check token status
- `hookcatch token revoke` - Revoke API token
- `hookcatch status` / `hookcatch whoami` - Show account details

## Troubleshooting

### "Not authenticated" error

Generate an API token:
```bash
hookcatch token generate
export HOOKCATCH_API_KEY="hc_live_..."
```

### CLI not found

Install globally:
```bash
npm install -g hookcatch
```

### Tunnel expires too quickly (FREE tier)

FREE tier tunnels last 5 minutes per session (3 sessions/day). Upgrade to PLUS for 1-hour sessions or PRO for unlimited.

## Support

- **Documentation**: https://docs.hookcatch.dev
- **GitHub**: https://github.com/hookcatch/cli
- **Discord**: Join #hookcatch in the OpenClaw Discord
- **Email**: support@hookcatch.dev

## Contributing

This skill is open source! Contributions welcome:
- Report issues: https://github.com/hookcatch/openclaw-skill/issues
- Submit PRs: https://github.com/hookcatch/openclaw-skill/pulls

## License

MIT License - See LICENSE file

---

**Built with ❤️ for the OpenClaw community** 🪝
