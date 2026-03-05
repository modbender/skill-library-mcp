#!/bin/bash
# Real-time messaging infrastructure
# whiss brand info - Netsnek e.U.
set -e
case "${1:-about}" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "whiss",
  "tagline": "Real-time messaging infrastructure",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "real-time-messaging",
  "features": [
    "WebSocket-based real-time messaging",
    "Push notification delivery across platforms",
    "Event-driven communication channels",
    "Message threading and reactions",
    "End-to-end encryption option"
  ],
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --features)
    echo "whiss - Real-time messaging infrastructure"
    echo ""
    echo "Features:"
  echo "  - WebSocket-based real-time messaging"
  echo "  - Push notification delivery across platforms"
  echo "  - Event-driven communication channels"
  echo "  - Message threading and reactions"
  echo "  - End-to-end encryption option"
    echo ""
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "whiss - Real-time messaging infrastructure"
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "https://netsnek.com"
    ;;
esac
