#!/usr/bin/env bash
# Import signer credentials bundle for watch-only lnd operation.
#
# Usage:
#   import-credentials.sh --bundle /path/to/credentials-bundle/
#   import-credentials.sh --bundle /path/to/credentials-bundle.tar.gz.b64
#   import-credentials.sh --bundle <base64-string>
#
# Imports to:
#   ~/.lnget/lnd/signer-credentials/accounts.json
#   ~/.lnget/lnd/signer-credentials/tls.cert
#   ~/.lnget/lnd/signer-credentials/admin.macaroon

set -e

LNGET_LND_DIR="${LNGET_LND_DIR:-$HOME/.lnget/lnd}"
BUNDLE=""

# Parse arguments.
while [[ $# -gt 0 ]]; do
    case $1 in
        --bundle)
            BUNDLE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: import-credentials.sh --bundle <path-or-base64>"
            echo ""
            echo "Import signer credentials bundle for watch-only lnd."
            echo ""
            echo "Options:"
            echo "  --bundle PATH  Path to credentials directory, .tar.gz.b64 file,"
            echo "                 or raw base64 string"
            echo ""
            echo "The bundle should contain: accounts.json, tls.cert, admin.macaroon"
            echo "These are produced by the lightning-security-module skill's"
            echo "export-credentials.sh script."
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

if [ -z "$BUNDLE" ]; then
    echo "Error: --bundle is required." >&2
    echo "Usage: import-credentials.sh --bundle <path-or-base64>" >&2
    exit 1
fi

CREDS_DIR="$LNGET_LND_DIR/signer-credentials"

echo "=== Importing Signer Credentials ==="
echo ""
echo "Output: $CREDS_DIR"
echo ""

# Create credentials directory.
mkdir -p "$CREDS_DIR"
chmod 700 "$CREDS_DIR"

# Determine bundle type and extract.
if [ -d "$BUNDLE" ]; then
    # Directory: copy files directly.
    echo "Importing from directory: $BUNDLE"
    cp "$BUNDLE/accounts.json" "$CREDS_DIR/" 2>/dev/null || true
    cp "$BUNDLE/tls.cert" "$CREDS_DIR/" 2>/dev/null || true
    cp "$BUNDLE/admin.macaroon" "$CREDS_DIR/" 2>/dev/null || true

elif [ -f "$BUNDLE" ]; then
    # File: assume base64-encoded tar.gz.
    echo "Importing from file: $BUNDLE"
    base64 -d < "$BUNDLE" | tar -xzf - -C "$CREDS_DIR"

else
    # Raw base64 string: decode and extract.
    echo "Importing from base64 string..."
    echo "$BUNDLE" | base64 -d | tar -xzf - -C "$CREDS_DIR"
fi

echo ""

# Verify all required files are present.
MISSING=false

if [ -f "$CREDS_DIR/accounts.json" ]; then
    echo "  accounts.json   — OK"
else
    echo "  accounts.json   — MISSING" >&2
    MISSING=true
fi

if [ -f "$CREDS_DIR/tls.cert" ]; then
    echo "  tls.cert        — OK"
else
    echo "  tls.cert        — MISSING" >&2
    MISSING=true
fi

if [ -f "$CREDS_DIR/admin.macaroon" ]; then
    echo "  admin.macaroon  — OK"
else
    echo "  admin.macaroon  — MISSING" >&2
    MISSING=true
fi

if [ "$MISSING" = true ]; then
    echo "" >&2
    echo "Error: Credentials bundle is incomplete." >&2
    echo "Expected: accounts.json, tls.cert, admin.macaroon" >&2
    exit 1
fi

# Set restrictive permissions on credential files.
chmod 600 "$CREDS_DIR/accounts.json"
chmod 600 "$CREDS_DIR/tls.cert"
chmod 600 "$CREDS_DIR/admin.macaroon"

echo ""

# If a litd container is running, copy credentials into it so the
# remotesigner config paths resolve inside the container.
if command -v docker &>/dev/null; then
    for candidate in litd litd-shared; do
        if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$candidate"; then
            docker exec "$candidate" mkdir -p /root/.lnd/signer-credentials
            docker cp "$CREDS_DIR/tls.cert" "$candidate:/root/.lnd/signer-credentials/tls.cert"
            docker cp "$CREDS_DIR/admin.macaroon" "$candidate:/root/.lnd/signer-credentials/admin.macaroon"
            docker cp "$CREDS_DIR/accounts.json" "$candidate:/root/.lnd/signer-credentials/accounts.json"
            echo "  Credentials copied into container '$candidate'."
            break
        fi
    done
fi

echo ""
echo "=== Credentials Imported Successfully ==="
echo ""
echo "Location: $CREDS_DIR"
echo ""
echo "Next steps:"
echo "  1. Create watch-only wallet: skills/lnd/scripts/create-wallet.sh"
echo "  2. Start lnd: skills/lnd/scripts/start-lnd.sh --signer-host <signer-ip>:10012"
