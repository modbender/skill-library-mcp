# SSH Key Sharing Example

> Generate SSH keys and distribute them securely using magic-wormhole

## Scenario

You need to generate SSH keys for a new user or service account and share the private key with the human recipient without exposing it in chat history.

## Basic SSH Key Generation and Sharing

### Agent Side: Generate and Send Key

```bash
#!/bin/bash
# generate-and-send-ssh-key.sh

# Configuration
KEY_TYPE="ed25519"
KEY_COMMENT="deploy-key-$(date +%s)"
TEMP_DIR="/tmp"

print_status() {
    echo "[INFO] $1"
}

print_success() {
    echo "[SUCCESS] $1"
}

# 1. Generate SSH key pair
print_status "Generating SSH key pair..."
ssh-keygen -t $KEY_TYPE -f "$TEMP_DIR/deploy-key" -C "$KEY_COMMENT" -N ""

# 2. Read keys into variables
PRIVATE_KEY=$(cat "$TEMP_DIR/deploy-key")
PUBLIC_KEY=$(cat "$TEMP_DIR/deploy-key.pub")

# 3. Send private key via wormhole
print_status "Sending private key via wormhole..."
CODE=$(wormhole send --text "$PRIVATE_KEY" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# Check if code extraction succeeded
if [ -z "$CODE" ]; then
    echo "[ERROR] Failed to send private key"
    rm -f "$TEMP_DIR/deploy-key" "$TEMP_DIR/deploy-key.pub"
    exit 1
fi

print_success "Private key sent successfully!"

# 4. Report to human (only the code, not the key!)
echo ""
echo "========================================="
echo "SSH Key Generated!"
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
echo "  2. Enter the code: $CODE"
echo "  3. Save the private key to: ~/.ssh/deploy-key"
echo "  4. Set permissions: chmod 600 ~/.ssh/deploy-key"
echo "  5. Add the public key to your server's authorized_keys"
echo ""

# 5. Cleanup
rm -f "$TEMP_DIR/deploy-key" "$TEMP_DIR/deploy-key.pub"
print_success "Cleanup complete."
```

### Human Side: Receive and Use Key

```bash
# 1. Receive the key
wormhole receive
# Enter the code when prompted (e.g., 7-blue-rabbit)

# 2. Save to your SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 3. Save received key
cat > ~/.ssh/deploy-key
# Paste the received private key
# Press Ctrl+D

# 4. Set proper permissions
chmod 600 ~/.ssh/deploy-key

# 5. Test the key
ssh -i ~/.ssh/deploy-key user@server
```

---

## Advanced: Multiple Key Distribution

### Generate Keys for Multiple Users

```bash
#!/bin/bash
# distribute-keys-to-team.sh

# User list
USERS=("alice" "bob" "charlie")
SERVER="production-server.example.com"
TEMP_DIR="/tmp"

print_status() {
    echo "[INFO] $1"
}

# Generate key for each user
for USER in "${USERS[@]}"; do
    print_status "Generating key for $USER..."

    # Generate key
    ssh-keygen -t ed25519 -f "$TEMP_DIR/key-$USER" -C "$USER@deploy" -N ""

    # Send private key
    PRIVATE_CODE=$(wormhole send --text "$(cat $TEMP_DIR/key-$USER)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

    # Add public key to server (requires SSH access to server)
    ssh root@$SERVER "mkdir -p /home/$USER/.ssh && echo '$(cat $TEMP_DIR/key-$USER.pub)' >> /home/$USER/.ssh/authorized_keys && chown $USER:$USER /home/$USER/.ssh/authorized_keys"

    # Report
    echo ""
    echo "User: $USER"
    echo "  Private key code: $PRIVATE_CODE"
    echo "  Public key: $(cat $TEMP_DIR/key-$USER.pub)"
    echo ""

    # Cleanup
    rm -f "$TEMP_DIR/key-$USER" "$TEMP_DIR/key-$USER.pub"
done

print_status "All keys distributed!"
```

---

## Workflow: Server Access Setup

### Complete Setup Workflow

```bash
#!/bin/bash
# setup-server-access.sh

# Configuration
USERNAME="deploy"
SERVER="production.example.com"
TEMP_DIR="/tmp"

print_status() {
    echo "[INFO] $1"
}

print_success() {
    echo "[SUCCESS] $1"
}

# 1. Create user on server (requires root access)
print_status "Creating user $USERNAME on server..."
ssh root@$SERVER "useradd -m -s /bin/bash $USERNAME"

# 2. Generate SSH key
print_status "Generating SSH key pair..."
ssh-keygen -t ed25519 -f "$TEMP_DIR/$USERNAME-key" -C "$USERNAME@$SERVER" -N ""

# 3. Send private key to human
print_status "Sending private key via wormhole..."
CODE=$(wormhole send --text "$(cat $TEMP_DIR/$USERNAME-key)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# 4. Add public key to server
print_status "Adding public key to server..."
ssh root@$SERVER "mkdir -p /home/$USERNAME/.ssh && chmod 700 /home/$USERNAME/.ssh && echo '$(cat $TEMP_DIR/$USERNAME-key.pub)' > /home/$USERNAME/.ssh/authorized_keys && chmod 600 /home/$USERNAME/.ssh/authorized_keys && chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh"

# 5. Grant sudo access (optional)
print_status "Granting sudo access..."
ssh root@$SERVER "echo '$USERNAME ALL=(ALL) NOPASSWD:/usr/bin/apt-get' >> /etc/sudoers.d/$USERNAME"

# 6. Report to human
echo ""
echo "========================================="
print_success "Server access configured!"
echo "========================================="
echo ""
echo "Server: $SERVER"
echo "Username: $USERNAME"
echo ""
echo "PRIVATE KEY:"
echo "  Receive with: wormhole receive"
echo "  Code: $CODE"
echo ""
echo "PUBLIC KEY:"
echo "  $(cat $TEMP_DIR/$USERNAME-key.pub)"
echo ""
echo "Connect with:"
echo "  ssh -i ~/.ssh/$USERNAME-key $USERNAME@$SERVER"
echo ""

# 7. Cleanup
rm -f "$TEMP_DIR/$USERNAME-key" "$TEMP_DIR/$USERNAME-key.pub"
print_success "Setup complete!"
```

---

## Security Best Practices

### 1. Use Key Comments

```bash
# Add meaningful comments to keys
ssh-keygen -t ed25519 -C "deployment@company.com" -f deploy-key -N ""
```

### 2. Set Proper Permissions

```bash
# Private keys should only be readable by owner
chmod 600 ~/.ssh/deploy-key
chmod 700 ~/.ssh

# Public keys can be world-readable
chmod 644 ~/.ssh/deploy-key.pub
```

### 3. Use Strong Key Types

```bash
# Recommended: ed25519 (modern, secure, small)
ssh-keygen -t ed25519 -f key -N ""

# Alternative: RSA 4096 (for legacy systems)
ssh-keygen -t rsa -b 4096 -f key -N ""
```

### 4. Limit Key Usage

```bash
# Add key restrictions (in authorized_keys)
command="echo 'This key can only run backups'",no-port-forwarding,no-X11-forwarding,no-pty ssh-ed25519 AAAA...

# Limit to specific hosts
from="192.168.1.100,192.168.1.101" ssh-ed25519 AAAA...
```

### 5. Rotate Keys Regularly

```bash
#!/bin/bash
# rotate-ssh-keys.sh

# Generate new key
ssh-keygen -t ed25519 -f /tmp/new-key -N ""

# Send new key
NEW_CODE=$(wormhole send --text "$(cat /tmp/new-key)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)

# Add new key to server (old key still works during transition)
ssh root@server "echo '$(cat /tmp/new-key.pub)' >> ~/.ssh/authorized_keys"

# Report
echo "New key ready. Code: $NEW_CODE"
echo "Please replace your old key with this new one."
echo "After confirming it works, remove the old key from authorized_keys."

rm -f /tmp/new-key /tmp/new-key.pub
```

---

## Troubleshooting

### "Permission denied (publickey)"

**Cause**: Server doesn't recognize the key or permissions are wrong

**Solution**:
```bash
# Check key permissions
ls -la ~/.ssh/
# Should show: -rw------- (600) for private keys

# Check if public key is on server
ssh user@server "cat ~/.ssh/authorized_keys"

# Verify key matches
ssh-keygen -y -f ~/.ssh/deploy-key  # Generate public key
# Compare with what's on server
```

### "Could not resolve hostname"

**Cause**: DNS issue or wrong hostname

**Solution**:
```bash
# Test DNS resolution
nslookup server.example.com
ping server.example.com

# Use IP address if DNS fails
ssh -i ~/.ssh/deploy-key user@192.168.1.100
```

### "Agent admitted failure to sign using the key"

**Cause**: SSH agent issue (rare with modern SSH)

**Solution**:
```bash
# Add key to ssh-agent
ssh-add ~/.ssh/deploy-key

# Or test without agent
ssh -o IdentitiesOnly=yes -i ~/.ssh/deploy-key user@server
```

---

## One-Liner Quick Reference

```bash
# Generate and send key (quick)
ssh-keygen -t ed25519 -f /tmp/k -N "" && CODE=$(wormhole send --text "$(cat /tmp/k)" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4) && echo "Code: $CODE" && echo "Pub: $(cat /tmp/k.pub)" && rm -f /tmp/k /tmp/k.pub

# Receive and save key
wormhole receive > ~/.ssh/deploy-key && chmod 600 ~/.ssh/deploy-key

# Test key
ssh -i ~/.ssh/deploy-key user@server
```

---

## Summary

Using magic-wormhole for SSH key sharing ensures:

✅ **Private keys never appear in chat logs**
✅ **Secure end-to-end encrypted transfer**
✅ **Human-readable codes for easy verification**
✅ **Automatic cleanup of temporary files**
✅ **Compliance with security best practices**

Pattern:
```
Agent: "I've generated your SSH key. Receive with: wormhole receive"
       "Code: 7-blue-rabbit"

Human: wormhole receive
       → Enter code
       → Save key securely
```

No secrets in chat. Secure transfer. Done. 🔐
