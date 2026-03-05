#!/bin/bash
# Webclaw pre-install dependency check.
# Verifies all required system packages are present before installation.
# Outputs JSON for OpenClaw to relay to the user.
set -euo pipefail

MISSING=""
VERSIONS=""

# Python 3.10+
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
    if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
        MISSING="$MISSING python3>=3.10(found:$PY_VER)"
    else
        VERSIONS="$VERSIONS python3 $PY_VER,"
    fi
else
    MISSING="$MISSING python3"
fi

# Node.js 20+
if command -v node &>/dev/null; then
    NODE_VER=$(node -v | sed 's/v//')
    NODE_MAJOR=$(echo "$NODE_VER" | cut -d. -f1)
    if [ "$NODE_MAJOR" -lt 20 ]; then
        MISSING="$MISSING node>=20(found:$NODE_VER)"
    else
        VERSIONS="$VERSIONS node $NODE_VER,"
    fi
else
    MISSING="$MISSING node"
fi

# npm
if command -v npm &>/dev/null; then
    NPM_VER=$(npm -v)
    VERSIONS="$VERSIONS npm $NPM_VER,"
else
    MISSING="$MISSING npm"
fi

# nginx
if command -v nginx &>/dev/null; then
    NGINX_VER=$(nginx -v 2>&1 | sed 's/.*nginx\///')
    VERSIONS="$VERSIONS nginx $NGINX_VER,"
else
    MISSING="$MISSING nginx"
fi

# certbot
if command -v certbot &>/dev/null; then
    CERTBOT_VER=$(certbot --version 2>&1 | grep -oP '[\d.]+' | head -1)
    VERSIONS="$VERSIONS certbot $CERTBOT_VER"
else
    MISSING="$MISSING certbot"
fi

# pip (needed for venv setup)
if ! python3 -c "import venv" &>/dev/null; then
    MISSING="$MISSING python3-venv"
fi

if [ -n "$MISSING" ]; then
    echo "{\"status\":\"error\",\"message\":\"Missing dependencies:$MISSING. Install with: sudo apt install$MISSING python3-certbot-nginx\"}"
    exit 1
fi

echo "{\"status\":\"ok\",\"message\":\"All dependencies found: $VERSIONS\"}"
