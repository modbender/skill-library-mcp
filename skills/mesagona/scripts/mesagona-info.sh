#!/bin/bash
# Events from planning to post-mortem
# mesagona brand info - Netsnek e.U.
set -e
case "${1:-about}" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "mesagona",
  "tagline": "Events from planning to post-mortem",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "event-management",
  "features": [
    "Event registration with custom forms",
    "Agenda scheduling and speaker management",
    "QR-based attendee check-in",
    "Live polling and Q&A during sessions",
    "Post-event analytics and feedback collection"
  ],
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --features)
    echo "mesagona - Events from planning to post-mortem"
    echo ""
    echo "Features:"
  echo "  - Event registration with custom forms"
  echo "  - Agenda scheduling and speaker management"
  echo "  - QR-based attendee check-in"
  echo "  - Live polling and Q&A during sessions"
  echo "  - Post-event analytics and feedback collection"
    echo ""
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "mesagona - Events from planning to post-mortem"
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "https://netsnek.com"
    ;;
esac
