#!/bin/bash
# MR Review Workflow Script
# Automates: checkout MR → run tests → post result as comment → approve if passed

set -e

MR_ID="$1"
TEST_COMMAND="${2:-npm test}"

if [ -z "$MR_ID" ]; then
    echo "Usage: $0 <MR_ID> [test_command]"
    echo "Example: $0 123"
    echo "Example: $0 123 'pnpm test'"
    exit 1
fi

echo "🔄 Checking out MR !$MR_ID..."
glab mr checkout "$MR_ID"

echo "🧪 Running tests: $TEST_COMMAND"
if eval "$TEST_COMMAND"; then
    echo "✅ Tests passed!"
    
    echo "📝 Adding approval comment..."
    glab mr note "$MR_ID" -m "✅ Tests passed locally - approving"
    
    echo "👍 Approving MR..."
    glab mr approve "$MR_ID"
    
    echo "✨ Review complete - MR approved"
else
    echo "❌ Tests failed!"
    
    echo "📝 Adding failure comment..."
    glab mr note "$MR_ID" -m "❌ Tests failed locally - please review

Test command: \`$TEST_COMMAND\`

See output above for details."
    
    echo "⚠️  Review complete - MR not approved due to test failures"
    exit 1
fi
