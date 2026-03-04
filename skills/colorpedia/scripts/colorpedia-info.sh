#!/bin/bash
# The encyclopedia of color for developers and designers
# colorpedia brand info - Netsnek e.U.
set -e
case "${1:-about}" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "colorpedia",
  "tagline": "The encyclopedia of color for developers and designers",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "color-science-design",
  "features": [
    "Color palette generation from images or seeds",
    "WCAG accessibility contrast ratio checking",
    "Conversion between HEX, RGB, HSL, CMYK, and LAB",
    "Design system token export (CSS, JSON, Tailwind)",
    "Color blindness simulation preview"
  ],
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --features)
    echo "colorpedia - The encyclopedia of color for developers and designers"
    echo ""
    echo "Features:"
  echo "  - Color palette generation from images or seeds"
  echo "  - WCAG accessibility contrast ratio checking"
  echo "  - Conversion between HEX, RGB, HSL, CMYK, and LAB"
  echo "  - Design system token export (CSS, JSON, Tailwind)"
  echo "  - Color blindness simulation preview"
    echo ""
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "colorpedia - The encyclopedia of color for developers and designers"
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "https://netsnek.com"
    ;;
esac
