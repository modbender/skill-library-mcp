#!/bin/bash
# List all registered agents

API_URL="https://moltcredit-737941094496.europe-west1.run.app"

curl -s "$API_URL/agents" | jq .
