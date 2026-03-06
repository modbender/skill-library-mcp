#!/bin/bash
# Test GIF integration for MISO Phase 2/3

set -e

CHAT_ID="7962608100"  # Test chat ID
MISO_DIR="/Users/a003/.openclaw/workspace/miso"

echo "=== Testing GIF Integration ==="

# Test 1: Send init animation
echo "Test 1: Sending init animation..."
python3 "$MISO_DIR/scripts/miso_telegram.py" send "$CHAT_ID" init "🧪 Test Mission 1

📋 GIF送信テスト
⏱ 0s ∣ 💰 $0.00

↳ 🧩 AGENTS (2 spawning)
——————————————
⏳ Agent 1 ∣ Research task
↳ INIT

⏳ Agent 2 ∣ Writing task
↳ INIT

——————————————
🌸 ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍɪʏᴀʙɪ"

# Store message ID for editing
echo "Please provide the message ID from the above test:"
read -p "Message ID: " MESSAGE_ID

# Test 2: Edit to running animation
echo ""
echo "Test 2: Updating to running animation..."
python3 "$MISO_DIR/scripts/miso_telegram.py" edit "$CHAT_ID" "$MESSAGE_ID" running "🤖 𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟
——————————————
📋 GIF送信テスト
⏱ 10s ∣ 💰 $0.05

↳ 🧩 AGENTS (0/2 complete)
——————————————

🔥 Agent 1 ∣ Research task
▓▓▓▓▓▓▓▓░░░░░░░ 50%
🧠 Collecting competitor data...
⏱ 8s ∣ 💰 $0.03

🔥 Agent 2 ∣ Writing task
▓▓▓▓▓░░░░░░░░░░ 31%
🧠 Drafting article outline...
⏱ 5s ∣ 💰 $0.02

——————————————
🌸 ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍɪʏᴀʙɪ"

echo ""
echo "=== Tests Complete ==="
echo "Verify GIF animations in Telegram:"
echo "1. Initial animation (miso-init.gif)"
echo "2. Running animation (miso-running.gif)"
