#!/usr/bin/env node
// demo.js — Self-contained demo: two XMTP agents (requestor + worker) communicate via group
//
// Uses real XMTP messaging on the 'dev' network. No coordinator, no server.

import { createUser, createSigner, Agent, filter, encodeText } from '@xmtp/agent-sdk';
import { parseMessage, serialize, createTask, createClaim, createResult, createPayment, MessageType } from '../src/protocol.js';

// Load .env
process.loadEnvFile('.env');

const log = (label, ...args) => console.log(`\n[${label}]`, ...args);

async function main() {
  console.log('=== XMTP Agent Swarm Demo ===\n');

  // --- Create two separate XMTP agents from different wallets ---
  const requestorUser = createUser(process.env.WALLET_PRIVATE_KEY);
  const workerUser = createUser(); // random new wallet for worker

  log('SETUP', `Requestor address: ${requestorUser.account.address}`);
  log('SETUP', `Worker address:    ${workerUser.account.address}`);

  // Create agents
  log('SETUP', 'Creating requestor agent...');
  const requestorAgent = await Agent.create(createSigner(requestorUser), {
    env: 'dev',
    dbPath: null,
  });

  log('SETUP', 'Creating worker agent...');
  const workerAgent = await Agent.create(createSigner(workerUser), {
    env: 'dev',
    dbPath: null,
  });

  // --- Set up message flow tracking ---
  let workerReceivedTask = false;
  let requestorReceivedClaim = false;
  let requestorReceivedResult = false;
  let workerReceivedPayment = false;

  // Resolve functions for async flow coordination
  let resolveWorkerTask, resolveRequestorClaim, resolveRequestorResult, resolveWorkerPayment;
  const workerTaskPromise = new Promise(r => { resolveWorkerTask = r; });
  const requestorClaimPromise = new Promise(r => { resolveRequestorClaim = r; });
  const requestorResultPromise = new Promise(r => { resolveRequestorResult = r; });
  const workerPaymentPromise = new Promise(r => { resolveWorkerPayment = r; });

  // Worker: on receiving a task → claim first subtask
  workerAgent.on('text', async (ctx) => {
    if (filter.fromSelf(ctx.message, ctx.client)) return;
    const msg = parseMessage(ctx.message.content);
    if (!msg) return;

    if (msg.type === MessageType.TASK && !workerReceivedTask) {
      workerReceivedTask = true;
      log('WORKER', `📋 Received task: "${msg.title}" with ${msg.subtasks.length} subtask(s)`);

      // Claim the first subtask
      const subtask = msg.subtasks[0];
      const claimMsg = createClaim({ taskId: msg.id, subtaskId: subtask.id, worker: workerUser.account.address });
      log('WORKER', `🙋 Claiming subtask: "${subtask.title}"`);
      await ctx.conversation.send(encodeText(serialize(claimMsg)));
      resolveWorkerTask();
    }

    if (msg.type === MessageType.PAYMENT && !workerReceivedPayment) {
      workerReceivedPayment = true;
      log('WORKER', `💰 Payment received! tx: ${msg.txHash}, amount: ${msg.amount} USDC`);
      resolveWorkerPayment();
    }
  });

  // Requestor: on receiving a claim → wait, then on result → send payment
  requestorAgent.on('text', async (ctx) => {
    if (filter.fromSelf(ctx.message, ctx.client)) return;
    const msg = parseMessage(ctx.message.content);
    if (!msg) return;

    if (msg.type === MessageType.CLAIM && !requestorReceivedClaim) {
      requestorReceivedClaim = true;
      log('REQUESTOR', `✅ Worker ${msg.worker.slice(0, 10)}... claimed subtask ${msg.subtaskId}`);
      resolveRequestorClaim();
    }

    if (msg.type === MessageType.RESULT && !requestorReceivedResult) {
      requestorReceivedResult = true;
      log('REQUESTOR', `📦 Result received from ${msg.worker.slice(0, 10)}...`);
      log('REQUESTOR', `   Result data:`, JSON.stringify(msg.result));

      // Send payment confirmation
      const payMsg = createPayment({
        taskId: msg.taskId,
        subtaskId: msg.subtaskId,
        worker: msg.worker,
        txHash: '0xdemo_tx_' + Date.now().toString(16),
        amount: '0.50',
      });
      log('REQUESTOR', `💸 Sending payment confirmation...`);
      await ctx.conversation.send(encodeText(serialize(payMsg)));
      resolveRequestorResult();
    }
  });

  // --- Start both agents ---
  log('SETUP', 'Starting agents...');
  await Promise.all([requestorAgent.start(), workerAgent.start()]);
  log('SETUP', 'Both agents online ✓');

  // --- Requestor creates a group and invites the worker ---
  log('REQUESTOR', 'Creating swarm group...');
  const group = await requestorAgent.createGroupWithAddresses(
    [workerUser.account.address],
    { name: 'Demo Swarm', description: 'Agent swarm demo group' }
  );
  log('REQUESTOR', `Group created: ${group.id}`);

  // Give XMTP a moment to propagate the group
  await sleep(2000);

  // --- Requestor posts a task ---
  const task = createTask({
    id: 'task-001',
    title: 'Research Base Sepolia Faucets',
    description: 'Find and list working Base Sepolia testnet faucets',
    budget: '1.00',
    subtasks: [
      { id: 'sub-001', title: 'Find faucet URLs', description: 'Search for Base Sepolia faucets' },
    ],
    requirements: 'Return at least 3 faucet URLs',
  });

  log('REQUESTOR', `📤 Posting task: "${task.title}"`);
  await group.send(encodeText(serialize(task)));

  // --- Wait for the flow to complete ---
  log('FLOW', 'Waiting for worker to see task...');
  await withTimeout(workerTaskPromise, 30000, 'Worker never received task');

  log('FLOW', 'Waiting for requestor to see claim...');
  await withTimeout(requestorClaimPromise, 15000, 'Requestor never received claim');

  // Worker submits a result
  await sleep(1000);

  // We need worker's view of the group to send messages
  // Worker sends result through their agent's text handler — let's send it directly
  // The worker needs to find the conversation. Let's sync and send.
  await workerAgent.client.conversations.sync();
  const workerConvos = await workerAgent.client.conversations.list();
  const workerGroup = workerConvos.find(c => c.id === group.id);

  if (workerGroup) {
    const resultMsg = createResult({
      taskId: 'task-001',
      subtaskId: 'sub-001',
      worker: workerUser.account.address,
      result: {
        faucets: [
          'https://www.coinbase.com/faucets/base-ethereum-goerli-faucet',
          'https://faucet.quicknode.com/base/sepolia',
          'https://www.alchemy.com/faucets/base-sepolia',
        ],
      },
    });
    log('WORKER', `📤 Submitting result...`);
    await workerGroup.send(encodeText(serialize(resultMsg)));
  }

  log('FLOW', 'Waiting for requestor to receive result...');
  await withTimeout(requestorResultPromise, 15000, 'Requestor never received result');

  log('FLOW', 'Waiting for worker to receive payment...');
  await withTimeout(workerPaymentPromise, 15000, 'Worker never received payment');

  // --- Done ---
  console.log('\n' + '='.repeat(50));
  console.log('✅ Demo complete! Full message flow:');
  console.log('   1. Requestor created group & posted task');
  console.log('   2. Worker received task & claimed subtask');
  console.log('   3. Worker submitted result');
  console.log('   4. Requestor received result & sent payment');
  console.log('   5. Worker received payment confirmation');
  console.log('='.repeat(50) + '\n');

  // Clean shutdown
  await requestorAgent.stop();
  await workerAgent.stop();
  process.exit(0);
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function withTimeout(promise, ms, msg) {
  return Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error(`Timeout: ${msg}`)), ms)),
  ]);
}

main().catch(err => {
  console.error('Demo failed:', err);
  process.exit(1);
});
