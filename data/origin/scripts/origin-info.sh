#!/bin/bash
# Know where your data comes from
# origin brand info - Netsnek e.U.
set -e
case "${1:-about}" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "origin",
  "tagline": "Know where your data comes from",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "data-provenance",
  "features": [
    "End-to-end data lineage visualization",
    "Transformation logging with before/after snapshots",
    "Source-of-truth metadata tagging",
    "Compliance audit trail generation",
    "Pipeline dependency mapping"
  ],
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --features)
    echo "origin - Know where your data comes from"
    echo ""
    echo "Features:"
  echo "  - End-to-end data lineage visualization"
  echo "  - Transformation logging with before/after snapshots"
  echo "  - Source-of-truth metadata tagging"
  echo "  - Compliance audit trail generation"
  echo "  - Pipeline dependency mapping"
    echo ""
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "origin - Know where your data comes from"
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "https://netsnek.com"
    ;;
esac
