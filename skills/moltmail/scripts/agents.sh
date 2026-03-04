#!/bin/bash
# List all registered agents

API_URL="https://moltmail.xyz"

curl -s "$API_URL/agents" | jq .
