#!/bin/bash
# OpenClaw AWS Startup Script
# This script is called by systemd to start the OpenClaw gateway

set -e

# Configuration
export HOME="/home/openclaw"
export PATH="/usr/local/bin:/usr/bin:$PATH"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >&2
}

log "Starting OpenClaw startup sequence..."

# Set Node.js heap limit (1GB is safe for t4g.medium)
export NODE_OPTIONS="--max-old-space-size=1024"

# Verify Node.js (should be 22+)
NODE_VERSION=$(node --version)
log "Node.js version: $NODE_VERSION"

# Verify OpenClaw
OPENCLAW_PATH=$(which openclaw)
log "OpenClaw path: $OPENCLAW_PATH"

# Set AWS region (for SSM)
export AWS_DEFAULT_REGION="${AWS_REGION:-us-east-1}"
export AWS_REGION="${AWS_REGION:-us-east-1}"

# Change to OpenClaw directory
cd /home/openclaw/.openclaw

# Start gateway in FOREGROUND mode
# CRITICAL: Use 'run' not 'start' — 'start' tries systemctl --user which fails
log "Starting OpenClaw gateway (foreground)..."
exec /usr/local/bin/openclaw gateway run --allow-unconfigured
