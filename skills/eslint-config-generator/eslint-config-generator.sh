#!/bin/bash
PRESET="${1:-airbnb}"

cat > .eslintrc.json << JSON
{
  "extends": ["$PRESET"],
  "rules": {}
}
JSON

echo "✅ ESLint config generated: $PRESET"
