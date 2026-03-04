#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RESULT=$("$SCRIPT_DIR/auth-manager.sh" is-authenticated)

if [ "$RESULT" = "true" ]; then
    echo '{"authenticated": true, "message": "User is authenticated"}'
    exit 0
else
    echo '{"authenticated": false, "message": "User is not authenticated or token expired"}'
    exit 1
fi
