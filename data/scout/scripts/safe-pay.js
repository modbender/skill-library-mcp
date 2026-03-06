#!/usr/bin/env node
/**
 * Scout Safe-Pay: Trust-gated USDC payments
 * Usage: node safe-pay.js --agent <name> --to <address> --amount <usdc> --task "description"
 *        node safe-pay.js --check <address>   (check on-chain activity)
 */

const { MoltbookClient } = require('./lib/moltbook');
const { TrustScorer } = require('./lib/scoring');
const { USDCClient } = require('./lib/usdc');

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--agent' && argv[i + 1]) args.agent = argv[++i];
    else if (argv[i] === '--to' && argv[i + 1]) args.to = argv[++i];
    else if (argv[i] === '--amount' && argv[i + 1]) args.amount = parseFloat(argv[++i]);
    else if (argv[i] === '--task' && argv[i + 1]) args.task = argv[++i];
    else if (argv[i] === '--check' && argv[i + 1]) args.check = argv[++i];
    else if (argv[i] === '--json') args.json = true;
    else if (argv[i] === '--dry-run') args.dryRun = true;
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  const moltbookKey = process.env.MOLTBOOK_API_KEY;
  const privateKey = process.env.SCOUT_PRIVATE_KEY;

  // Mode: check on-chain activity
  if (args.check) {
    const usdc = new USDCClient(privateKey);
    const activity = await usdc.checkActivity(args.check);
    console.log('\n=== ON-CHAIN ACTIVITY CHECK ===');
    console.log(`Address: ${activity.address}`);
    console.log(`Chain: ${activity.chain}`);
    console.log(`USDC Balance: ${activity.usdcBalance}`);
    console.log(`ETH Balance: ${activity.ethBalance}`);
    console.log(`Has USDC: ${activity.hasUSDC ? 'Yes' : 'No'}`);
    console.log(`Has Gas: ${activity.hasGas ? 'Yes' : 'No'}`);
    return;
  }

  // Mode: safe payment
  if (!args.agent || !args.amount) {
    console.error(`
Scout Safe-Pay: Trust-gated USDC payments

Usage:
  node safe-pay.js --agent <name> --to <address> --amount <usdc> --task "description" [--dry-run] [--json]
  node safe-pay.js --check <address>

Options:
  --agent     Moltbook agent name to check trust for
  --to        Recipient wallet address (Base Sepolia)
  --amount    Amount in USDC
  --task      Task description
  --dry-run   Check trust but don't send USDC
  --check     Check on-chain activity for an address
  --json      Output as JSON

Environment:
  MOLTBOOK_API_KEY    Moltbook API key (required)
  SCOUT_PRIVATE_KEY   Wallet private key for sending USDC (optional for dry-run)
    `);
    process.exit(1);
  }

  if (!moltbookKey) {
    console.error('Error: MOLTBOOK_API_KEY required');
    process.exit(1);
  }

  const client = new MoltbookClient(moltbookKey);
  const scorer = new TrustScorer();
  const usdc = new USDCClient(privateKey);

  try {
    // Step 1: Trust check
    console.log(`\n[1/3] Running trust check on ${args.agent}...`);
    const profile = await client.getProfile(args.agent);
    const trustResult = scorer.score(profile);

    console.log(trustResult.summary);

    // Step 2: Payment recommendation
    console.log(`[2/3] Evaluating payment: ${args.amount} USDC for "${args.task || 'unspecified task'}"...`);

    const payResult = await (args.dryRun
      ? mockSafePay(trustResult, args.to, args.amount, args.task)
      : usdc.safePay(trustResult, args.to || '0x0000000000000000000000000000000000000000', args.amount, args.task || 'unspecified')
    );

    // Step 3: Result
    console.log(`\n[3/3] Payment Decision:`);
    console.log(`  Status: ${payResult.status}`);
    console.log(`  Trust: ${payResult.trustScore}/100 (${payResult.trustLevel})`);

    if (payResult.status === 'APPROVED') {
      console.log(`  Upfront: ${payResult.upfrontAmount} USDC`);
      console.log(`  Escrowed: ${payResult.escrowAmount} USDC`);
      console.log(`  Terms: ${payResult.terms}`);

      if (payResult.transactions?.length > 0) {
        payResult.transactions.forEach(tx => {
          console.log(`\n  Transaction sent!`);
          console.log(`    Hash: ${tx.txHash}`);
          console.log(`    Explorer: ${tx.explorerUrl}`);
        });
      }

      if (payResult.escrowNote) {
        console.log(`\n  ${payResult.escrowNote}`);
      }

      if (args.dryRun) {
        console.log(`\n  (DRY RUN - no USDC was sent)`);
      }
    } else {
      console.log(`  Reason: ${payResult.reason}`);
      if (payResult.suggestion) console.log(`  Suggestion: ${payResult.suggestion}`);
    }

    if (payResult.flags?.length > 0) {
      console.log(`\n  Flags: ${payResult.flags.join(', ')}`);
    }

    if (args.json) {
      console.log('\n' + JSON.stringify(payResult, null, 2));
    }

  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

// Mock for dry-run mode without wallet
function mockSafePay(trustResult, toAddress, amount, task) {
  const rec = trustResult.recommendation;

  if (rec.level === 'VERY_LOW') {
    return {
      status: 'BLOCKED',
      reason: `Trust score too low (${trustResult.score}/100)`,
      trustScore: trustResult.score,
      trustLevel: rec.level,
      recommendation: rec,
      flags: trustResult.flags
    };
  }

  let upfrontPct = rec.level === 'HIGH' ? 1.0 : rec.level === 'MEDIUM' ? 0.5 : 0.0;

  return {
    status: amount > rec.maxTransaction ? 'OVER_LIMIT' : 'APPROVED',
    reason: amount > rec.maxTransaction ? `Exceeds max ${rec.maxTransaction} USDC` : undefined,
    suggestion: amount > rec.maxTransaction ? `Split into smaller transactions` : undefined,
    trustScore: trustResult.score,
    trustLevel: rec.level,
    agentName: trustResult.agentName,
    requestedAmount: amount,
    taskDescription: task,
    upfrontAmount: Math.round(amount * upfrontPct * 100) / 100,
    escrowAmount: Math.round(amount * (1 - upfrontPct) * 100) / 100,
    toAddress: toAddress || '(not provided)',
    terms: rec.escrowTerms,
    flags: trustResult.flags,
    transactions: []
  };
}

main();
