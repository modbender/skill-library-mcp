# Magic Wormhole - Secure Secret Sharing for OpenClaw

> Share secrets securely without exposing them in chat history

---

## What is Magic Wormhole?

Magic Wormhole is a secure file and text transfer tool that uses human-readable codes to establish end-to-end encrypted connections. Instead of pasting sensitive data in chat, you exchange short codes like `7-blue-rabbit` to transfer secrets safely.

### Why It Matters for OpenClaw

**Problem**: Chat logs and agent responses often contain secrets (SSH keys, API tokens, passwords) that should never be stored in plain text.

**Solution**: Magic Wormhole enables agents to share secrets using short codes instead. The actual secret never appears in chat—only the transfer code.

### Example: Before vs After

**❌ Before (insecure):**
```
Agent: Here's your SSH key:
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICz9v9Y4bX9q...
```

**✅ After (secure):**
```
Agent: I'll send you the SSH key via wormhole. Code: 7-blue-rabbit
```

The human runs `wormhole receive`, enters the code, and receives the key securely. The key never appears in the chat log.

---

## How It Works

1. **Agent generates secret** (SSH key, API token, password)
2. **Agent sends via wormhole**: `wormhole send --text "$SECRET"`
3. **Agent extracts code**: Gets a short code like `7-blue-rabbit`
4. **Agent returns only the code** (NOT the secret!)
5. **Human receives**: `wormhole receive` → enters code → gets secret

### Security Model

- **PAKE Protocol**: Uses Password-Authenticated Key Exchange (SPAKE2)
- **End-to-end Encryption**: 256-bit symmetric keys via NaCl/libsodium
- **Single-use Codes**: Each code works once, then expires
- **No Server Knowledge**: Relay servers see only encrypted data, not secrets

---

## Quick Start

### 1. Install Magic Wormhole

**Linux (Debian/Ubuntu):**
```bash
sudo apt install magic-wormhole
```

**Linux (Other):**
```bash
pip install --user magic-wormhole
```

**macOS:**
```bash
brew install magic-wormhole
```

**Or use the automated installer:**
```bash
cd /data/.openclaw/workspace/skills/magic-wormhole
./install.sh
```

### 2. Verify Installation

```bash
wormhole --version
# Should output: magic-wormhole X.X.X
```

### 3. Send Your First Secret

**Agent sends secret to human:**

```bash
#!/bin/bash
# Generate and send SSH key

# 1. Generate key
ssh-keygen -t ed25519 -f /tmp/key -N ""

# 2. Send via wormhole
CODE=$(wormhole send --text "$(cat /tmp/key)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 3. Return only the code
echo "I've generated a new SSH key. Receive with: wormhole receive"
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

That's it! No secrets in chat. ✅

---

## Common Use Cases

### SSH Key Distribution

Generate SSH keys for server access and send securely:

```bash
ssh-keygen -t ed25519 -f /tmp/deploy-key -N ""
CODE=$(wormhole send --text "$(cat /tmp/deploy-key)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)
echo "Deployment key ready. Code: $CODE"
```

### API Token Transfer

**Human sends token to agent:**
```bash
# Human: Send token
wormhole send --text "sk-1234567890abcdef"
# Copy code: 3-noble-cactus
```

**Agent receives:**
```bash
# Agent: Receive and store
wormhole receive <<< "3-noble-cactus" > /tmp/token
pass insert -m api/production-key < /tmp/token
rm /tmp/token
```

### Password Rotation

Generate and distribute new passwords:

```bash
NEW_PASS=$(openssl rand -base64 24)
CODE=$(wormhole send --text "$NEW_PASS" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)
echo "New password ready. Code: $CODE"
```

### Team Credential Distribution

Send multiple secrets to a team:

```bash
#!/bin/bash
# Send database credentials

USER_CODE=$(wormhole send --text "$DB_USER" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)
PASS_CODE=$(wormhole send --text "$DB_PASS" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

echo "Database credentials:"
echo "Username: $USER_CODE"
echo "Password: $PASS_CODE"
```

---

## Core Commands

### Sending

```bash
# Send text/secret
wormhole send --text "your-secret-here"

# Send file
wormhole send filename.txt

# Send directory
wormhole send ~/.ssh/

# Send from clipboard (Linux)
xclip -o | wormhole send --text "$(cat)"

# Send from clipboard (macOS)
pbpaste | wormhole send --text "$(cat)"
```

### Receiving

```bash
# Interactive
wormhole receive
# Enter code when prompted

# Non-interactive
echo "7-blue-rabbit" | wormhole receive

# From argument
wormhole receive 7-blue-rabbit > output.txt
```

### Advanced Options

```bash
# Longer code (more secure)
wormhole send --code-length 3 filename

# Custom server
wormhole send --server=ws://your-server:4000/v1 filename

# Tor anonymity
wormhole send --tor filename

# Compression for large files
wormhole send --zstd large-file.tar

# Debug mode
wormhole send --debug filename
```

---

## Security Best Practices

### ✅ DO

- **Share codes separately**: Use phone, video chat, or secure messaging
- **Use longer codes**: `--code-length 3` for sensitive secrets
- **Self-host servers**: For production or regulated environments
- **Verify codes**: Confirm with recipient before/after transfer
- **Clean up temp files**: Remove `/tmp/` files after use
- **Store securely**: Use password managers or keyrings for received secrets

### ❌ DON'T

- **Share codes in same chat**: Don't send codes and discuss secrets together
- **Use short codes for sensitive data**: Default length is okay, longer is better
- **Ignore errors**: "Crowded"/"scary" errors indicate potential attacks
- **Log secrets**: Never log secret values in debug output
- **Leave temp files**: Clean up after transfers
- **Reuse codes**: Generate new codes for each transfer

---

## Example Workflows

### Workflow 1: "I Need SSH Access"

**Human**: "I need SSH access to the production server"

**Agent**:
```bash
ssh-keygen -t ed25519 -f /tmp/prod-key -N ""
CODE=$(wormhole send --text "$(cat /tmp/prod-key)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)
PUBLIC_KEY=$(cat /tmp/prod-key.pub)
echo "SSH key generated! Private key code: $CODE"
echo "Public key: $PUBLIC_KEY"
rm -f /tmp/prod-key /tmp/prod-key.pub
```

**Agent response**: "SSH key generated! Private key code: 7-blue-rabbit. Public key: ssh-ed25519 AAAA..."

**Human**:
```bash
wormhole receive
# Enter: 7-blue-rabbit
# Add public key to server
```

### Workflow 2: "Send Me Your API Token"

**Human**:
```bash
wormhole send --text "sk-1234567890abcdef"
# Copy code: 3-noble-cactus
```

**Human**: "Sending API token via wormhole. Code: 3-noble-cactus"

**Agent**:
```bash
wormhole receive <<< "3-noble-cactus" > /tmp/token
pass insert -m api/production-token < /tmp/token
rm /tmp/token
echo "API token stored securely."
```

### Workflow 3: Emergency Access

**Agent**:
```bash
# Generate temporary credentials
USER="emergency-$(date +%s)"
PASS=$(openssl rand -base64 32)
USER_CODE=$(wormhole send --text "$USER" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)
PASS_CODE=$(wormhole send --text "$PASS" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)
echo "Emergency credentials (valid 1 hour):"
echo "Username: $USER_CODE"
echo "Password: $PASS_CODE"
```

---

## Troubleshooting

### Connection Issues

```bash
# Test connectivity
curl -I https://relay.magic-wormhole.io/
nc -zv transit.magic-wormhole.io 4001

# Debug mode
wormhole send --debug filename 2>&1 | tee debug.log
```

### "Crowded" Error

**Cause**: Wrong code or active attack

**Solution**: Verify code and re-send with new code

### Slow Transfers

```bash
# Use compression
wormhole send --zstd large-file.tar
```

### Update Installation

```bash
pip install --upgrade magic-wormhole
# or
sudo apt update && sudo apt upgrade magic-wormhole
```

---

## More Examples

See the `examples/` directory for detailed examples:

- **ssh-key-sharing.md**: Complete SSH key generation and distribution
- **api-token-sharing.md**: Secure API token transfer patterns
- **agent-to-human.md**: Full agent-to-human workflow

Advanced usage: See `docs/advanced-usage.md`

---

## Resources

### Official Magic Wormhole

- **GitHub**: https://github.com/magic-wormhole/magic-wormhole
- **Documentation**: https://magic-wormhole.readthedocs.io/
- **Protocol**: https://github.com/magic-wormhole/magic-wormhole-protocols

### Default Servers

- **Rendezvous**: `relay.magic-wormhole.io:4000`
- **Transit**: `transit.magic-wormhole.io:4001`

### Community

- **IRC**: `#magic-wormhole` on Libera.chat
- **Mailing List**: magic-wormhole@lists.sourceforge.net

---

## Security in a Nutshell

**Protocol**: SPAKE2 PAKE + NaCl/libsodium

**What servers know**: IP addresses, codes, connection timing (not secrets)

**What attackers see**: Encrypted traffic (without code, they can't decrypt)

**Security level**: 256-bit symmetric encryption, single-use codes, audited crypto

**Recommendation**: Use this skill for any secret that shouldn't appear in logs or chat history.

---

## Remember

🔐 **Never paste secrets in chat.** Use wormhole instead.

```
❌ "Here's the key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA..."

✅ "I'll send the key via wormhole. Code: 7-blue-rabbit"
```

Keep secrets secret. Use wormhole.
