#!/usr/bin/env node
// full-demo.js — Complete end-to-end demo: discovery, escrow, reputation
//
// This demo runs the FULL protocol lifecycle:
// 1. Two agents come online on XMTP production
// 2. Worker posts profile to bulletin board
// 3. Requestor posts listing to bulletin board
// 4. Worker bids on the listing
// 5. Requestor creates private group, locks USDC in escrow
// 6. Task → Claim → Result → Release escrow
// 7. Query on-chain reputation for both agents
//
// Uses real USDC on Base mainnet. Real XMTP production. Real escrow contract.

import { createUser, createSigner, Agent, filter, encodeText } from '@xmtp/agent-sdk';
import { parseMessage, serialize, createTask, createClaim, createResult, createPayment, createListing, createProfileMsg, createBid, MessageType } from '../src/protocol.js';
import { createEscrow, releaseEscrow, getEscrowStatus, getDefaultEscrowAddress } from '../src/escrow.js';
import { buildReputation, formatReputation } from '../src/reputation.js';
import { logTask, logClaim, logResult, logPayment, logListing, logEscrow, updateEscrow, logReputation } from '../src/state.js';
import { ethers } from 'ethers';

process.loadEnvFile('.env');

// Use the main wallet as requestor, generate a fresh worker
const REQUESTOR_KEY = process.env.WALLET_PRIVATE_KEY;
const WORKER_KEY = process.env.WORKER_KEY;
if (!WORKER_KEY) { console.error('Set WORKER_KEY env var'); process.exit(1); }
const USDC_ADDRESS = process.env.USDC_ADDRESS;
const BASE_RPC = process.env.RPC_URL;
const ESCROW_ADDR = getDefaultEscrowAddress();

const USDC_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function transfer(address to, uint256 amount) returns (bool)',
];

const log = (label, ...args) => {
  const ts = new Date().toISOString().slice(11, 19);
  console.log(`[${ts}] [${label}]`, ...args);
};
const divider = (title) => {
  console.log('\n' + '─'.repeat(60));
  if (title) console.log(`  ${title}`);
  console.log('─'.repeat(60) + '\n');
};

async function main() {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║  AGENT SWARM — Full Protocol Demo                           ║
║  Discovery → Escrow → Task → Payment → Reputation           ║
║  Real USDC on Base. Real XMTP. Real escrow contract.        ║
╚══════════════════════════════════════════════════════════════╝
`);

  const provider = new ethers.JsonRpcProvider(BASE_RPC);
  const requestorWallet = new ethers.Wallet(REQUESTOR_KEY, provider);
  const workerWallet = new ethers.Wallet(WORKER_KEY, provider);

  log('INIT', `Requestor: ${requestorWallet.address}`);
  log('INIT', `Worker:    ${workerWallet.address}`);
  log('INIT', `Escrow:    ${ESCROW_ADDR}`);
  log('INIT', `Network:   Base mainnet`);

  const usdc = new ethers.Contract(USDC_ADDRESS, USDC_ABI, provider);
  const reqBal = ethers.formatUnits(await usdc.balanceOf(requestorWallet.address), 6);
  const workerBal = ethers.formatUnits(await usdc.balanceOf(workerWallet.address), 6);
  log('BALANCE', `Requestor: ${reqBal} USDC`);
  log('BALANCE', `Worker:    ${workerBal} USDC`);

  // ═══════════════════════════════════════════════════════════
  divider('PHASE 1: XMTP AGENTS COME ONLINE');
  // ═══════════════════════════════════════════════════════════

  const requestorUser = createUser(REQUESTOR_KEY);
  const workerUser = createUser(WORKER_KEY);

  log('XMTP', 'Creating requestor agent on XMTP production...');
  const requestorAgent = await Agent.create(createSigner(requestorUser), {
    env: 'production',
    dbPath: null,
  });

  log('XMTP', 'Creating worker agent on XMTP production...');
  const workerAgent = await Agent.create(createSigner(workerUser), {
    env: 'production',
    dbPath: null,
  });

  // Flow coordination
  let resolveWorkerTask, resolveRequestorClaim, resolveRequestorResult, resolveWorkerPayment;
  const workerTaskP = new Promise(r => { resolveWorkerTask = r; });
  const requestorClaimP = new Promise(r => { resolveRequestorClaim = r; });
  const requestorResultP = new Promise(r => { resolveRequestorResult = r; });
  const workerPaymentP = new Promise(r => { resolveWorkerPayment = r; });

  // Worker handler
  workerAgent.on('text', async (ctx) => {
    if (filter.fromSelf(ctx.message, ctx.client)) return;
    const msg = parseMessage(ctx.message.content);
    if (!msg) return;

    if (msg.type === MessageType.TASK) {
      log('WORKER', `Received task: "${msg.title}"`);
      log('WORKER', `Budget: ${msg.budget} USDC | Subtasks: ${msg.subtasks.length}`);
      const subtask = msg.subtasks[0];
      const claimMsg = createClaim({ taskId: msg.id, subtaskId: subtask.id, worker: workerUser.account.address });
      log('WORKER', `Claiming: "${subtask.title}"`);
      await ctx.conversation.send(encodeText(serialize(claimMsg)));
      logClaim(msg.id, subtask.id, workerUser.account.address);
      resolveWorkerTask();
    }

    if (msg.type === MessageType.PAYMENT) {
      log('WORKER', `Payment confirmed: ${msg.amount} USDC`);
      log('WORKER', `TX: ${msg.txHash}`);
      if (msg.escrowContract) log('WORKER', `Escrow: ${msg.escrowContract}`);
      resolveWorkerPayment();
    }
  });

  // Requestor handler
  requestorAgent.on('text', async (ctx) => {
    if (filter.fromSelf(ctx.message, ctx.client)) return;
    const msg = parseMessage(ctx.message.content);
    if (!msg) return;

    if (msg.type === MessageType.CLAIM) {
      log('REQUESTOR', `Worker claimed subtask: ${msg.subtaskId}`);
      resolveRequestorClaim();
    }

    if (msg.type === MessageType.RESULT) {
      log('REQUESTOR', 'Result received:');
      console.log(JSON.stringify(msg.result, null, 2));
      resolveRequestorResult();
    }
  });

  log('XMTP', 'Starting both agents...');
  await Promise.all([requestorAgent.start(), workerAgent.start()]);
  log('XMTP', 'Both agents online on XMTP production');

  // ═══════════════════════════════════════════════════════════
  divider('PHASE 2: DISCOVERY — BULLETIN BOARD');
  // ═══════════════════════════════════════════════════════════

  // Simulate bulletin board discovery (log to state for dashboard)
  const workerProfile = createProfileMsg({
    agent: workerWallet.address,
    skills: ['backend', 'smart-contracts', 'code-review'],
    rates: { 'backend': '3.00', 'smart-contracts': '5.00', 'code-review': '2.00' },
    availability: 'active',
  });
  log('BOARD', `Worker posted profile: ${workerProfile.skills.join(', ')}`);
  log('BOARD', `Rates: ${JSON.stringify(workerProfile.rates)}`);

  const taskId = `task-${Date.now()}`;
  const listing = {
    taskId,
    title: 'Build reputation query endpoint',
    description: 'Create a function that queries on-chain escrow events and returns a trust score for any wallet address. Must read from the TaskEscrow contract on Base.',
    budget: '2.00',
    skills_needed: ['backend', 'smart-contracts'],
    requestor: requestorWallet.address,
  };
  log('BOARD', `Requestor posted listing: "${listing.title}"`);
  log('BOARD', `Budget: ${listing.budget} USDC | Skills: ${listing.skills_needed.join(', ')}`);
  logListing(listing);

  const bid = createBid({
    taskId,
    worker: workerWallet.address,
    price: '2.00',
    estimatedTime: '1h',
  });
  log('BOARD', `Worker bid on listing: ${bid.price} USDC, est. ${bid.estimatedTime}`);
  log('BOARD', 'Requestor accepts bid. Moving to private group.');

  // ═══════════════════════════════════════════════════════════
  divider('PHASE 3: ESCROW — LOCK USDC ON-CHAIN');
  // ═══════════════════════════════════════════════════════════

  const deadline = Math.floor(Date.now() / 1000) + 86400; // 24h
  log('ESCROW', `Locking 2.00 USDC in escrow for task ${taskId}`);
  log('ESCROW', `Worker: ${workerWallet.address}`);
  log('ESCROW', `Deadline: ${new Date(deadline * 1000).toISOString()}`);
  log('ESCROW', `Contract: ${ESCROW_ADDR}`);

  log('ESCROW', 'Approving USDC spend...');
  const { txHash: escrowTxHash, taskIdHash } = await createEscrow(requestorWallet, ESCROW_ADDR, {
    taskId,
    worker: workerWallet.address,
    amount: '2.00',
    deadline,
  });
  log('ESCROW', `Escrow created! TX: ${escrowTxHash}`);
  log('ESCROW', `Task hash: ${taskIdHash}`);

  const escrowStatus = await getEscrowStatus(provider, ESCROW_ADDR, taskId);
  log('ESCROW', `Status: ${escrowStatus.status} | Amount: ${escrowStatus.amount} USDC`);

  logEscrow({
    taskId,
    requestor: requestorWallet.address,
    worker: workerWallet.address,
    amount: '2.00',
    deadline,
    status: 'active',
    txHash: escrowTxHash,
  });

  // ═══════════════════════════════════════════════════════════
  divider('PHASE 4: TASK EXECUTION OVER XMTP');
  // ═══════════════════════════════════════════════════════════

  log('XMTP', 'Creating private XMTP group for this task...');
  const group = await requestorAgent.createGroupWithAddresses(
    [workerUser.account.address],
    { name: listing.title, description: listing.description }
  );
  log('XMTP', `Group: ${group.id.slice(0, 30)}...`);

  await sleep(2000);

  const task = createTask({
    id: taskId,
    title: listing.title,
    description: listing.description,
    budget: listing.budget,
    subtasks: [{
      id: 'rep-endpoint',
      title: 'Build reputation query function',
      description: 'Query TaskEscrow events, calculate trust score (0-100), return reputation object with completion rate, dispute rate, volume, total earned/spent.',
    }],
    requirements: 'Must use ethers.js, read EscrowCreated/Released/Disputed/Refunded events, return structured JSON.',
  });

  log('REQUESTOR', `Posting task: "${task.title}"`);
  await group.send(encodeText(serialize(task)));
  logTask(task, requestorWallet.address);

  log('FLOW', 'Waiting for worker to claim...');
  await withTimeout(workerTaskP, 30000, 'Worker never received task');
  await withTimeout(requestorClaimP, 15000, 'Never received claim');

  // Worker "builds" and submits
  await sleep(2000);
  log('WORKER', 'Building reputation query endpoint...');
  await sleep(1000);

  await workerAgent.client.conversations.sync();
  const workerConvos = await workerAgent.client.conversations.list();
  const workerGroup = workerConvos.find(c => c.id === group.id);

  if (workerGroup) {
    const resultMsg = createResult({
      taskId,
      subtaskId: 'rep-endpoint',
      worker: workerUser.account.address,
      result: {
        deliverable: 'reputation.js module',
        exports: ['buildReputation(provider, escrowAddress, agentAddress)', 'formatReputation(rep)', 'createReputationQuery()', 'createReputationResponse()'],
        trustScoreFormula: {
          completionRate: '0-70 points',
          volumeBonus: '0-20 points (logarithmic)',
          valueBonus: '0-10 points',
          disputePenalty: '-0.5 per dispute rate pct',
        },
        tests: 'verified against live escrow contract events on Base',
        code: 'https://github.com/clawberrypi/agent-swarm/blob/main/src/reputation.js',
      },
    });
    log('WORKER', 'Submitting completed reputation module...');
    await workerGroup.send(encodeText(serialize(resultMsg)));
    logResult(taskId, 'rep-endpoint', workerUser.account.address);
  }

  log('FLOW', 'Waiting for requestor to validate...');
  await withTimeout(requestorResultP, 30000, 'Never received result');

  // ═══════════════════════════════════════════════════════════
  divider('PHASE 5: RELEASE ESCROW — WORKER GETS PAID');
  // ═══════════════════════════════════════════════════════════

  log('ESCROW', 'Requestor releasing escrow...');
  const { txHash: releaseTxHash } = await releaseEscrow(requestorWallet, ESCROW_ADDR, taskId);
  log('ESCROW', `Released! TX: ${releaseTxHash}`);

  const finalStatus = await getEscrowStatus(provider, ESCROW_ADDR, taskId);
  log('ESCROW', `Final status: ${finalStatus.status}`);

  updateEscrow(taskId, 'released', releaseTxHash);

  // Send payment confirmation over XMTP
  const payMsg = createPayment({
    taskId,
    subtaskId: 'rep-endpoint',
    worker: workerUser.account.address,
    txHash: releaseTxHash,
    amount: '2.00',
    escrowContract: ESCROW_ADDR,
  });
  await group.send(encodeText(serialize(payMsg)));
  logPayment(taskId, workerUser.account.address, '2.00', releaseTxHash);

  log('FLOW', 'Waiting for worker to confirm payment...');
  await withTimeout(workerPaymentP, 15000, 'Worker never got payment');

  // ═══════════════════════════════════════════════════════════
  divider('PHASE 6: ON-CHAIN REPUTATION');
  // ═══════════════════════════════════════════════════════════

  log('REPUTATION', 'Querying on-chain reputation from escrow contract events...\n');

  let reqRep = { trustScore: '?' }, workerRep = { trustScore: '?' };
  try {
    reqRep = await buildReputation(provider, ESCROW_ADDR, requestorWallet.address);
    console.log('Requestor reputation:');
    console.log(formatReputation(reqRep));
    logReputation(reqRep);

    console.log();

    workerRep = await buildReputation(provider, ESCROW_ADDR, workerWallet.address);
    console.log('Worker reputation:');
    console.log(formatReputation(workerRep));
    logReputation(workerRep);
  } catch (e) {
    log('REPUTATION', `RPC error (non-fatal): ${e.message?.slice(0, 80)}`);
    log('REPUTATION', 'Reputation queries require eth_getLogs — public RPCs may rate-limit.');
    log('REPUTATION', 'Use a dedicated RPC (Alchemy/QuickNode) for reliable reputation queries.');
  }

  // ═══════════════════════════════════════════════════════════
  divider('FINAL BALANCES');
  // ═══════════════════════════════════════════════════════════

  const reqBalFinal = ethers.formatUnits(await usdc.balanceOf(requestorWallet.address), 6);
  const workerBalFinal = ethers.formatUnits(await usdc.balanceOf(workerWallet.address), 6);

  console.log(`
╔══════════════════════════════════════════════════════════════╗
║                    DEMO COMPLETE                             ║
╠══════════════════════════════════════════════════════════════╣
║  Requestor: ${reqBal} → ${reqBalFinal} USDC`.padEnd(63) + `║
║  Worker:    ${workerBal} → ${workerBalFinal} USDC`.padEnd(63) + `║
╠══════════════════════════════════════════════════════════════╣
║  Requestor trust score: ${reqRep.trustScore}/100`.padEnd(63) + `║
║  Worker trust score:    ${workerRep.trustScore}/100`.padEnd(63) + `║
╠══════════════════════════════════════════════════════════════╣
║  Protocol: 9 message types over XMTP                        ║
║  Escrow: zero-fee, auto-release, verified on BaseScan        ║
║  Reputation: derived from on-chain escrow history            ║
║  Network: Base mainnet | XMTP production                     ║
╠══════════════════════════════════════════════════════════════╣
║  To run this yourself:                                       ║
║  1. npx clawhub install xmtp-agent-swarm                     ║
║  2. cp .env.example .env                                     ║
║  3. Add your private key to .env                             ║
║  4. Fund wallet with ETH on Base                             ║
║  5. node scripts/full-demo.js                                ║
╚══════════════════════════════════════════════════════════════╝
`);

  await requestorAgent.stop();
  await workerAgent.stop();
  process.exit(0);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function withTimeout(p, ms, msg) {
  return Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error(`Timeout: ${msg}`)), ms))]);
}

main().catch(err => { console.error('Demo failed:', err); process.exit(1); });
