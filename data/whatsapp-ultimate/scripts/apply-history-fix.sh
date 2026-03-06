#!/usr/bin/env bash
# whatsapp-ultimate: Apply self-chat history capture fix to OpenClaw
# This patches monitor.ts to store all inbound messages in the WhatsApp history DB.
# Safe to run multiple times — skips if already applied.

set -euo pipefail

# Find OpenClaw source directory
OPENCLAW_SRC=""
for dir in "$HOME/src/clawdbot-moltbot-openclaw" "$HOME/src/openclaw" "$HOME/.openclaw/src"; do
  if [[ -f "$dir/src/web/inbound/monitor.ts" ]]; then
    OPENCLAW_SRC="$dir"
    break
  fi
done

if [[ -z "$OPENCLAW_SRC" ]]; then
  echo "❌ Could not find OpenClaw source directory."
  echo "   Looked in: ~/src/clawdbot-moltbot-openclaw, ~/src/openclaw, ~/.openclaw/src"
  echo "   Set OPENCLAW_SRC env var to your OpenClaw repo path and re-run."
  exit 1
fi

MONITOR="$OPENCLAW_SRC/src/web/inbound/monitor.ts"

echo "📁 OpenClaw source: $OPENCLAW_SRC"
echo "📄 Target: $MONITOR"

# Check if already patched
if grep -q "insertHistoryMessage" "$MONITOR" 2>/dev/null; then
  echo "✅ Already patched — history capture is present in monitor.ts"
  exit 0
fi

echo "🔧 Applying self-chat history capture patch..."

# Step 1: Add import
# Find the last import line and add our import after it
IMPORT_LINE='import { insertMessage as insertHistoryMessage, getContactName, getChatName, type MessageRecord } from "../../whatsapp-history/db.js";'

# Add import after the sent-ids import
if grep -q 'from "./sent-ids.js"' "$MONITOR"; then
  sed -i '/from "\.\/sent-ids\.js"/a '"$IMPORT_LINE" "$MONITOR"
  echo "  ✓ Added import"
else
  echo "  ⚠ Could not find sent-ids import anchor. Adding at top of imports."
  sed -i "1i\\$IMPORT_LINE" "$MONITOR"
fi

# Step 2: Add the capture block after the self-chat read receipt block
PATCH_BLOCK='      // Fork (whatsapp-ultimate): ensure every inbound message processed by the monitor
      // is stored in the WhatsApp history DB. Baileys misses self-chat inbound messages.
      try {
        const chatJid = remoteJid.includes("@") ? remoteJid : `${remoteJid}@s.whatsapp.net`;
        const histRecord: MessageRecord = {
          id: id || `monitor-${Date.now()}`,
          chat_jid: chatJid,
          chat_name: getChatName(chatJid) || groupSubject || undefined,
          sender_jid: senderE164 ? `${senderE164.replace("+", "")}@s.whatsapp.net` : undefined,
          sender_name: getContactName(senderE164 ? `${senderE164.replace("+", "")}@s.whatsapp.net` : "") || undefined,
          sender_pushname: msg.pushName || undefined,
          from_me: Boolean(msg.key?.fromMe),
          timestamp: messageTimestampMs ? Math.floor(messageTimestampMs / 1000) : Math.floor(Date.now() / 1000),
          message_type: msg.message?.conversation || msg.message?.extendedTextMessage ? "text" : "other",
          text_content: earlyBody || undefined,
          source: "live",
        };
        insertHistoryMessage(histRecord);
      } catch (_histErr) {
        // Ignore duplicates — live-capture may have already stored it
      }'

# Find the anchor: "Offline message recovery" comment
if grep -q "Offline message recovery" "$MONITOR"; then
  # Create a temp file with the patch inserted before the anchor
  python3 -c "
import sys
with open('$MONITOR', 'r') as f:
    content = f.read()

anchor = '      // Offline message recovery'
patch = '''$PATCH_BLOCK

'''
if anchor in content:
    content = content.replace(anchor, patch + anchor)
    with open('$MONITOR', 'w') as f:
        f.write(content)
    print('  ✓ Inserted history capture block')
else:
    print('  ❌ Could not find anchor point')
    sys.exit(1)
"
else
  echo "  ❌ Could not find 'Offline message recovery' anchor in monitor.ts"
  echo "  The file structure may have changed. Manual patching required."
  exit 1
fi

# Verify
if grep -q "insertHistoryMessage" "$MONITOR"; then
  echo "✅ Patch applied successfully!"
  echo ""
  echo "Next steps:"
  echo "  1. Rebuild: cd $OPENCLAW_SRC && npm run build"
  echo "  2. Restart gateway: openclaw gateway restart"
  echo "  3. Set syncFullHistory: true in openclaw.json → channels.whatsapp"
  echo "  4. Re-link WhatsApp to trigger full history sync"
else
  echo "❌ Patch verification failed. Check $MONITOR manually."
  exit 1
fi
