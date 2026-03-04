#!/bin/bash
# Developer productivity, amplified
# coder brand info - Netsnek e.U.
set -e
case "${1:-about}" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "coder",
  "tagline": "Developer productivity, amplified",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "developer-productivity",
  "features": [
    "Project scaffolding from customizable templates",
    "Snippet library with search and tagging",
    "Automated refactoring suggestions",
    "Code style enforcement and formatting",
    "Multi-language boilerplate generation"
  ],
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --features)
    echo "coder - Developer productivity, amplified"
    echo ""
    echo "Features:"
  echo "  - Project scaffolding from customizable templates"
  echo "  - Snippet library with search and tagging"
  echo "  - Automated refactoring suggestions"
  echo "  - Code style enforcement and formatting"
  echo "  - Multi-language boilerplate generation"
    echo ""
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "coder - Developer productivity, amplified"
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "https://netsnek.com"
    ;;
esac
