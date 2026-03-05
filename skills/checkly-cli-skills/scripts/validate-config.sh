#!/bin/bash
# Validate Checkly project configuration

set -e

echo "🔍 Validating Checkly project configuration..."

npx checkly validate --verify-runtime-dependencies

if [ $? -eq 0 ]; then
  echo "✅ Configuration is valid!"
else
  echo "❌ Configuration has errors. Fix them before deploying."
  exit 1
fi
