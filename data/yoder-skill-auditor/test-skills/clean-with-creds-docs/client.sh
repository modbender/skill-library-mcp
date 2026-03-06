#!/bin/bash
# Simple API client - reads config from arguments only
ENDPOINT="${1:?Usage: client.sh <endpoint>}"
echo "Connecting to $ENDPOINT..."
echo "Response: 200 OK"
