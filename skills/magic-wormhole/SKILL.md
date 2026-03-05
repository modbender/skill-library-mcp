---
name: magic-wormhole
description: Secure secret sharing for OpenClaw using magic-wormhole protocol
homepage: https://github.com/magic-wormhole/magic-wormhole
version: 1.0.0
metadata:
  clawdbot:
    emoji: "🔐"
    requires:
      env: []
    primaryEnv: null
    files: ["install.sh", "docs/*", "examples/*"]
  author:
    name: Stateless Collective
    url: https://stateless.id
  attribution:
    - "Created by Stateless Collective AI Committee (https://stateless.id)"
    - "Based on magic-wormhole by Brian Warner and contributors (https://github.com/magic-wormhole/magic-wormhole)"
    - "License: MIT (matches magic-wormhole)"
tags: security, secrets, encryption, privacy, tools, ssh, api-keys, credentials
---

# Magic Wormhole Skill - Secure Secret Sharing

## Description

This skill enables OpenClaw agents to securely share secrets (SSH keys, API tokens, passwords, certificates, and other sensitive data) with humans without exposing them in chat history or logs.

Uses **magic-wormhole**, a secure file and text transfer tool that employs the PAKE (Password-Authenticated Key Exchange) protocol. Secrets are transferred using human-readable codes (e.g., `7-blue-rabbit`) that enable end-to-end encrypted communication without pre-shared keys or certificates.

### Key Features

- **Zero-exposure secrets**: Secrets never appear in chat logs or agent responses
- **Simple workflow**: Share short codes instead of long secrets
- **Agent-to-human & human-to-agent**: Works in both directions
- **Scriptable & automation-friendly**: Easy to integrate into agent workflows
- **Self-hostable**: Run your own servers for production security
- **Cross-platform**: Works on Linux, macOS, Windows, and mobile

---

## Use Cases

### When to Use This Skill

✅ **Use magic-wormhole when:**

- **SSH Key Distribution**: Generate and send SSH keys to humans securely
- **API Token Transfer**: Share API tokens without exposing in chat
- **Password Rotation**: Distribute new credentials during rotation
- **Certificate Sharing**: Transfer SSL/TLS certificates or keys
- **Secret File Transfer**: Send configuration files with sensitive data
- **Team Credential Distribution**: Share temporary credentials with team members
- **Air-gapped Environments**: Transfer secrets when direct access isn't possible
- **Audit Trail Requirements**: Maintain security by keeping secrets out of logs

❌ **Don't use for:**

- Large file transfers (over ~100MB) - use dedicated file transfer tools
- Public data that isn't sensitive
- Situations requiring persistent sharing channels (wormhole codes are one-time)

### Example Scenarios

1. **Deployment Setup**: Agent generates SSH keys for server access, sends via wormhole
2. **API Integration**: Human shares API token with agent for configuration
3. **Incident Response**: Temporary credentials shared with security team
4. **Onboarding**: New team member receives access keys via secure transfer
5. **Secret Rotation**: Automated password rotation with secure distribution

---

## Prerequisites

### Required Tools

- **wormhole CLI** (magic-wormhole): Python-based secure transfer tool
- **bash** or compatible shell: For running installation and example scripts
- **OpenClaw Agent**: With access to shell execution (`exec` tool)

### Platform Support

| Platform | Installation Method | Tested |
|----------|---------------------|--------|
| Linux (Debian/Ubuntu) | `apt`, `snap`, `pip` | ✅ |
| Linux (Fedora) | `dnf`, `pip` | ✅ |
| Linux (openSUSE) | `zypper`, `pip` | ✅ |
| macOS | Homebrew, `pip` | ✅ |
| Windows | `pip` | ⚠️ Limited |

### Network Requirements

- **Outbound HTTPS**: To connect to default rendezvous server (`relay.magic-wormhole.io`)
- **WebSocket Support**: For relay communication
- **Optional**: Direct P2P connections (if NAT allows)

---

## Installation

### Method 1: Automated Script (Recommended)

Run the installation script included with this skill:

```bash
cd /data/.openclaw/workspace/skills/magic-wormhole
./install.sh
```

The script will:
1. Detect your package manager (apt, dnf, zypper, brew, pip)
2. Install `magic-wormhole` if not present
3. Verify installation
4. Print success message with version info

### Method 2: Manual Installation

#### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install magic-wormhole
```

#### Linux (Fedora)

```bash
sudo dnf install magic-wormhole
```

#### Linux (Other Distros)

```bash
pip install --user magic-wormhole
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### macOS

```bash
brew install magic-wormhole
```

### Verification

Check that installation succeeded:

```bash
wormhole --version
# Should output: magic-wormhole X.X.X
```

### Self-Hosting (Optional)

For production security, host your own relay servers:

```bash
pip install magic-wormhole-server
wormhole-server start --rendezvous-relay=ws://0.0.0.0:4000/v1 \
  --transit-relay=tcp:0.0.0.0:4001
```

Then use with `--server` flag:

```bash
wormhole send --server=ws://your-server:4000/v1 filename
```

---

## Usage

### Basic Pattern: Agent Sends Secret to Human

**Workflow:**
1. Agent generates secret (SSH key, API token, password)
2. Agent sends via `wormhole send --text "$SECRET"`
3. Agent extracts code from output
4. Agent returns **only the code** to human
5. Human runs `wormhole receive` and enters code

**Example Script:**

```bash
#!/bin/bash
# Generate SSH key and send securely

# 1. Generate key
ssh-keygen -t ed25519 -f /tmp/key -N ""

# 2. Send via wormhole
CODE=$(wormhole send --text "$(cat /tmp/key)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 3. Return only the code (NOT the secret!)
echo "I've generated a new SSH key. Receive it with: wormhole receive"
echo "Code: $CODE"

# 4. Cleanup
rm -f /tmp/key /tmp/key.pub
```

**Human receives:**
```bash
wormhole receive
# Enter: 7-blue-rabbit
# Save the key
```

### Basic Pattern: Human Sends Secret to Agent

**Workflow:**
1. Human initiates: `wormhole send --text "my-secret"`
2. Human shares code with agent
3. Agent runs: `wormhole receive <<< "$CODE"`
4. Agent stores secret securely

**Example Script:**

```bash
#!/bin/bash
# Receive secret from human and store

# 1. Receive secret
wormhole receive <<< "$CODE" > /tmp/secret

# 2. Store securely (example: password manager)
pass insert -m api/production-key < /tmp/secret

# 3. Cleanup
rm -f /tmp/secret
echo "Secret stored securely."
```

### Core Commands

#### Sending Secrets

```bash
# Send text/secret
wormhole send --text "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5..."

# Send file
wormhole send ~/.ssh/id_rsa

# Send directory
wormhole send ~/.ssh/

# Send from clipboard (Linux)
xclip -o | wormhole send --text "$(cat)"

# Send from clipboard (macOS)
pbpaste | wormhole send --text "$(cat)"
```

#### Receiving Secrets

```bash
# Interactive
wormhole receive
# Enter code when prompted

# Non-interactive
echo "7-blue-rabbit" | wormhole receive

# From argument
wormhole receive 7-blue-rabbit > output.txt
```

### Extracting Codes Programmatically

```bash
# Extract code from output
CODE=$(wormhole send --text "$SECRET" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# Verify extraction
if [ -z "$CODE" ]; then
    echo "ERROR: Failed to extract code"
    exit 1
fi
echo "Code: $CODE"
```

### Batch Distribution

```bash
#!/bin/bash
# Send multiple secrets to team

# Send username
USER_CODE=$(wormhole send --text "$DB_USER" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# Send password
PASS_CODE=$(wormhole send --text "$DB_PASS" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# Report codes
echo "Database credentials ready:"
echo "Username: wormhole receive → Code: $USER_CODE"
echo "Password: wormhole receive → Code: $PASS_CODE"
```

---

## Integration

### OpenClaw Workflow Integration

This skill integrates seamlessly with OpenClaw's agent capabilities:

#### Pattern 1: Inline Shell Execution

Agent executes shell commands directly:

```bash
# Agent command
ssh-keygen -t ed25519 -f /tmp/key -N ""
wormhole send --text "$(cat /tmp/key)"
```

#### Pattern 2: Script Templates

Agent generates and executes scripts on-the-fly:

```bash
# Create temporary script
cat > /tmp/send-key.sh << 'EOF'
#!/bin/bash
SECRET="$1"
CODE=$(wormhole send --text "$SECRET" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)
echo "Code: $CODE"
EOF

chmod +x /tmp/send-key.sh
/tmp/send-key.sh "$MY_SECRET"
```

#### Pattern 3: Workflow Integration

Use as part of larger automated workflows:

```bash
#!/bin/bash
# Deployment workflow with secure credential distribution

# 1. Generate deployment credentials
USER="deploy-$(date +%s)"
PASS=$(openssl rand -base64 24)

# 2. Configure server
ssh root@server "useradd $USER && echo '$PASS' | passwd $USER --stdin"

# 3. Send credentials to team via wormhole
USER_CODE=$(wormhole send --text "$USER" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)
PASS_CODE=$(wormhole send --text "$PASS" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 4. Notify team (via message tool or other channel)
echo "Deployment credentials ready:"
echo "User: $USER_CODE"
echo "Pass: $PASS_CODE"
```

### Security Best Practices for Integration

#### DO:

✅ **Return only codes**: Never return secrets in agent responses
✅ **Use temporary files**: Write secrets to `/tmp/` with cleanup on exit
✅ **Set proper permissions**: `chmod 600` for sensitive files
✅ **Validate codes**: Check that code extraction succeeded before proceeding
✅ **Use secure storage**: Store received secrets in password managers or keyrings
✅ **Self-host for production**: Use your own relay servers for sensitive operations
✅ **Share codes separately**: Use phone, video chat, or secure messaging for codes

#### DON'T:

❌ **Log secrets**: Avoid logging secret values in debug output
❌ **Reuse codes**: Codes are single-use; generate new ones for each transfer
❌ **Share codes in same channel**: Don't send codes and discuss secrets in same chat
❌ **Ignore errors**: "Crowded"/"scary" errors indicate potential attacks
❌ **Leave temporary files**: Clean up `/tmp/` after transfers
❌ **Use short codes**: Use `--code-length 3` for sensitive secrets

### Message Tool Integration Pattern

```python
# Pseudocode: Send secure notification with code
import subprocess

def send_secret_notification(secret, channel):
    # 1. Send secret via wormhole
    result = subprocess.run(
        ["wormhole", "send", "--text", secret],
        capture_output=True,
        text=True
    )

    # 2. Extract code
    if "Wormhole code is:" in result.stderr:
        code = result.stderr.split("Wormhole code is:")[1].strip().split()[0]
    else:
        return {"error": "Failed to send secret"}

    # 3. Send notification via message tool
    message.send(
        action="send",
        channel=channel,
        message=f"I'm sending a secure secret. Receive with: wormhole receive\nCode: {code}"
    )

    return {"success": True, "code": code}
```

---

## Troubleshooting

### Common Issues

#### "Connection Refused" or "Timeout"

**Cause:** Firewall or NAT blocking connection

**Solutions:**
```bash
# Check firewall
sudo ufw allow 4000:4001/tcp

# Use custom transit relay
wormhole send --transit-relay=tcp://public-relay.magic-wormhole.io:4001 filename

# Test connectivity
ping -c 3 relay.magic-wormhole.io
nc -zv transit.magic-wormhole.io 4001
```

#### "Crowded" or "Scary" Error

**Cause:** Wrong code or active MITM attack

**Solution:**
```bash
# Verify code with recipient
# Re-send with new code
wormhole send --text "$SECRET"
```

#### "Code Not Found"

**Cause:** Code expired (single-use) or wrong server

**Solutions:**
```bash
# Generate new code
wormhole send --text "$SECRET"

# Check server
wormhole send --server=ws://relay.magic-wormhole.io:4000/v1 filename
```

#### "Permission Denied" on Receive

**Cause:** No write permission in current directory

**Solution:**
```bash
cd ~/Downloads
wormhole receive
```

#### Slow Transfers

**Cause:** Relay congestion or slow internet

**Solutions:**
```bash
# Use compression
wormhole send --zstd large-file.tar

# Use custom transit relay
wormhole send --transit-relay=tcp://fast-relay.example.com:4001 filename
```

### Debug Mode

Enable verbose output:

```bash
# Full debug logs
wormhole send --debug filename

# Save logs to file
wormhole send --debug filename 2>&1 | tee wormhole-debug.log
```

### Version Compatibility

**Check version:**
```bash
wormhole --version
```

**Update:**
```bash
pip install --upgrade magic-wormhole
# or
sudo apt update && sudo apt upgrade magic-wormhole
```

### Python Dependency Issues

```bash
# Install missing dependencies
pip install --upgrade attrs automat spake2 twisted

# Check Python version (requires 3.10+)
python3 --version
```

### Test Installation

```bash
# Test with dummy secret
echo "test" | wormhole send --text "$(cat)"
# Should output: "Wormhole code is: X-word-word"
```

---

## Security Notes

### How Magic Wormhole Works

1. **Connection Establishment**: Both parties connect to a rendezvous server
2. **Key Agreement (PAKE)**: SPAKE2 protocol establishes a 256-bit shared secret using the code
3. **Data Transfer**: All traffic is end-to-end encrypted using NaCl/libsodium

### Security Properties

| Threat | Protection |
|--------|------------|
| Man-in-the-Middle | PAKE prevents impersonation without the code |
| Server Compromise | Servers only see encrypted data or metadata |
| Brute Force | Single-use codes + 256-bit derived key |
| Traffic Analysis | All data encrypted end-to-end |
| Replay Attacks | Codes are single-use, expire after transfer |

### Server Knowledge

- **Rendezvous Server**: Knows code, IPs, connection timing (not encryption keys or plaintext)
- **Transit Relay**: Knows encrypted data blobs (not encryption keys or plaintext)

### Recommendations

- Use `--code-length 3` for highly sensitive secrets (~4M combinations)
- Self-host servers for production or regulated environments
- Share codes via out-of-band channel (phone, video chat, Signal)
- Verify code with recipient before/after transfer
- Use Tor for anonymity when needed: `wormhole send --tor filename`

---

## Examples

See the `examples/` directory for detailed usage examples:

- **ssh-key-sharing.md**: Generating and distributing SSH keys
- **api-token-sharing.md**: Secure API token transfer patterns
- **agent-to-human.md**: Complete agent-to-human secret sharing workflow

---

## Additional Documentation

- **docs/advanced-usage.md**: Advanced features and customization options

---

## Resources

### Official Links

- **GitHub**: https://github.com/magic-wormhole/magic-wormhole
- **Documentation**: https://magic-wormhole.readthedocs.io/
- **Protocol Spec**: https://github.com/magic-wormhole/magic-wormhole-protocols

### Default Servers

- **Rendezvous**: `relay.magic-wormhole.io:4000`
- **Transit**: `transit.magic-wormhole.io:4001`

### Community

- **IRC**: `#magic-wormhole` on Libera.chat
- **Mailing List**: magic-wormhole@lists.sourceforge.net

---

## License

This skill documentation is provided for use with OpenClaw deployments.

Magic Wormhole itself is licensed under the MIT License: https://github.com/magic-wormhole/magic-wormhole/blob/main/LICENSE
