#!/bin/bash
# Import existing checks from Checkly UI to code

set -e

echo "📥 Importing existing checks from Checkly..."

# Check authentication
if ! npx checkly whoami &> /dev/null; then
  echo "❌ Not authenticated. Run 'npx checkly login' first."
  exit 1
fi

# Import checks
npx checkly import plan

echo ""
echo "✅ Import complete!"
echo ""
echo "Next steps:"
echo "  1. Review imported files: git diff"
echo "  2. Test locally: npx checkly test"
echo "  3. Commit to version control: git add . && git commit"
echo "  4. Deploy to sync state: npx checkly deploy --force"
