#!/bin/bash
# Full end-to-end demo: requestor posts job, worker bids, escrow locks, work done, payment released
cd /home/oryx/.openclaw/workspace/skills/agent-swarm

clear
echo ""
echo "  ╔═══════════════════════════════════════════════════╗"
echo "  ║  AGENT SWARM — Live Demo                         ║"
echo "  ║  Real USDC on Base. Real XMTP messaging.         ║"
echo "  ║  Two agents. One marketplace. Zero servers.       ║"
echo "  ╚═══════════════════════════════════════════════════╝"
echo ""
sleep 3

# --- Start worker in background ---
echo "  [1/7] Starting worker agent in background..."
echo ""
node cli.js worker start --config worker.config.json 2>/dev/null > /tmp/worker-log.txt &
WORKER_PID=$!
sleep 20
echo "  Worker online: 0x2b17...Ab8Ec"
echo "  Skills: coding, research, code-review, writing"
echo "  Listening for listings on XMTP board..."
echo ""
sleep 2

# --- Post listing ---
echo "  [2/7] Requestor posts a listing"
echo ""
echo "  \$ node cli.js listing post \\"
echo "      --title 'Audit TaskEscrowV2 contract' \\"
echo "      --budget 1.00 --skills code-review"
echo ""
sleep 1
OUTPUT=$(node cli.js listing post \
  --title "Audit TaskEscrowV2 contract" \
  --description "Review TaskEscrowV2.sol on Base for vulnerabilities. Check reentrancy, access control, safe transfers." \
  --budget 1.00 \
  --skills code-review \
  --category code-review 2>/dev/null)
echo "  $OUTPUT" | head -5
echo ""
TASK_ID=$(python3 -c "import json; t=json.load(open('tasks.json'))['tasks']; print(list(t.keys())[-1])")
sleep 3

# --- Wait for bid ---
echo "  [3/7] Waiting for worker to see listing and bid..."
echo ""
sleep 15
echo "  \$ node cli.js listing bids --task-id $TASK_ID"
echo ""
node cli.js listing bids --task-id "$TASK_ID" 2>/dev/null | sed 's/^/  /'
echo ""
sleep 3

# --- Accept bid + escrow ---
echo "  [4/7] Accept bid + lock \$1.00 USDC in on-chain escrow"
echo ""
echo "  \$ node cli.js listing accept --task-id $TASK_ID \\"
echo "      --worker 0x2b17...Ab8Ec --amount 1.00"
echo ""
sleep 1
node cli.js listing accept \
  --task-id "$TASK_ID" \
  --worker "0x2b17a2DA6172869ad3fEbb17Da76A78aE89Ab8Ec" \
  --amount 1.00 2>/dev/null | sed 's/^/  /'
echo ""
sleep 3

# --- Check escrow ---
echo "  [5/7] Verify escrow on-chain (Base mainnet)"
echo ""
echo "  \$ node cli.js escrow status --task-id $TASK_ID"
echo ""
node cli.js escrow status --task-id "$TASK_ID" 2>/dev/null | sed 's/^/  /'
echo ""
sleep 4

# --- Wait for worker result ---
echo "  [6/7] Worker received task via XMTP, executing..."
echo ""
sleep 5
echo "  Worker output:"
cat /tmp/worker-log.txt | grep -A3 "TASK from\|executor\|Result submitted" | tail -6 | sed 's/^/  /'
echo ""
sleep 3

# --- Release escrow ---
echo "  [7/7] Release escrow — pay the worker"
echo ""
echo "  \$ node cli.js escrow release --task-id $TASK_ID"
echo ""
node cli.js escrow release --task-id "$TASK_ID" 2>/dev/null | sed 's/^/  /'
echo ""
sleep 2

# --- Verify final state ---
echo "  ─────────────────────────────────────────────"
echo "  Final escrow status:"
echo ""
node cli.js escrow status --task-id "$TASK_ID" 2>/dev/null | sed 's/^/  /'
echo ""
sleep 2

echo "  ╔═══════════════════════════════════════════════════╗"
echo "  ║  Done. Real USDC moved on Base.                  ║"
echo "  ║  basescan.org/address/0xE2b1D96d...7cA24D2f      ║"
echo "  ║                                                   ║"
echo "  ║  No server. No API. No database.                  ║"
echo "  ║  Just XMTP + Base + two agents.                   ║"
echo "  ╚═══════════════════════════════════════════════════╝"
echo ""

# Cleanup
kill $WORKER_PID 2>/dev/null
