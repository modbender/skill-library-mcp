# Troubleshooting Guide

Common issues encountered during OpenClaw AWS deployment and their solutions.

## Instance Issues

### OOM (Out of Memory) on t4g.micro
**Symptom:** Gateway fails to start, heap allocation errors in logs
```
FATAL ERROR: Reached heap limit Allocation failed
```

**Solution:** Upgrade to t4g.medium (4GB RAM minimum — t4g.small OOMs during npm install + gateway startup)
```bash
aws ec2 stop-instances --instance-ids $INSTANCE_ID
aws ec2 modify-instance-attribute --instance-id $INSTANCE_ID --instance-type t4g.medium
aws ec2 start-instances --instance-ids $INSTANCE_ID
```

## Gateway Startup Issues

### "systemctl --user unavailable" Error
**Symptom:** 
```
Gateway service check failed: Error: systemctl --user unavailable: Failed to connect to bus
```

**Cause:** `openclaw gateway start` tries to create a user-level systemd service

**Solution:** Use foreground mode instead:
```bash
exec openclaw gateway run --allow-unconfigured
```

### "Missing config" Error
**Symptom:**
```
Missing config. Run `openclaw setup` or set gateway.mode=local
```

**Solution:** Ensure `openclaw.json` (not config.yaml) has:
```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "your-secret-token"
    }
  }
}
```

### "Port already in use" Error
**Symptom:**
```
Port 18789 is already in use.
Gateway already running locally.
```

**Solution:** Kill existing gateway before restart:
```bash
sudo pkill -f openclaw-gateway
sleep 2
sudo systemctl restart openclaw
```

### Invalid gateway.auth.mode
**Symptom:**
```
gateway.auth.mode: Invalid input
```

**Solution:** `mode: "none"` is not valid. Use:
```json
"auth": {
  "mode": "token",
  "token": "your-secret-token"
}
```

## Telegram Issues

### Telegram Not Showing in Channels
**Symptom:** `openclaw status` shows empty Channels table

**Solution:** Enable the plugin explicitly:
```json
{
  "plugins": {
    "entries": {
      "telegram": {
        "enabled": true
      }
    }
  }
}
```

### Messages Not Being Received
**Symptom:** Bot online but ignores messages

**Cause:** `dmPolicy: "allowlist"` with no users configured

**Solution:** Use pairing mode:
```json
{
  "channels": {
    "telegram": {
      "dmPolicy": "pairing"
    }
  }
}
```

### Pairing Required
**Symptom:** Bot responds with pairing code

**Solution:** Approve the pairing:
```bash
openclaw pairing approve telegram <PAIRING_CODE>
```

## Model Issues

### "Unknown model" Error

**Cause 1:** Wrong provider prefix
- ❌ `bedrock/model-id`
- ✅ `amazon-bedrock/model-id`

**Cause 2:** Model not enabled in Bedrock console
- Go to AWS Bedrock Console → Model Access
- Enable the model you want to use

**Cause 3:** Anthropic use case form not submitted
- Anthropic models require use case details
- Fill out the form in Bedrock console

**Cause 4:** Model discovery failed
- Manually configure model in `models.providers`:
```json
{
  "models": {
    "providers": {
      "amazon-bedrock": {
        "baseUrl": "https://bedrock-runtime.us-east-1.amazonaws.com",
        "api": "bedrock-converse-stream",
        "auth": "aws-sdk",
        "models": [
          {
            "id": "mistral.mistral-large-2402-v1:0",
            "name": "Mistral Large",
            "input": ["text"],
            "contextWindow": 32000,
            "maxTokens": 8192
          }
        ]
      }
    }
  }
}
```

### "Model doesn't support system messages"
**Symptom:** Error with Mistral 7B or similar small models

**Solution:** Use a larger model (Mistral Large, Claude, Gemini Flash)

### "Model doesn't support tool use in streaming mode"
**Symptom:** Error when agent tries to use tools

**Solution:** Disable streaming:
```json
{
  "channels": {
    "telegram": {
      "streamMode": "off"
    }
  }
}
```

## Authentication Issues

### "No API key found for provider"
**Symptom:**
```
No API key found for provider "google"
```

**Solution:** Create auth-profiles.json:
```bash
mkdir -p ~/.openclaw/agents/main/agent
cat > ~/.openclaw/agents/main/agent/auth-profiles.json << 'EOF'
{
  "version": 1,
  "profiles": {
    "google:default": {
      "type": "token",
      "provider": "google",
      "token": "YOUR_API_KEY"
    }
  }
}
EOF
```

### Environment Variables Not Picked Up
**Symptom:** Env vars set in startup script not available to gateway

**Solution:** Use systemd EnvironmentFile:
```bash
# Create env file
echo "GEMINI_API_KEY=your-key" | sudo tee /etc/openclaw/env
sudo chmod 600 /etc/openclaw/env

# Add to systemd service (under [Service])
EnvironmentFile=/etc/openclaw/env

# Reload
sudo systemctl daemon-reload
sudo systemctl restart openclaw
```

## AWS/IAM Issues

### Bedrock Access Denied
**Symptom:**
```
AccessDeniedException: not authorized to perform: bedrock:ListFoundationModels
```

**Solution:** Add Bedrock permissions to IAM role:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["bedrock:*"],
      "Resource": "*"
    }
  ]
}
```

### SSM Parameter Access Denied
**Symptom:** Can't retrieve secrets from SSM

**Solution:** Add SSM permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters"
      ],
      "Resource": "arn:aws:ssm:REGION:ACCOUNT:parameter/starfish/*"
    }
  ]
}
```

## Rate Limits

### Gemini 429 Quota Exceeded
**Symptom:**
```
You exceeded your current quota
```

**Cause:** Free tier limits (15 RPM, 1M tokens/day)

**Solution:**
1. Wait 1-2 minutes for reset
2. Or enable billing in Google AI Studio
3. Or switch to Bedrock model

## Quick Diagnostic Commands

```bash
# Check service status
sudo systemctl status openclaw

# View recent logs
sudo journalctl -u openclaw -n 50 --no-pager

# Check gateway status
openclaw status --deep

# List available models
openclaw models list

# Check auth profiles
cat ~/.openclaw/agents/main/agent/auth-profiles.json

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Test Gemini API key
curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_KEY"
```

## Issues Added 2026-02-15

### #19: ReadWritePaths=/tmp/openclaw + PrivateTmp Conflict
**Symptom:**
```
openclaw.service: Failed to set up mount namespacing: /run/systemd/unit-root/tmp/openclaw: No such file or directory
```

**Cause:** `ReadWritePaths=/tmp/openclaw` + `PrivateTmp=true` creates a namespace conflict when the directory doesn't exist.

**Solution:** Remove `ReadWritePaths=/tmp/openclaw` from systemd service. `PrivateTmp=true` handles temp isolation.

Better yet, use a simplified systemd service without `ProtectHome`, `ProtectSystem=strict`, or `ReadWritePaths` — these cause more issues than they solve in this context.

### #20: npm install openclaw Gets Placeholder Package
**Symptom:**
```
openclaw@0.0.1 installed
```

**Cause:** There's a placeholder package `openclaw@0.0.1` on npm. Bare `npm install -g openclaw` may resolve to it.

**Solution:** Always use version specifier:
```bash
npm install -g openclaw@latest
```

### #21: npm install Fails — git Not Found
**Symptom:**
```
npm error code ENOENT
npm error syscall spawn git
npm error path git
npm error An unknown git error occurred
```

**Cause:** OpenClaw has git-based dependencies. AL2023 minimal doesn't include git.

**Solution:** Install git before npm:
```bash
dnf install -y git
npm install -g openclaw@latest
```

### #22: Node 20 Not Supported
**Symptom:**
```
openclaw requires Node >=22.12.0.
Detected: node 20.20.0
```

**Cause:** OpenClaw 2026.x requires Node.js 22+.

**Solution:** Install Node 22.14.0 or later.

### #23: NodeSource setup_22.x Doesn't Work on AL2023 ARM64
**Symptom:** After running `curl -fsSL https://rpm.nodesource.com/setup_22.x | bash -`, `dnf install nodejs` still installs Node 20.

**Cause:** NodeSource repository may not have Node 22 packages for AL2023 ARM64, or the repo configuration doesn't override existing packages.

**Solution:** Install Node.js from official tarball:
```bash
curl -fsSL "https://nodejs.org/dist/v22.14.0/node-v22.14.0-linux-arm64.tar.xz" -o node.tar.xz
tar -xf node.tar.xz -C /usr/local --strip-components=1
rm node.tar.xz
```

### #24: t4g.small (2GB) Still OOMs During OpenClaw Startup
**Symptom:**
```
FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
v8::internal::Heap::CollectGarbage...
```

**Cause:** OpenClaw 2026.x + npm install + gateway startup exceeds 2GB RAM on t4g.small.

**Solution:** Use t4g.medium (4GB RAM). Cost increase ~$12/mo but necessary for reliability.

Alternative (not recommended): Add swap space, but this slows everything down on EBS.
