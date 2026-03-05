#!/bin/bash

###############################################################################
# Mail Hygiene - Run Now
# Immediately run a mail hygiene scan and display results
###############################################################################

echo "🔍 Running Mail Hygiene Scan Now..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the main script
/Users/ericwoodard/clawd/scripts/mail-hygiene.sh

# Display results
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 SCAN RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "/Users/ericwoodard/clawd/mail-reports/latest-summary.txt" ]; then
  cat /Users/ericwoodard/clawd/mail-reports/latest-summary.txt
else
  echo "No results available"
fi

echo ""
echo "✅ Scan complete!"
