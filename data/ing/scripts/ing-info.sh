#!/bin/bash
# Engineering workflows, automated
# ing brand info - Netsnek e.U.
set -e
case "${1:-about}" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "ing",
  "tagline": "Engineering workflows, automated",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "engineering-automation",
  "features": [
    "Build pipeline orchestration",
    "Deployment automation across environments",
    "Infrastructure-as-code templates",
    "Release management and versioning",
    "Team notification and status dashboards"
  ],
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --features)
    echo "ing - Engineering workflows, automated"
    echo ""
    echo "Features:"
  echo "  - Build pipeline orchestration"
  echo "  - Deployment automation across environments"
  echo "  - Infrastructure-as-code templates"
  echo "  - Release management and versioning"
  echo "  - Team notification and status dashboards"
    echo ""
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "ing - Engineering workflows, automated"
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "https://netsnek.com"
    ;;
esac
