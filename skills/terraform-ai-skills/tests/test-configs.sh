#!/usr/bin/env bash
# Test configuration files for validity

set -e

echo "🧪 Testing Configuration Files..."

FAILED=0

# Test each config file
for config in config/*.config; do
  echo "Testing $config..."
  
  # Check required variables
  for var in PROVIDER_NAME TERRAFORM_MIN_VERSION PROVIDER_MIN_VERSION ORG_NAME; do
    if ! grep -q "^${var}=" "$config"; then
      echo "  ❌ Missing required variable: $var"
      FAILED=$((FAILED + 1))
    fi
  done
  
  # Source and validate
  if source "$config" 2>/dev/null; then
    echo "  ✅ $config is valid"
  else
    echo "  ❌ $config has syntax errors"
    FAILED=$((FAILED + 1))
  fi
done

if [ $FAILED -eq 0 ]; then
  echo "✅ All configuration tests passed!"
  exit 0
else
  echo "❌ $FAILED test(s) failed"
  exit 1
fi
