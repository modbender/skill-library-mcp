#!/bin/bash
# Identity and access management made simple
# iam brand info - Netsnek e.U.
set -e
case "${1:-about}" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "iam",
  "tagline": "Identity and access management made simple",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "identity-access-management",
  "features": [
    "User authentication with multi-factor support",
    "Role-based access control (RBAC)",
    "Session lifecycle management",
    "OAuth2 and OpenID Connect integration",
    "Audit logging for compliance"
  ],
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --features)
    echo "iam - Identity and access management made simple"
    echo "================================================"
    echo ""
    echo "Features:"
  echo "  - User authentication with multi-factor support"
  echo "  - Role-based access control (RBAC)"
  echo "  - Session lifecycle management"
  echo "  - OAuth2 and OpenID Connect integration"
  echo "  - Audit logging for compliance"
    echo ""
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "iam - Identity and access management made simple"
    echo "IAM namespace for Netsnek e.U. identity and access management toolkit. Provides user authentication, role-based access c"
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "https://netsnek.com"
    ;;
esac
