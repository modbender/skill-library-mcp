# API Token Sharing Example

> Securely transfer API tokens, API keys, and credentials using magic-wormhole

## Scenario

API tokens, secrets, and credentials need to be shared between humans and agents without exposing them in chat history or logs.

## Pattern 1: Human Sends Token to Agent

Human shares an API token with the agent for configuration or automation.

### Human Side: Send Token

**Interactive:**
```bash
# Send token interactively
wormhole send --text "sk-1234567890abcdef"
# Output: Wormhole code is: 3-noble-cactus
```

**From clipboard:**
```bash
# Linux
xclip -o | wormhole send --text "$(cat)"

# macOS
pbpaste | wormhole send --text "$(cat)"
```

**From file:**
```bash
# Token stored in file
cat ~/.api-token | wormhole send --text "$(cat)"
```

### Human communicates code to agent:
```
"I'm sending the API token via wormhole. Code: 3-noble-cactus"
```

### Agent Side: Receive and Store Token

```bash
#!/bin/bash
# receive-and-store-token.sh

CODE="$1"  # Passed from human: 3-noble-cactus
TEMP_TOKEN="/tmp/api-token"
TOKEN_FILE="$HOME/.config/myapp/token"

# 1. Receive token
echo "[INFO] Receiving API token..."
wormhole receive <<< "$CODE" > "$TEMP_TOKEN"

# Check if token was received
if [ ! -s "$TEMP_TOKEN" ]; then
    echo "[ERROR] Failed to receive token"
    exit 1
fi

# 2. Store securely (choose your method)

# Option A: Store in password manager (pass)
if command -v pass &> /dev/null; then
    echo "[INFO] Storing in password manager..."
    pass insert -m api/production-token < "$TEMP_TOKEN"
    echo "[SUCCESS] Token stored in password manager"

# Option B: Store in keyring (secret-tool)
elif command -v secret-tool &> /dev/null; then
    echo "[INFO] Storing in keyring..."
    SECRET=$(cat "$TEMP_TOKEN")
    secret-tool store --label='API Token' service myapp secret api-token <<< "$SECRET"
    echo "[SUCCESS] Token stored in keyring"

# Option C: Store in secure file (chmod 600)
else
    echo "[INFO] Storing in secure file..."
    mkdir -p "$(dirname "$TOKEN_FILE")"
    cp "$TEMP_TOKEN" "$TOKEN_FILE"
    chmod 600 "$TOKEN_FILE"
    echo "[SUCCESS] Token stored in: $TOKEN_FILE"
fi

# 3. Cleanup
rm -f "$TEMP_TOKEN"
echo "[INFO] Cleanup complete."
```

---

## Pattern 2: Agent Sends Token to Human

Agent generates or retrieves an API token and shares it with a human.

### Agent Side: Generate/Retrieve and Send Token

```bash
#!/bin/bash
# generate-and-send-token.sh

TEMP_TOKEN="/tmp/api-token"

# Option A: Generate new token (example with fictional API)
echo "[INFO] Generating new API token..."
TOKEN=$(openssl rand -hex 32)
echo "$TOKEN" > "$TEMP_TOKEN"

# Option B: Retrieve from storage (example with pass)
if command -v pass &> /dev/null; then
    echo "[INFO] Retrieving token from password manager..."
    pass api/production-token > "$TEMP_TOKEN"
fi

# Option C: Extract from config file (be careful with secrets!)
# cat ~/.config/myapp/secret > "$TEMP_TOKEN"

# Send token via wormhole
echo "[INFO] Sending token via wormhole..."
CODE=$(wormhole send --text "$(cat $TEMP_TOKEN)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# Check if code extraction succeeded
if [ -z "$CODE" ]; then
    echo "[ERROR] Failed to send token"
    rm -f "$TEMP_TOKEN"
    exit 1
fi

# Report to human (only the code!)
echo ""
echo "========================================="
echo "API Token Ready!"
echo "========================================="
echo ""
echo "Receive with: wormhole receive"
echo "Code: $CODE"
echo ""
echo "Instructions:"
echo "  1. Run: wormhole receive"
echo "  2. Enter: $CODE"
echo "  3. Save token to your password manager or .env file"
echo ""

# Cleanup
rm -f "$TEMP_TOKEN"
echo "[SUCCESS] Token sent and temporary files cleaned up."
```

### Human Side: Receive Token

```bash
# Receive token
wormhole receive
# Enter code: 3-noble-cactus

# Save securely

# Option A: Password manager (pass)
pass insert -m api/production-token
# Paste token, Ctrl+D

# Option B: Environment file
echo "API_TOKEN=sk-1234567890abcdef" >> ~/.env
chmod 600 ~/.env

# Option C: Keyring
secret-tool store --label='API Token' service myapp secret api-token
# Paste token
```

---

## Pattern 3: Batch Token Distribution

Distribute multiple tokens to team members or services.

```bash
#!/bin/bash
# distribute-tokens-to-team.sh

# Token definitions
declare -A TOKENS=(
    ["alice-db"]="db_user_alice_password"
    ["bob-api"]="api_bob_secret_key"
    ["charlie-s3"]="s3_access_key"
)

TEMP_DIR="/tmp/tokens"

# Create temporary directory
mkdir -p "$TEMP_DIR"

# Generate and send each token
for KEY in "${!TOKENS[@]}"; do
    echo "[INFO] Processing token for: $KEY"

    # Generate random token
    TOKEN=$(openssl rand -hex 32)
    echo "$TOKEN" > "$TEMP_DIR/$KEY"

    # Send via wormhole
    CODE=$(wormhole send --text "$(cat $TEMP_DIR/$KEY)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

    # Report
    echo ""
    echo "Token: $KEY"
    echo "  Code: $CODE"
    echo ""

    # Cleanup
    rm -f "$TEMP_DIR/$KEY"
done

# Cleanup directory
rmdir "$TEMP_DIR"
echo "[SUCCESS] All tokens distributed!"
```

---

## Pattern 4: Token Rotation

Rotate API tokens while maintaining security.

```bash
#!/bin/bash
# rotate-api-token.sh

SERVICE="myapp"
OLD_TOKEN_FILE="/tmp/old-token"
NEW_TOKEN_FILE="/tmp/new-token"

# 1. Generate new token
echo "[INFO] Generating new token..."
NEW_TOKEN=$(openssl rand -hex 32)
echo "$NEW_TOKEN" > "$NEW_TOKEN_FILE"

# 2. Save old token for reference (temporary)
if [ -f "$HOME/.config/$SERVICE/token" ]; then
    cp "$HOME/.config/$SERVICE/token" "$OLD_TOKEN_FILE"
fi

# 3. Send new token via wormhole
echo "[INFO] Sending new token..."
CODE=$(wormhole send --text "$(cat $NEW_TOKEN_FILE)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 4. Update local storage
echo "[INFO] Updating local storage..."
mkdir -p "$HOME/.config/$SERVICE"
cp "$NEW_TOKEN_FILE" "$HOME/.config/$SERVICE/token"
chmod 600 "$HOME/.config/$SERVICE/token"

# 5. Report
echo ""
echo "========================================="
echo "Token Rotation Complete!"
echo "========================================="
echo ""
echo "NEW TOKEN:"
echo "  Receive with: wormhole receive"
echo "  Code: $CODE"
echo ""
echo "OLD TOKEN (for reference):"
if [ -f "$OLD_TOKEN_FILE" ]; then
    echo "  $(cat $OLD_TOKEN_FILE)"
else
    echo "  (no previous token found)"
fi
echo ""
echo "Next steps:"
echo "  1. Receive new token with wormhole"
echo "  2. Update your application/configuration"
echo "  3. Verify it works"
echo "  4. Old token will be invalid after verification"
echo ""

# 6. Cleanup (cleanup old token after 5 minutes)
(
    sleep 300
    rm -f "$OLD_TOKEN_FILE" "$NEW_TOKEN_FILE"
    echo "[INFO] Cleanup: Temporary token files removed"
) &

echo "[SUCCESS] Token rotated successfully."
```

---

## Pattern 5: Multi-Part Credentials

Send username and password as separate transfers for extra security.

```bash
#!/bin/bash
# send-credentials-separately.sh

USERNAME="deploy-user-$(date +%s)"
PASSWORD=$(openssl rand -base64 24)

# Send username
echo "[INFO] Sending username..."
USER_CODE=$(wormhole send --text "$USERNAME" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# Send password
echo "[INFO] Sending password..."
PASS_CODE=$(wormhole send --text "$PASSWORD" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# Report
echo ""
echo "========================================="
echo "Credentials Ready!"
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
echo "  1. Receive username with code: $USER_CODE"
echo "  2. Receive password with code: $PASS_CODE"
echo "  3. Use immediately (both are single-use)"
echo ""
```

### Human receives both:
```bash
# Receive username
wormhole receive
# Enter: 3-noble-cactus
# Save: USERNAME=deploy-user-1737480000

# Receive password
wormhole receive
# Enter: 7-blue-rabbit
# Save: PASSWORD=abc123xyz...
```

---

## Integration Examples

### Example 1: Store in Environment Variables

```bash
#!/bin/bash
# store-token-in-env.sh

TOKEN="$1"
ENV_FILE="$HOME/.config/myapp/.env"

# Create .env file if it doesn't exist
mkdir -p "$(dirname "$ENV_FILE")"
touch "$ENV_FILE"
chmod 600 "$ENV_FILE"

# Check if token already exists
if grep -q "^API_TOKEN=" "$ENV_FILE"; then
    # Replace existing token
    sed -i "s/^API_TOKEN=.*/API_TOKEN=$TOKEN/" "$ENV_FILE"
    echo "[INFO] Updated existing API token"
else
    # Add new token
    echo "API_TOKEN=$TOKEN" >> "$ENV_FILE"
    echo "[INFO] Added new API token"
fi

echo "[SUCCESS] Token stored in: $ENV_FILE"
```

### Example 2: Configure AWS CLI

```bash
#!/bin/bash
# configure-aws-with-token.sh

ACCESS_KEY="$1"
SECRET_KEY="$2"

# Configure AWS CLI
aws configure set aws_access_key_id "$ACCESS_KEY"
aws configure set aws_secret_access_key "$SECRET_KEY"
aws configure set default.region us-east-1

echo "[SUCCESS] AWS CLI configured"
```

### Example 3: Configure Git Credential Helper

```bash
#!/bin/bash
# configure-git-token.sh

TOKEN="$1"
REPO="https://github.com/org/repo.git"

# Configure credential helper
git config --global credential.helper store

# Store credentials (format: https://user:token@github.com)
echo "https://oauth2:$TOKEN@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

echo "[SUCCESS] Git configured with token"
echo "[INFO] You can now: git clone $REPO"
```

---

## Security Best Practices

### 1. Never Log Tokens

```bash
# ❌ BAD - Token appears in logs
echo "Token: $TOKEN"

# ✅ GOOD - Token is hidden
echo "Token sent via wormhole. Code: $CODE"
```

### 2. Use Temporary Files with Cleanup

```bash
# Use temp directory
TEMP_TOKEN=$(mktemp)
trap "rm -f $TEMP_TOKEN" EXIT  # Auto-cleanup on exit

echo "$TOKEN" > "$TEMP_TOKEN"
# Use token...
# Cleanup happens automatically
```

### 3. Set Proper File Permissions

```bash
# Private files: 600 (read/write by owner only)
chmod 600 ~/.api-token

# Directory: 700 (only owner can access)
chmod 700 ~/.config/myapp

# Never use 777!
```

### 4. Store in Password Managers

```bash
# pass (Git-based password manager)
pass insert -m api/production-token

# secret-tool (GNOME Keyring)
secret-tool store --label='API Token' service myapp secret api-token

# bw (Bitwarden CLI)
bw get password "API Token" > /tmp/token
```

### 5. Rotate Regularly

```bash
#!/bin/bash
# Scheduled token rotation (run via cron)

# Generate new token
NEW_TOKEN=$(openssl rand -hex 32)

# Update in application
curl -X PUT https://api.example.com/token \
  -H "Authorization: Bearer $OLD_TOKEN" \
  -d '{"token": "'$NEW_TOKEN'"}'

# Send new token to team
CODE=$(wormhole send --text "$NEW_TOKEN" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)
echo "New token code: $CODE"
```

---

## Common Token Formats

### GitHub Personal Access Token
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Stripe API Key
```
sk_live_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### AWS Access Key
```
AKIAIOSFODNN7EXAMPLE
```

### JWT Token
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Generic API Key
```
sk-1234567890abcdefghijklmnopqrstuv
```

---

## Troubleshooting

### "Token doesn't work"

**Cause**: Token was corrupted during transfer or copy-paste

**Solution**:
```bash
# Verify token format
echo "$TOKEN" | wc -c  # Check length
echo "$TOKEN" | base64 -d  # Validate if base64

# Re-send token
wormhole send --text "$TOKEN"
```

### "Unauthorized" after receiving token

**Cause**: Wrong token or token expired

**Solution**:
```bash
# Verify token with API (example)
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/me

# If fails, request new token
```

### "Token visible in process list"

**Cause**: Token passed as command-line argument

**Solution**:
```bash
# ❌ BAD - Visible in ps
curl -H "Authorization: Bearer $TOKEN" https://api.example.com

# ✅ GOOD - Hidden from ps
echo "$TOKEN" | curl -H "Authorization: Bearer @-" https://api.example.com
```

---

## One-Liner Quick Reference

```bash
# Send token quickly
echo "sk-1234567890" | wormhole send --text "$(cat)"

# Receive and store in .env
wormhole receive >> ~/.env && chmod 600 ~/.env

# Generate and send random token
openssl rand -hex 32 | wormhole send --text "$(cat)"

# Send from clipboard (Linux)
xclip -o | wormhole send --text "$(cat)"

# Send from clipboard (macOS)
pbpaste | wormhole send --text "$(cat)"
```

---

## Summary

Using magic-wormhole for API token sharing ensures:

✅ **Tokens never appear in chat logs or audit trails**
✅ **Secure end-to-end encrypted transfer**
✅ **Human-readable codes for verification**
✅ **Automatic cleanup of temporary files**
✅ **Compliance with security best practices**

Pattern:
```
Human: "Sending API token via wormhole. Code: 3-noble-cactus"

Agent: wormhole receive → Enter code → Store securely
```

No secrets in chat. Secure transfer. Done. 🔐
