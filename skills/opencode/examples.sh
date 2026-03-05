#!/bin/bash
# OpenCode Examples - Test various commands
# Ensure PATH includes /usr/sbin for sysctl

set -e

export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

echo "=== OpenCode Examples ==="
echo ""

# Check version
echo "1. Version Check:"
opencode --version
echo ""

# List models
echo "2. Available Models:"
opencode models | head -20
echo ""

# Check auth status
echo "3. Auth Status:"
opencode auth list || echo "No auth configured"
echo ""

# List sessions
echo "4. Existing Sessions:"
opencode session list || echo "No sessions found"
echo ""

# Show stats
echo "5. Usage Stats:"
opencode stats || echo "No usage data yet"
echo ""

echo "=== Examples Complete ==="
echo ""
echo "Try these next:"
echo "  opencode run 'Add error handling to my code'"
echo "  opencode --help"
echo "  opencode pr 123  # GitHub PR workflow"
