# Agent-to-Human Secret Sharing Workflow

> Complete guide for OpenClaw agents to securely share secrets with humans

## Overview

This example demonstrates the complete workflow for agents to generate secrets (SSH keys, API tokens, passwords, certificates) and share them with humans using magic-wormhole.

### Why This Matters

**Problem**: Chat logs, agent responses, and audit trails often contain secrets that should never be stored in plain text.

**Solution**: Use magic-wormhole to transfer secrets using short codes. The actual secret never appears in the chat—only the transfer code.

---

## Core Pattern

### Agent Workflow

1. **Generate secret** (SSH key, API token, password, etc.)
2. **Write to temporary file** (secure, auto-cleanup)
3. **Send via wormhole**: `wormhole send --text "$SECRET"`
4. **Extract code** from output
5. **Return ONLY the code** to human (NOT the secret!)
6. **Cleanup** temporary files

### Human Workflow

1. **Receive code** from agent
2. **Run**: `wormhole receive`
3. **Enter code** when prompted
4. **Save secret** securely (password manager, keyring, etc.)
5. **Verify** secret works

---

## Complete Example Scripts

### Example 1: Generate and Send SSH Key

```bash
#!/bin/bash
# generate-ssh-key-for-human.sh

# Configuration
KEY_TYPE="ed25519"
KEY_COMMENT="deploy-key-$(date +%s)"
TEMP_DIR="/tmp"

# 1. Generate SSH key pair
echo "[INFO] Generating SSH key pair..."
ssh-keygen -t $KEY_TYPE -f "$TEMP_DIR/deploy-key" -C "$KEY_COMMENT" -N ""

# 2. Read keys
PRIVATE_KEY=$(cat "$TEMP_DIR/deploy-key")
PUBLIC_KEY=$(cat "$TEMP_DIR/deploy-key.pub")

# 3. Send private key via wormhole
echo "[INFO] Sending private key via wormhole..."
CODE=$(wormhole send --text "$PRIVATE_KEY" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 4. Validate code extraction
if [ -z "$CODE" ]; then
    echo "[ERROR] Failed to send private key"
    rm -f "$TEMP_DIR/deploy-key" "$TEMP_DIR/deploy-key.pub"
    exit 1
fi

# 5. Report to human (ONLY code and public key!)
echo ""
echo "========================================="
echo "SSH Key Generated"
echo "========================================="
echo ""
echo "PRIVATE KEY:"
echo "  Receive with: wormhole receive"
echo "  Code: $CODE"
echo ""
echo "PUBLIC KEY:"
echo "  $PUBLIC_KEY"
echo ""
echo "Instructions:"
echo "  1. Run: wormhole receive"
echo "  2. Enter code: $CODE"
echo "  3. Save private key to: ~/.ssh/deploy-key"
echo "  4. Set permissions: chmod 600 ~/.ssh/deploy-key"
echo ""

# 6. Cleanup
rm -f "$TEMP_DIR/deploy-key" "$TEMP_DIR/deploy-key.pub"
echo "[SUCCESS] SSH key sent and temporary files cleaned up."
```

### Example 2: Generate and Send API Token

```bash
#!/bin/bash
# generate-api-token-for-human.sh

# Configuration
TOKEN_LENGTH=32
TEMP_TOKEN="/tmp/api-token"

# 1. Generate random token
echo "[INFO] Generating API token..."
TOKEN=$(openssl rand -hex $TOKEN_LENGTH)
echo "$TOKEN" > "$TEMP_TOKEN"

# 2. Send via wormhole
echo "[INFO] Sending token via wormhole..."
CODE=$(wormhole send --text "$(cat $TEMP_TOKEN)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 3. Validate
if [ -z "$CODE" ]; then
    echo "[ERROR] Failed to send token"
    rm -f "$TEMP_TOKEN"
    exit 1
fi

# 4. Report
echo ""
echo "========================================="
echo "API Token Generated"
echo "========================================="
echo ""
echo "Receive with: wormhole receive"
echo "Code: $CODE"
echo ""
echo "Instructions:"
echo "  1. Run: wormhole receive"
echo "  2. Enter code: $CODE"
echo "  3. Save to your password manager"
echo "  4. Use in your application"
echo ""

# 5. Cleanup
rm -f "$TEMP_TOKEN"
echo "[SUCCESS] Token sent and temporary files cleaned up."
```

### Example 3: Generate and Send Password

```bash
#!/bin/bash
# generate-password-for-human.sh

# Configuration
PASSWORD_LENGTH=24
TEMP_PASS="/tmp/password"

# 1. Generate strong password
echo "[INFO] Generating password..."
PASSWORD=$(openssl rand -base64 $PASSWORD_LENGTH)
echo "$PASSWORD" > "$TEMP_PASS"

# 2. Send via wormhole
echo "[INFO] Sending password via wormhole..."
CODE=$(wormhole send --text "$(cat $TEMP_PASS)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 3. Validate
if [ -z "$CODE" ]; then
    echo "[ERROR] Failed to send password"
    rm -f "$TEMP_PASS"
    exit 1
fi

# 4. Report
echo ""
echo "========================================="
echo "Password Generated"
echo "========================================="
echo ""
echo "Receive with: wormhole receive"
echo "Code: $CODE"
echo ""
echo "Password length: $PASSWORD_LENGTH characters"
echo "Type: Base64-encoded random bytes"
echo ""
echo "Instructions:"
echo "  1. Run: wormhole receive"
echo "  2. Enter code: $CODE"
echo "  3. Save to password manager"
echo "  4. Change on first use (recommended)"
echo ""

# 5. Cleanup
rm -f "$TEMP_PASS"
echo "[SUCCESS] Password sent and temporary files cleaned up."
```

### Example 4: Generate Multi-Part Credentials

```bash
#!/bin/bash
# generate-credentials-for-human.sh

# Configuration
USERNAME="user-$(date +%s)"
PASSWORD_LENGTH=24
TEMP_DIR="/tmp/credentials"

# Create temp directory
mkdir -p "$TEMP_DIR"

# 1. Generate username
echo "$USERNAME" > "$TEMP_DIR/username"

# 2. Generate password
PASSWORD=$(openssl rand -base64 $PASSWORD_LENGTH)
echo "$PASSWORD" > "$TEMP_DIR/password"

# 3. Send username
echo "[INFO] Sending username..."
USER_CODE=$(wormhole send --text "$(cat $TEMP_DIR/username)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 4. Send password
echo "[INFO] Sending password..."
PASS_CODE=$(wormhole send --text "$(cat $TEMP_DIR/password)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 5. Report
echo ""
echo "========================================="
echo "Credentials Generated"
echo "========================================="
echo ""
echo "USERNAME:"
echo "  Receive: wormhole receive"
echo "  Code: $USER_CODE"
echo ""
echo "PASSWORD:"
echo "  Receive: wormhole receive"
echo "  Code: $PASS_CODE"
echo ""
echo "Instructions:"
echo "  1. Receive username: wormhole receive → $USER_CODE"
echo "  2. Receive password: wormhole receive → $PASS_CODE"
echo "  3. Both are single-use codes"
echo "  4. Use immediately"
echo ""

# 6. Cleanup
rm -rf "$TEMP_DIR"
echo "[SUCCESS] Credentials sent and temporary files cleaned up."
```

### Example 5: Complete Deployment Workflow

```bash
#!/bin/bash
# complete-deployment-workflow.sh

# Configuration
APP_NAME="myapp"
SERVER="production.example.com"
DEPLOY_USER="deploy"
TEMP_DIR="/tmp/deploy"

# Create temp directory
mkdir -p "$TEMP_DIR"

echo "========================================="
echo "Deployment Setup for $APP_NAME"
echo "========================================="
echo ""

# 1. Generate SSH key for deployment
echo "[INFO] Generating deployment SSH key..."
ssh-keygen -t ed25519 -f "$TEMP_DIR/deploy-key" -C "$DEPLOY_USER@$APP_NAME" -N ""

# 2. Send private key
echo "[INFO] Sending SSH private key..."
SSH_CODE=$(wormhole send --text "$(cat $TEMP_DIR/deploy-key)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 3. Generate database password
echo "[INFO] Generating database password..."
DB_PASS=$(openssl rand -base64 24)
echo "$DB_PASS" > "$TEMP_DIR/db-pass"

# 4. Send database password
echo "[INFO] Sending database password..."
DB_CODE=$(wormhole send --text "$(cat $TEMP_DIR/db-pass)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 5. Generate API token
echo "[INFO] Generating API token..."
API_TOKEN=$(openssl rand -hex 32)
echo "$API_TOKEN" > "$TEMP_DIR/api-token"

# 6. Send API token
echo "[INFO] Sending API token..."
API_CODE=$(wormhole send --text "$(cat $TEMP_DIR/api-token)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 7. Extract public key
PUBLIC_KEY=$(cat "$TEMP_DIR/deploy-key.pub")

# 8. Complete report
echo ""
echo "========================================="
echo "Deployment Credentials Ready"
echo "========================================="
echo ""
echo "Application: $APP_NAME"
echo "Server: $SERVER"
echo "Deploy User: $DEPLOY_USER"
echo ""
echo "SSH KEY (for server access):"
echo "  Private key code: $SSH_CODE"
echo "  Public key: $PUBLIC_KEY"
echo ""
echo "DATABASE PASSWORD:"
echo "  Receive: wormhole receive"
echo "  Code: $DB_CODE"
echo ""
echo "API TOKEN:"
echo "  Receive: wormhole receive"
echo "  Code: $API_CODE"
echo ""
echo "Instructions:"
echo "  1. Save SSH private key: ~/.ssh/$DEPLOY_USER-key"
echo "     chmod 600 ~/.ssh/$DEPLOY_USER-key"
echo ""
echo "  2. Save database password to password manager"
echo ""
echo "  3. Save API token to password manager or .env file"
echo ""
echo "  4. Add public key to server's authorized_keys:"
echo "     echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys"
echo ""
echo "  5. Test SSH access:"
echo "     ssh -i ~/.ssh/$DEPLOY_USER-key $DEPLOY_USER@$SERVER"
echo ""

# 9. Cleanup
rm -rf "$TEMP_DIR"
echo "[SUCCESS] Deployment workflow complete. All temporary files cleaned up."
```

---

## Error Handling Patterns

### Robust Script with Error Handling

```bash
#!/bin/bash
# robust-secret-generation.sh

set -e  # Exit on error

# Configuration
SECRET_TYPE="${1:-password}"  # Default: password
TEMP_SECRET="/tmp/generated-secret"

# Function to cleanup on exit
cleanup() {
    if [ -f "$TEMP_SECRET" ]; then
        rm -f "$TEMP_SECRET"
        echo "[INFO] Cleaned up temporary files"
    fi
}

# Register cleanup function
trap cleanup EXIT

# Generate secret based on type
case "$SECRET_TYPE" in
    password)
        echo "[INFO] Generating password..."
        SECRET=$(openssl rand -base64 24)
        ;;
    token)
        echo "[INFO] Generating API token..."
        SECRET=$(openssl rand -hex 32)
        ;;
    uuid)
        echo "[INFO] Generating UUID..."
        SECRET=$(uuidgen)
        ;;
    *)
        echo "[ERROR] Unknown secret type: $SECRET_TYPE"
        echo "Usage: $0 [password|token|uuid]"
        exit 1
        ;;
esac

# Save to temp file
echo "$SECRET" > "$TEMP_SECRET"

# Send via wormhole
echo "[INFO] Sending secret via wormhole..."
CODE=$(wormhole send --text "$(cat $TEMP_SECRET)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# Validate code extraction
if [ -z "$CODE" ]; then
    echo "[ERROR] Failed to send secret"
    exit 1
fi

# Report
echo ""
echo "========================================="
echo "${SECRET_TYPE^} Generated"
echo "========================================="
echo ""
echo "Receive with: wormhole receive"
echo "Code: $CODE"
echo ""

# Cleanup happens automatically via trap
echo "[SUCCESS] Secret sent."
```

---

## Integration with OpenClaw

### Pattern 1: One-Time Secret Generation

Agent responds to human request:

```bash
# Human: "I need a new API token for the staging environment"

# Agent runs:
./generate-api-token-for-human.sh

# Agent response:
# "I've generated an API token for staging. Receive with: wormhole receive"
# "Code: 7-blue-rabbit"
```

### Pattern 2: Batch Credential Generation

Agent generates multiple credentials at once:

```bash
# Human: "Set up deployment credentials for the new team"

# Agent runs:
./complete-deployment-workflow.sh

# Agent response:
# "Deployment credentials ready for myapp on production.example.com"
# ""
# "SSH Key (private): 3-noble-cactus"
# "SSH Key (public): ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA..."
# ""
# "Database password: 8-brave-dragon"
# "API token: 2-quiet-tiger"
```

### Pattern 3: Rotating Secrets

Agent rotates existing secrets:

```bash
# Human: "Rotate all production secrets"

# Agent runs:
./rotate-secrets.sh  # (not shown, but follows same pattern)

# Agent response:
# "Secret rotation complete:"
# ""
# "New database password: 5-calm-otter"
# "New API token: 9-sweet-badger"
# "New SSH key (private): 1-lucky-panda"
# "New SSH key (public): ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA..."
```

---

## Human-Side Instructions

### Receiving Secrets

```bash
# 1. Receive secret
wormhole receive
# Enter code when prompted

# 2. Save securely (choose method)

# Option A: Password manager (pass)
pass insert -m myapp/production-token
# Paste secret, Ctrl+D

# Option B: Keyring (secret-tool)
secret-tool store --label='Production Token' service myapp secret token
# Paste secret

# Option C: Secure file
cat > ~/.config/myapp/token
# Paste secret, Ctrl+D
chmod 600 ~/.config/myapp/token

# Option D: Environment file
echo "TOKEN=your-secret-here" >> ~/.env
chmod 600 ~/.env
```

### Verifying Secrets

```bash
# Test SSH key
ssh -i ~/.ssh/deploy-key user@server

# Test API token
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/me

# Test database password
psql -h db.example.com -u user -d database
# Enter password when prompted
```

---

## Best Practices for Agents

### ✅ DO

- **Return only codes**: Never return secrets in agent responses
- **Use temporary files**: Write to `/tmp/` with auto-cleanup
- **Set traps**: Use `trap` to ensure cleanup on exit/error
- **Validate output**: Check that code extraction succeeded
- **Clear instructions**: Tell humans how to receive and save secrets
- **Set permissions**: Use `chmod 600` for sensitive files

### ❌ DON'T

- **Log secrets**: Never log or print secret values
- **Reuse codes**: Generate new codes for each transfer
- **Skip cleanup**: Always remove temporary files
- **Ignore errors**: Check for and handle failures
- **Return secrets**: Only return codes to humans
- **Use weak randomness**: Use `openssl rand` or `uuidgen`, not `/dev/urandom` directly

---

## Security Checklist

- [ ] Secret generated with strong randomness
- [ ] Secret written to temporary file only
- [ ] Secret sent via wormhole (not in chat)
- [ ] Code extracted and validated
- [ ] Only code returned to human (not secret)
- [ ] Temporary files cleaned up
- [ ] Instructions provided to human
- [ ] Code shared via separate channel (recommended)

---

## One-Liner Quick Reference

```bash
# Generate password and send
openssl rand -base64 24 | tee /tmp/p | wormhole send --text "$(cat /tmp/p)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4 && rm /tmp/p

# Generate token and send
openssl rand -hex 32 | tee /tmp/t | wormhole send --text "$(cat /tmp/t)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4 && rm /tmp/t

# Generate SSH key and send
ssh-keygen -t ed25519 -f /tmp/k -N "" && CODE=$(wormhole send --text "$(cat /tmp/k)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4) && echo "Code: $CODE" && echo "Pub: $(cat /tmp/k.pub)" && rm -f /tmp/k /tmp/k.pub
```

---

## Summary

The agent-to-human secret sharing workflow ensures:

✅ **Zero exposure**: Secrets never appear in chat logs
✅ **Secure transfer**: End-to-end encrypted via PAKE protocol
✅ **Human-friendly**: Short codes are easy to share
✅ **Automatic cleanup**: Temporary files removed automatically
✅ **Error handling**: Robust validation and error reporting

**Pattern:**
```
Agent: "I've generated your secret. Receive with: wormhole receive"
       "Code: 7-blue-rabbit"

Human: wormhole receive → Enter code → Save securely
```

**Result:** Secret transferred securely, never logged, compliant with best practices. 🔐
