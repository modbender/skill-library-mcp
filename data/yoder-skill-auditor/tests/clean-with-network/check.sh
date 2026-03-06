#!/bin/bash
# Health check - just pings an endpoint
URL="${1:?Usage: check.sh <url>}"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
echo "Status: $STATUS"
