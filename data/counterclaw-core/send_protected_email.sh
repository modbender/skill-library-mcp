#!/bin/bash
# Protected email sender - wraps gog with CounterClaw scanning
# Usage: ./send_protected_email.sh --to "email@example.com" --subject "Subject" --body "Body"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EMAIL_PROTECTOR="$SCRIPT_DIR/email_protector.py"

# Check if protector exists
if [ ! -f "$EMAIL_PROTECTOR" ]; then
    echo "Error: email_protector.py not found at $EMAIL_PROTECTOR"
    exit 1
fi

# Default values
ALLOW_UNSAFE=false
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --to)
            TO="$2"
            shift 2
            ;;
        --subject)
            SUBJECT="$2"
            shift 2
            ;;
        --body)
            BODY="$2"
            shift 2
            ;;
        --body-file)
            BODY_FILE="$2"
            shift 2
            ;;
        --allow-unsafe)
            ALLOW_UNSAFE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get body from file if provided
if [ -n "$BODY_FILE" ]; then
    BODY=$(cat "$BODY_FILE")
fi

# Validate required params
if [ -z "$TO" ] || [ -z "$SUBJECT" ] || [ -z "$BODY" ]; then
    echo "Usage: $0 --to \"email@example.com\" --subject \"Subject\" --body \"Body\" [--allow-unsafe]"
    echo "Or: $0 --to \"email@example.com\" --subject \"Subject\" --body-file ./file.txt [--allow-unsafe]"
    exit 1
fi

# Combine subject + body for scanning
FULL_CONTENT="Subject: $SUBJECT

$BODY"

# Scan the outbound email (capture output, don't exit on non-zero)
export PYTHONPATH="${HOME}/.openclaw/workspace/skills/counterclaw-core/src:$PYTHONPATH"
SCAN_RESULT=$(python3 "$EMAIL_PROTECTOR" --outbound "$FULL_CONTENT" 2>&1)
SCAN_EXIT=$?

echo "$SCAN_RESULT"

# Check if unsafe (exit code 1 means PII detected)
if [ $SCAN_EXIT -eq 1 ]; then
    if [ "$ALLOW_UNSAFE" = "true" ]; then
        echo ""
        echo "⚠️  PII detected but --allow-unsafe flag set. Proceeding with send..."
    else
        echo ""
        echo "❌ Blocked: PII detected. Use --allow-unsafe to send anyway."
        exit 1
    fi
fi

# If dry run, stop here
if [ "$DRY_RUN" = "true" ]; then
    echo ""
    echo "🔍 Dry run - would send email to: $TO"
    exit 0
fi

# Send via gog
echo ""
echo "📤 Sending email via gog..."
gog gmail send --to "$TO" --subject "$SUBJECT" --body "$BODY"

echo ""
echo "✅ Email sent successfully"
