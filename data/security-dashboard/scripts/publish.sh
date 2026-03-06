#!/bin/bash
# Publish Security Dashboard to ClawdHub with proper metadata

VERSION="1.2.2"
SKILL_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CHANGELOG="Real-time security monitoring dashboard for OpenClaw and Linux server infrastructure.

## What's New in v1.2.1
- Fixed ClawdHub metadata display
- Updated publish script with proper changelog format

## Security Features
- Monitors 7 critical security areas (gateway, network, SSH, firewall, fail2ban, resources)
- 4x daily automated checks with instant alerts
- Runs as dedicated user with limited privileges (recommended)
- Systemd hardening (NoNewPrivileges, ProtectSystem, PrivateTmp)
- Localhost-only binding (127.0.0.1) - secure by default

## Installation
\`\`\`bash
cd skills/security-dashboard
sudo ./scripts/install.sh
\`\`\`

Access via SSH port forwarding for maximum security."

TAGS="security,monitoring,devops,infrastructure,dashboard,latest"

echo "Publishing Security Dashboard v$VERSION to ClawdHub..."
echo ""

clawdhub publish "$SKILL_PATH" \
  --slug security-dashboard \
  --name "Security Dashboard" \
  --version "$VERSION" \
  --changelog "$CHANGELOG" \
  --tags "$TAGS"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Successfully published Security Dashboard v$VERSION"
    echo "View at: https://clawhub.ai/vegasbrianc/security-dashboard"
else
    echo ""
    echo "❌ Publish failed with exit code $EXIT_CODE"
    exit $EXIT_CODE
fi
