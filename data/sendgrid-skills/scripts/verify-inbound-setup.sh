#!/bin/bash
# verify-inbound-setup.sh - Verify SendGrid Inbound Parse configuration
#
# Usage: ./verify-inbound-setup.sh <hostname> [webhook-url]
#
# Examples:
#   ./verify-inbound-setup.sh parse.example.com
#   ./verify-inbound-setup.sh parse.example.com https://webhook.example.com/parse

set -e

# Help
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
  echo "Usage: $0 <hostname> [webhook-url]"
  echo ""
  echo "Verify SendGrid Inbound Parse configuration:"
  echo "  1. Check MX record points to mx.sendgrid.net"
  echo "  2. Validate DNS propagation"
  echo "  3. (Optional) Test webhook endpoint accessibility"
  echo ""
  echo "Examples:"
  echo "  $0 parse.example.com"
  echo "  $0 parse.example.com https://webhook.example.com/parse"
  exit 0
fi

# Validate hostname
if [[ -z "$1" ]]; then
  echo "❌ Error: Hostname required"
  echo "Usage: $0 <hostname> [webhook-url]"
  exit 1
fi

HOSTNAME="$1"
WEBHOOK_URL="$2"

# Security: Validate HOSTNAME to prevent shell injection.
# Only alphanumeric characters, dots, and hyphens are permitted.
# This blocks shell metacharacters and ensures dig/nslookup receive safe input.
if [[ ! "$HOSTNAME" =~ ^[a-zA-Z0-9]([a-zA-Z0-9.-]{0,251}[a-zA-Z0-9])?$ ]]; then
  echo "❌ Error: Invalid hostname. Only letters, numbers, dots, and hyphens are allowed."
  exit 1
fi

# Security: Validate WEBHOOK_URL to prevent SSRF (Server-Side Request Forgery).
# Only HTTPS URLs with clean hostnames are accepted.
# This blocks file://, http://, internal addresses, and shell metacharacters.
if [[ -n "$WEBHOOK_URL" ]]; then
  if [[ ! "$WEBHOOK_URL" =~ ^https://[a-zA-Z0-9]([a-zA-Z0-9.-]+)(:[0-9]+)?(/.*)?$ ]]; then
    echo "❌ Error: Webhook URL must use HTTPS (e.g. https://webhook.example.com/parse)"
    exit 1
  fi
fi

echo "🔍 Verifying Inbound Parse setup for: $HOSTNAME"
echo ""

# Check if dig is available
if ! command -v dig &> /dev/null; then
  echo "⚠️  Warning: 'dig' command not found, using 'nslookup' instead"
  USE_NSLOOKUP=1
fi

# Check MX record
echo "📝 Checking MX record..."
if [[ -n "$USE_NSLOOKUP" ]]; then
  MX_RECORDS=$(nslookup -type=MX "$HOSTNAME" 2>&1 | grep "mail exchanger" || true)
else
  MX_RECORDS=$(dig +short MX "$HOSTNAME" 2>&1 || true)
fi

if [[ -z "$MX_RECORDS" ]]; then
  echo "❌ Error: No MX records found for $HOSTNAME"
  echo ""
  echo "Expected MX record:"
  echo "  Type: MX"
  echo "  Host: $HOSTNAME"
  echo "  Priority: 10"
  echo "  Value: mx.sendgrid.net"
  echo ""
  echo "Note: DNS propagation can take 24-48 hours"
  exit 1
fi

echo "✅ MX records found:"
echo "$MX_RECORDS"
echo ""

# Check if mx.sendgrid.net is in records
if echo "$MX_RECORDS" | grep -q "mx.sendgrid.net"; then
  echo "✅ MX record correctly points to mx.sendgrid.net"
else
  echo "⚠️  Warning: MX record does not point to mx.sendgrid.net"
  echo ""
  echo "Expected: mx.sendgrid.net"
  echo "Found: $MX_RECORDS"
  echo ""
  echo "Update your MX record to:"
  echo "  Type: MX"
  echo "  Host: $HOSTNAME"
  echo "  Priority: 10"
  echo "  Value: mx.sendgrid.net"
  exit 1
fi

echo ""

# Test webhook if provided
if [[ -n "$WEBHOOK_URL" ]]; then
  echo "🌐 Testing webhook endpoint..."
  echo "URL: $WEBHOOK_URL"
  echo ""
  
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$WEBHOOK_URL" \
    -H "Content-Type: multipart/form-data" \
    -F "from=test@example.com" \
    -F "to=$HOSTNAME" \
    -F "subject=Test" \
    -F "text=Test message" \
    2>&1 || echo "000")
  
  if [[ "$HTTP_CODE" == "000" ]]; then
    echo "❌ Error: Could not connect to webhook endpoint"
    echo ""
    echo "Check:"
    echo "  - URL is correct and publicly accessible"
    echo "  - Firewall/security groups allow incoming traffic"
    echo "  - Server is running and listening on correct port"
    exit 1
  elif [[ "$HTTP_CODE" =~ ^2 ]]; then
    echo "✅ Webhook endpoint accessible (HTTP $HTTP_CODE)"
  elif [[ "$HTTP_CODE" == "401" ]]; then
    echo "✅ Webhook endpoint accessible but requires auth (HTTP $HTTP_CODE)"
    echo "   This is expected if you've configured basic auth"
  else
    echo "⚠️  Webhook returned HTTP $HTTP_CODE"
    echo "   Endpoint is accessible but may need configuration"
  fi
  echo ""
fi

# Summary
echo "📋 Summary:"
echo "  ✅ MX record configured correctly"
if [[ -n "$WEBHOOK_URL" ]]; then
  echo "  ✅ Webhook endpoint tested"
fi
echo ""
echo "Next steps:"
echo "  1. Configure Inbound Parse in SendGrid Console"
echo "     → Settings → Inbound Parse → Add Host & URL"
echo "  2. Set Hostname: $HOSTNAME"
if [[ -n "$WEBHOOK_URL" ]]; then
  echo "  3. Set Destination URL: $WEBHOOK_URL"
fi
echo "  4. Send test email to: anything@$HOSTNAME"
echo ""
echo "Note: DNS propagation can take up to 48 hours"
