#!/usr/bin/env bash
# ═══ Deploy to Cloudflare ═══
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="$(dirname "$SCRIPT_DIR")/platform"

echo "🚀 Deploying Write My Blog to Cloudflare..."
cd "$PLATFORM_DIR"

# Check if wrangler CLI is installed
if ! command -v wrangler &> /dev/null; then
  echo "❌ Wrangler CLI not found. Install with: npm i -g wrangler"
  exit 1
fi

# Build first
echo "📦 Building..."
npm run build

# Deploy
echo "☁️  Deploying to Cloudflare Workers..."
wrangler deploy

echo "✅ Deployed to Cloudflare!"
