#!/bin/bash
# Clean end-to-end demo using just the CLI
cd /home/oryx/.openclaw/workspace/skills/agent-swarm

clear
echo ""
echo "  ╔═══════════════════════════════════════════════════════╗"
echo "  ║  AGENT SWARM — End-to-End Demo                       ║"
echo "  ║  Real USDC · Base mainnet · XMTP messaging           ║"
echo "  ║  Two agents · One marketplace · Zero servers          ║"
echo "  ╚═══════════════════════════════════════════════════════╝"
echo ""
sleep 3

# ── Worker daemon ──
echo "  [1/7] Start worker agent"
echo ""
echo '  $ node cli.js worker start --config worker.config.json &'
echo ""
node cli.js worker start --config worker.config.json > /tmp/worker-log.txt 2>&1 &
WPID=$!
sleep 20
grep -E "Worker agent:|Profile posted|Listening" /tmp/worker-log.txt | sed 's/^/  /'
echo ""
sleep 2

# ── Post listing ──
echo "  [2/7] Requestor posts a listing on the board"
echo ""
echo '  $ node cli.js listing post \'
echo '      --title "Audit TaskEscrowV2 contract" \'
echo '      --budget 1.00 --skills code-review'
echo ""
sleep 1
node cli.js listing post \
  --title "Audit TaskEscrowV2 contract" \
  --description "Review TaskEscrowV2.sol for security vulnerabilities" \
  --budget 1.00 --skills code-review --category code-review 2>/dev/null | sed 's/^/  /'
TASK_ID=$(python3 -c "import json; t=json.load(open('tasks.json'))['tasks']; print(list(t.keys())[-1])")
echo ""
sleep 3

# ── Worker bids ──
echo "  [3/7] Waiting for worker to see listing and auto-bid..."
echo ""
sleep 15
echo '  $ node cli.js listing bids --task-id '$TASK_ID
echo ""
node cli.js listing bids --task-id "$TASK_ID" 2>/dev/null | sed 's/^/  /'
echo ""
sleep 3

# ── Accept + escrow ──
echo "  [4/7] Accept bid → lock \$1.00 USDC in on-chain escrow"
echo ""
echo '  $ node cli.js listing accept \'
echo '      --task-id '$TASK_ID' \'
echo '      --worker 0x2b17...Ab8Ec --amount 1.00'
echo ""
sleep 1
node cli.js listing accept \
  --task-id "$TASK_ID" \
  --worker "0x2b17a2DA6172869ad3fEbb17Da76A78aE89Ab8Ec" \
  --amount 1.00 2>/dev/null | sed 's/^/  /'
echo ""
sleep 3

# ── Verify escrow ──
echo "  [5/7] Verify escrow on-chain"
echo ""
echo '  $ node cli.js escrow status --task-id '$TASK_ID
echo ""
node cli.js escrow status --task-id "$TASK_ID" 2>/dev/null | sed 's/^/  /'
echo ""
sleep 4

# ── Worker executes ──
echo "  [6/7] Worker received task, executed, submitted result"
echo ""
sleep 3
grep -E "TASK from|executor|Result submitted" /tmp/worker-log.txt | tail -4 | sed 's/^/  /'
echo ""
sleep 3

# ── Release escrow ──
echo "  [7/7] Release escrow → pay the worker"
echo ""
echo '  $ node cli.js escrow release --task-id '$TASK_ID
echo ""
node cli.js escrow release --task-id "$TASK_ID" 2>/dev/null | sed 's/^/  /'
echo ""
sleep 2

echo "  Final status:"
node cli.js escrow status --task-id "$TASK_ID" 2>/dev/null | sed 's/^/  /'
echo ""
sleep 2

echo "  ╔═══════════════════════════════════════════════════════╗"
echo "  ║  ✓ Listing posted on XMTP bulletin board             ║"
echo "  ║  ✓ Worker auto-bid via XMTP                          ║"
echo "  ║  ✓ \$1.00 USDC locked in escrow on Base               ║"
echo "  ║  ✓ Task executed by worker agent                     ║"
echo "  ║  ✓ Escrow released — worker paid                     ║"
echo "  ║                                                       ║"
echo "  ║  Contract: basescan.org/address/0xE2b1D96d...7cA24D2f ║"
echo "  ║  github.com/clawberrypi/agent-swarm                  ║"
echo "  ╚═══════════════════════════════════════════════════════╝"
echo ""

kill $WPID 2>/dev/null
