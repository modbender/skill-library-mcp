#!/bin/bash
# Invoice Collector Script
# Usage: ./collect_invoices.sh <config_file>
# Config file format (JSON):
# {
#   "account": "user@gmail.com",
#   "sources": [
#     {"name": "Claude", "query": "from:anthropic (invoice OR receipt)"},
#     {"name": "Vercel", "query": "from:invoice+statements@vercel.com"}
#   ],
#   "date_range": {"after": "2026/01/01", "before": "2026/02/01"},
#   "destination": "recipient@example.com",
#   "subject": "【2026年1月】請求書まとめ"
# }

set -e

CONFIG_FILE="${1:-config.json}"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Config file not found: $CONFIG_FILE"
  exit 1
fi

# Parse config
ACCOUNT=$(jq -r '.account' "$CONFIG_FILE")
DESTINATION=$(jq -r '.destination' "$CONFIG_FILE")
SUBJECT=$(jq -r '.subject' "$CONFIG_FILE")
AFTER=$(jq -r '.date_range.after' "$CONFIG_FILE")
BEFORE=$(jq -r '.date_range.before' "$CONFIG_FILE")

export GOG_ACCOUNT="$ACCOUNT"
export PATH="$HOME/.local/bin:$PATH"

# Create output directory
INVOICE_DIR="/tmp/invoices_$(date +%Y%m%d%H%M%S)"
mkdir -p "$INVOICE_DIR"

ATTACHMENTS=""
SUMMARY=""

# Process each source
jq -c '.sources[]' "$CONFIG_FILE" | while read -r source; do
  NAME=$(echo "$source" | jq -r '.name')
  QUERY=$(echo "$source" | jq -r '.query')
  
  echo "Processing: $NAME"
  
  # Search for emails
  FULL_QUERY="$QUERY after:$AFTER before:$BEFORE"
  RESULT=$(gog gmail search "$FULL_QUERY" --json 2>/dev/null || echo '{"threads":[]}')
  
  MSG_ID=$(echo "$RESULT" | jq -r '.threads[0].id // empty')
  
  if [ -z "$MSG_ID" ]; then
    echo "  No emails found for $NAME"
    continue
  fi
  
  echo "  Found email: $MSG_ID"
  
  # Get email details
  EMAIL_JSON=$(gog gmail read "$MSG_ID" --json 2>/dev/null)
  
  # Check for PDF attachment
  ATTACH_ID=$(echo "$EMAIL_JSON" | jq -r '.thread.messages[0].payload.parts[]? | select(.filename | test("\\.pdf$"; "i")) | .body.attachmentId // empty' | head -1)
  
  if [ -n "$ATTACH_ID" ]; then
    # Download PDF
    FILENAME="${NAME}_$(date +%Y%m).pdf"
    echo "  Downloading PDF: $FILENAME"
    gog gmail attachment "$MSG_ID" "$ATTACH_ID" --out "$INVOICE_DIR/$FILENAME"
    echo "$INVOICE_DIR/$FILENAME" >> "$INVOICE_DIR/attachments.txt"
  else
    # Take screenshot
    FILENAME="${NAME}_$(date +%Y%m).png"
    echo "  Taking screenshot: $FILENAME"
    
    # Extract HTML
    echo "$EMAIL_JSON" | node -e "
      const fs = require('fs');
      let data = '';
      process.stdin.on('data', chunk => data += chunk);
      process.stdin.on('end', () => {
        const json = JSON.parse(data);
        const msg = json.thread.messages[0];
        const parts = msg.payload.parts || [];
        let html = '';
        const findHtml = (p) => {
          if (p.mimeType === 'text/html' && p.body && p.body.data) {
            html = Buffer.from(p.body.data, 'base64').toString('utf-8');
          }
          if (p.parts) p.parts.forEach(findHtml);
        };
        parts.forEach(findHtml);
        if (!html && msg.payload.body && msg.payload.body.data) {
          html = Buffer.from(msg.payload.body.data, 'base64').toString('utf-8');
        }
        fs.writeFileSync('$INVOICE_DIR/temp.html', html || '<html><body>No content</body></html>');
      });
    "
    
    # Screenshot with Puppeteer
    cd /tmp && node -e "
      const puppeteer = require('puppeteer');
      const fs = require('fs');
      (async () => {
        const browser = await puppeteer.launch({
          headless: 'new',
          args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        const page = await browser.newPage();
        await page.setViewport({ width: 800, height: 1200 });
        const html = fs.readFileSync('$INVOICE_DIR/temp.html', 'utf-8');
        await page.setContent(html, { waitUntil: 'networkidle0' });
        await page.screenshot({ path: '$INVOICE_DIR/$FILENAME', fullPage: true });
        await browser.close();
      })();
    "
    
    echo "$INVOICE_DIR/$FILENAME" >> "$INVOICE_DIR/attachments.txt"
  fi
done

# Build attachment flags
if [ -f "$INVOICE_DIR/attachments.txt" ]; then
  ATTACH_FLAGS=""
  while read -r file; do
    ATTACH_FLAGS="$ATTACH_FLAGS --attach $file"
  done < "$INVOICE_DIR/attachments.txt"
  
  # Send email
  echo "Sending summary email to $DESTINATION"
  gog gmail send \
    --to "$DESTINATION" \
    --subject "$SUBJECT" \
    --body "請求書を添付します。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 請求書まとめ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

添付ファイル一覧は本メールをご確認ください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

このメールは自動生成されました。
" $ATTACH_FLAGS
  
  echo "Done! Sent to $DESTINATION"
else
  echo "No invoices found"
fi

# Cleanup
rm -rf "$INVOICE_DIR"
