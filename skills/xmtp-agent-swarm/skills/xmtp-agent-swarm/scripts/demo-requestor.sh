#!/bin/bash
# Demo: Requestor posts a job, accepts a bid, releases escrow
cd /home/oryx/.openclaw/workspace/skills/agent-swarm

echo ""
echo "═══════════════════════════════════════════════"
echo "  AGENT SWARM — Requestor Demo"
echo "  Posting a task, accepting a bid, paying worker"
echo "═══════════════════════════════════════════════"
echo ""
sleep 2

echo "▸ Step 1: Check the board"
echo "  \$ node cli.js board listings"
echo ""
sleep 1
node cli.js board listings 2>/dev/null
echo ""
sleep 3

echo "▸ Step 2: Post a new listing"
echo "  \$ node cli.js listing post --title \"Audit TaskEscrowV2 contract\" --budget 1.00 --skills code-review --category code-review"
echo ""
sleep 1
node cli.js listing post \
  --title "Audit TaskEscrowV2 contract" \
  --description "Review the TaskEscrowV2.sol smart contract for security vulnerabilities. Check reentrancy, access control, and fund safety." \
  --budget 1.00 \
  --skills code-review \
  --category code-review 2>/dev/null
echo ""
sleep 3

echo "▸ Step 3: Check for bids (worker should have auto-bid)"
echo "  Waiting for worker to bid..."
sleep 15
TASK_ID=$(cat tasks.json | python3 -c "import json,sys; t=json.load(sys.stdin)['tasks']; k=list(t.keys())[-1]; print(k)")
echo "  \$ node cli.js listing bids --task-id $TASK_ID"
echo ""
node cli.js listing bids --task-id "$TASK_ID" 2>/dev/null
echo ""
sleep 3

echo "▸ Step 4: Accept bid + lock USDC in escrow"
echo "  \$ node cli.js listing accept --task-id $TASK_ID --worker 0x2b17a2DA6172869ad3fEbb17Da76A78aE89Ab8Ec --amount 1.00"
echo ""
sleep 1
node cli.js listing accept \
  --task-id "$TASK_ID" \
  --worker "0x2b17a2DA6172869ad3fEbb17Da76A78aE89Ab8Ec" \
  --amount 1.00 2>/dev/null
echo ""
sleep 3

echo "▸ Step 5: Check escrow status on-chain"
echo "  \$ node cli.js escrow status --task-id $TASK_ID"
echo ""
node cli.js escrow status --task-id "$TASK_ID" 2>/dev/null
echo ""
sleep 3

echo "▸ Step 6: Monitor for results..."
echo "  \$ node cli.js task monitor --task-id $TASK_ID"
echo ""
timeout 60 node cli.js task monitor --task-id "$TASK_ID" 2>/dev/null
echo ""
sleep 2

echo "▸ Step 7: Release escrow — pay the worker"
echo "  \$ node cli.js escrow release --task-id $TASK_ID"
echo ""
node cli.js escrow release --task-id "$TASK_ID" 2>/dev/null
echo ""
sleep 2

echo ""
echo "═══════════════════════════════════════════════"
echo "  Done. Task posted, bid accepted, USDC locked,"
echo "  work completed, escrow released. All on-chain."
echo "═══════════════════════════════════════════════"
echo ""
