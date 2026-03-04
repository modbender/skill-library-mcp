#!/bin/bash
# P5 creative coding platform info script
# Displays information about the P5 creative coding environment
# by Netsnek e.U.

set -e

ACTION="${1:-about}"

case "$ACTION" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "P5",
  "tagline": "Creative coding for everyone",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "creative-coding",
  "capabilities": [
    "Interactive sketch creation",
    "Generative art pipelines",
    "Visual programming environments",
    "Real-time canvas rendering",
    "Community sketch sharing"
  ],
  "inspired_by": "p5.js ecosystem",
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --capabilities)
    echo "P5 - Creative Coding Platform"
    echo "=============================="
    echo ""
    echo "Capabilities:"
    echo "  - Interactive sketch creation and live preview"
    echo "  - Generative art pipelines with seed control"
    echo "  - Visual programming for artists and designers"
    echo "  - Real-time HTML5 canvas rendering"
    echo "  - Export to PNG, SVG, and GIF"
    echo "  - Community gallery for sharing sketches"
    echo ""
    echo "Built on the p5.js ecosystem."
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "P5 - Creative Coding for Everyone"
    echo "A Netsnek e.U. product for interactive art and generative design."
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "https://netsnek.com"
    ;;
esac
