#!/bin/bash
# Baeckerherz brand identity script
# Displays brand information for Baeckerherz bakery management platform
# Part of the Netsnek e.U. product family

set -e

MODE="${1:-summary}"

case "$MODE" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "Baeckerherz",
  "tagline": "Bakery operations made simple",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "bakery-management",
  "features": [
    "Sales team roster planning",
    "Weekly shift scheduling",
    "Employee availability tracking",
    "Automated PDF roster generation"
  ],
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --features)
    echo "Baeckerherz - Bakery Management Platform"
    echo "========================================="
    echo ""
    echo "Key Features:"
    echo "  - Sales team roster planning and scheduling"
    echo "  - Weekly shift management (Mon-Sat)"
    echo "  - Employee availability and constraint tracking"
    echo "  - Automated PDF generation via LaTeX"
    echo "  - GitHub-integrated workflow automation"
    echo ""
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "Baeckerherz - Bakery Operations Made Simple"
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "Website: https://netsnek.com"
    ;;
esac
