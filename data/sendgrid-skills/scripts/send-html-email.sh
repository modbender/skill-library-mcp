#!/bin/bash
set -e

# send-html-email.sh
# Send HTML email via SendGrid API

show_help() {
  cat << EOF
Usage: $(basename "$0") <recipient> <subject> <html-content-or-file>

Send HTML-formatted email via SendGrid API.

ARGUMENTS:
  recipient           Recipient email address
  subject             Email subject line
  html-content        HTML content string OR path to HTML file

ENVIRONMENT VARIABLES:
  SENDGRID_API_KEY    SendGrid API key (required)
  SENDGRID_FROM       Sender email address (default: test@example.com)

EXAMPLES:
  # Send HTML string
  $(basename "$0") user@example.com "Welcome" "<h1>Hello!</h1><p>Welcome to our service.</p>"

  # Send HTML file
  $(basename "$0") user@example.com "Daily Report" /path/to/report.html

  # With custom sender
  export SENDGRID_FROM="noreply@example.com"
  $(basename "$0") user@example.com "Newsletter" newsletter.html

EXIT CODES:
  0   Email sent successfully
  1   Error (missing args, API key, or SendGrid API failure)

EOF
}

# Parse help flag
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
  show_help
  exit 0
fi

# Validate arguments
if [[ $# -lt 3 ]]; then
  echo "❌ Error: Missing required arguments"
  echo ""
  show_help
  exit 1
fi

RECIPIENT="$1"
SUBJECT="$2"
HTML_INPUT="$3"

# Check for API key
if [[ -z "$SENDGRID_API_KEY" ]]; then
  echo "❌ Error: SENDGRID_API_KEY environment variable not set"
  echo ""
  echo "Get your API key at: https://app.sendgrid.com/settings/api_keys"
  echo "Then set it: export SENDGRID_API_KEY=SG.xxxxxxxxx"
  exit 1
fi

# Set default sender if not provided
FROM_EMAIL="${SENDGRID_FROM:-test@example.com}"

# Security: Validate file path inputs to prevent arbitrary file read.
# If HTML_INPUT looks like a file path (starts with / or ./, or -f resolves it as a file),
# we validate before reading:
#   - Must end in .html or .htm (no reading arbitrary system files)
#   - Must not contain .. (no directory traversal)
#   - Must resolve to a real, existing file via realpath
if [[ "$HTML_INPUT" == /* ]] || [[ "$HTML_INPUT" == ./* ]] || [[ -f "$HTML_INPUT" ]]; then
  # Reject directory traversal attempts
  if [[ "$HTML_INPUT" == *..* ]]; then
    echo "❌ Error: File path must not contain '..' (directory traversal is not allowed)"
    exit 1
  fi
  # Require .html or .htm extension
  if [[ "$HTML_INPUT" != *.html ]] && [[ "$HTML_INPUT" != *.htm ]]; then
    echo "❌ Error: File path must end in .html or .htm"
    exit 1
  fi
  # Resolve to canonical path and confirm it exists
  RESOLVED_PATH=$(realpath --canonicalize-existing "$HTML_INPUT" 2>/dev/null) || {
    echo "❌ Error: File not found or path could not be resolved: $HTML_INPUT"
    exit 1
  }
  HTML_INPUT="$RESOLVED_PATH"
fi

# Determine if input is file or string
if [[ -f "$HTML_INPUT" ]]; then
  # Input is a validated file path — read its contents
  HTML_CONTENT=$(cat "$HTML_INPUT")
else
  # Input is an inline HTML string
  HTML_CONTENT="$HTML_INPUT"
fi

# Validate HTML content is not empty
if [[ -z "$HTML_CONTENT" ]]; then
  echo "❌ Error: HTML content is empty"
  exit 1
fi

echo "📧 Sending HTML email..."
echo "  From: $FROM_EMAIL"
echo "  To: $RECIPIENT"
echo "  Subject: $SUBJECT"
echo ""

# Build JSON payload using jq for proper escaping
# This handles special characters, quotes, newlines, etc.
JSON_PAYLOAD=$(jq -n \
  --arg from "$FROM_EMAIL" \
  --arg to "$RECIPIENT" \
  --arg subject "$SUBJECT" \
  --arg html "$HTML_CONTENT" \
  '{
    personalizations: [{
      to: [{email: $to}]
    }],
    from: {email: $from},
    subject: $subject,
    content: [{
      type: "text/html",
      value: $html
    }]
  }')

# Send via SendGrid API
RESPONSE=$(curl -s -w "\n%{http_code}" \
  --request POST \
  --url https://api.sendgrid.com/v3/mail/send \
  --header "Authorization: Bearer $SENDGRID_API_KEY" \
  --header 'Content-Type: application/json' \
  --data "$JSON_PAYLOAD")

# Extract HTTP status code (last line)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | head -n-1)

# Check response
if [[ "$HTTP_CODE" == "202" ]]; then
  echo "✅ Success! Email queued for delivery (HTTP $HTTP_CODE)"
  echo ""
  echo "Note: Check recipient inbox/spam folder in ~1 minute"
  exit 0
else
  echo "❌ Error: Unexpected response (HTTP $HTTP_CODE)"
  echo ""
  if [[ -n "$RESPONSE_BODY" ]]; then
    echo "Response: $RESPONSE_BODY"
  fi
  exit 1
fi
