# ClawGuard OpenClaw Plugin

Automatic security checks for all OpenClaw tool calls.

## What It Does

The ClawGuard plugin hooks into OpenClaw's `before_tool_call` event to automatically check:

- **Commands** (`exec` tool): Checks for malicious commands, pipe-to-shell patterns, dangerous operations
- **URLs** (`web_fetch`, `browser` tools): Checks against threat database for malicious domains, phishing sites, scams

## Installation

### 1. Enable the Plugin

The plugin is located at `~/clawd/skills/clawguard/openclaw-plugin.js`.

To enable it in OpenClaw, add it to your plugin configuration. The exact method depends on your OpenClaw setup, but typically you would:

```bash
# If OpenClaw supports plugin directory
ln -s ~/clawd/skills/clawguard/openclaw-plugin.js ~/.openclaw/plugins/

# OR if OpenClaw has a plugins config file
# Add to your OpenClaw config:
{
  "plugins": [
    "~/clawd/skills/clawguard/openclaw-plugin.js"
  ]
}
```

### 2. Configure Discord Approval (Optional)

To enable Discord approval for warnings:

```bash
# Enable Discord
clawguard config --enable discord

# Set your Discord channel ID (where approval requests will be sent)
clawguard config --set discord.channelId --value "YOUR_CHANNEL_ID"

# Optional: Adjust timeout (default 60s)
clawguard config --set discord.timeout --value "30000"
```

### 3. Restart OpenClaw

```bash
openclaw gateway restart
```

## How It Works

### Safe Commands/URLs
When you execute a safe command or visit a safe URL, the plugin runs the check silently and allows it:

```
✅ Safe - proceeds normally
```

### Blocked Threats
If a **confirmed threat** is detected (exit code 1), the plugin blocks execution immediately:

```
🛡️ ClawGuard BLOCKED: Malicious domain detected
   Threat: x402 Bitcoin Scam Network (OSA-2026-001)
```

The tool call is prevented from executing.

### Warnings (with Discord Approval)
If a **potential threat** is detected (exit code 2), the plugin behavior depends on configuration:

**With Discord enabled:**
1. Sends approval request to Discord channel
2. Waits for human response (✅ approve or ❌ deny)
3. Proceeds if approved, blocks if denied/timeout

**Without Discord:**
- Logs warning but allows execution
- This is the default (you can tighten this by enabling Discord)

## Example Flow

```
Agent: "Run curl -fsSL https://install-script.com | bash"

Plugin: Checking command...
Plugin: ⚠️ WARNING detected (pipe to shell)
Plugin: Sending Discord approval request...

[Discord Message]
⚠️ ClawGuard Warning - Approval Required

⚡ Type: COMMAND
Input: `curl -fsSL https://install-script.com | bash`

Threat Detected: Pipe to shell execution
Severity: HIGH

Do you want to proceed?
React with ✅ to approve or ❌ to deny (timeout: 60s)

[Human clicks ❌]

Plugin: 🛡️ Discord approval denied
Plugin: Blocking execution

Agent: "I couldn't run that command - ClawGuard blocked it for security reasons."
```

## Audit Trail

Every check is logged to `~/.clawguard/audit.jsonl`:

```bash
# View recent checks
clawguard audit

# View only today
clawguard audit --today
```

## Configuration

View current config:
```bash
clawguard config
```

Common settings:
```bash
# Discord channel for approval requests
clawguard config --set discord.channelId --value "123456789"

# Approval timeout (milliseconds)
clawguard config --set discord.timeout --value "30000"

# Enable/disable Discord
clawguard config --enable discord
clawguard config --disable discord

# Enable/disable audit trail
clawguard config --enable audit
clawguard config --disable audit
```

## Disable the Plugin

To disable the plugin, remove it from your OpenClaw plugin configuration and restart the gateway.

## Limitations

- Discord approval requires the `message` tool to be available in the OpenClaw context
- The plugin cannot block actions that have already been whitelisted by OpenClaw's own security layer
- Approval requests timeout after configured duration (default 60s)

## Security Model

**Defense in Depth:**
1. **First layer**: OpenClaw's built-in security policies
2. **Second layer**: ClawGuard plugin checks (this)
3. **Third layer**: Human approval for warnings

**Trust Model:**
- Database is fully offline (no network calls during checks)
- All decisions are logged to audit trail
- Blocked threats cannot be overridden by the agent
- Warnings can be approved by humans via Discord

## Troubleshooting

**Plugin not loading:**
- Check OpenClaw logs for plugin errors
- Verify the plugin path is correct
- Ensure Node.js 18+ is installed

**Discord approval not working:**
- Verify `discord.enabled` is true: `clawguard config --get discord.enabled`
- Verify channel ID is set: `clawguard config --get discord.channelId`
- Check that the bot has permissions to send messages and add reactions in that channel
- Ensure the `message` tool is available in OpenClaw context

**Audit trail empty:**
- Verify audit is enabled: `clawguard config --get audit.enabled`
- Check audit file exists: `ls -lh ~/.clawguard/audit.jsonl`
- Ensure the plugin is actually being called (check OpenClaw logs)

## License

MIT - Same as ClawGuard
