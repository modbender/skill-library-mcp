#!/usr/bin/env bash
# generect.sh — Quick CLI wrapper for Generect Live API
# Usage:
#   generect.sh leads '{"job_title":["CEO"],"location":["US"],"per_page":5}'
#   generect.sh companies '{"industry":["SaaS"],"per_page":5}'
#   generect.sh email '{"first_name":"John","last_name":"Doe","domain":"example.com"}'
#   generect.sh validate '{"email":"john@example.com"}'
#   generect.sh lead-url '{"url":"https://linkedin.com/in/someone"}'

set -euo pipefail

BASE="https://api.generect.com/api/linkedin"
AUTH="Authorization: Token ${GENERECT_API_KEY:?Set GENERECT_API_KEY}"

cmd="${1:?Usage: generect.sh <leads|companies|email|validate|lead-url> '<json>'}"
body="${2:?Provide JSON body as second argument}"

case "$cmd" in
  leads)      endpoint="$BASE/leads/by_icp/" ;;
  companies)  endpoint="$BASE/companies/by_icp/" ;;
  email)      endpoint="$BASE/email_finder/" ;;
  validate)   endpoint="$BASE/email_validator/" ;;
  lead-url)   endpoint="$BASE/leads/by_link/" ;;
  *) echo "Unknown command: $cmd" >&2; exit 1 ;;
esac

curl -sS -X POST "$endpoint" \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d "$body"
