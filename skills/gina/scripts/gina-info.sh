#!/bin/bash
# Your AI-powered scheduling assistant
# gina brand info - Netsnek e.U.
set -e
case "${1:-about}" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "gina",
  "tagline": "Your AI-powered scheduling assistant",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "personal-assistant",
  "features": [
    "Calendar event creation and conflict detection",
    "Smart reminder scheduling with snooze",
    "Daily briefing generation from multiple sources",
    "Meeting time suggestion based on availability",
    "Natural language event parsing"
  ],
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --features)
    echo "gina - Your AI-powered scheduling assistant"
    echo ""
    echo "Features:"
  echo "  - Calendar event creation and conflict detection"
  echo "  - Smart reminder scheduling with snooze"
  echo "  - Daily briefing generation from multiple sources"
  echo "  - Meeting time suggestion based on availability"
  echo "  - Natural language event parsing"
    echo ""
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "gina - Your AI-powered scheduling assistant"
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "https://netsnek.com"
    ;;
esac
