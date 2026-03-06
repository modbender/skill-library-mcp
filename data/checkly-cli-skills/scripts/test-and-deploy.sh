#!/bin/bash
# Test checks locally before deploying to production

set -e

echo "🧪 Testing checks locally..."
npx checkly test

if [ $? -eq 0 ]; then
  echo "✅ All checks passed!"
  echo ""
  read -p "Deploy to production? (y/N) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Deploying checks..."
    npx checkly deploy --force
    echo "✅ Deployment complete!"
  else
    echo "❌ Deployment cancelled"
    exit 1
  fi
else
  echo "❌ Some checks failed. Fix issues before deploying."
  exit 1
fi
