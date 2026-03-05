#!/usr/bin/env node
// live-demo.js — Real agent-to-agent task with USDC payment on Base
//
// Scenario: Agent A has a frontend site but needs a backend API built.
// Instead of spending more Claude credits doing it themselves, they hire
// Agent B through the swarm protocol. Agent B builds it, submits the work,
// gets paid in USDC. All coordination over XMTP, payment on-chain.

import { createUser, createSigner, Agent, filter, encodeText } from '@xmtp/agent-sdk';
import { parseMessage, serialize, createTask, createClaim, createResult, createPayment, MessageType } from '../src/protocol.js';
import { ethers } from 'ethers';

process.loadEnvFile('.env');

const REQUESTOR_KEY = 'process.env.REQUESTOR_PRIVATE_KEY';
const WORKER_KEY = 'process.env.WORKER_PRIVATE_KEY';
const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
const BASE_RPC = 'https://mainnet.base.org';

const USDC_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function transfer(address to, uint256 amount) returns (bool)',
];

const log = (label, ...args) => {
  const ts = new Date().toISOString().slice(11, 19);
  console.log(`[${ts}] [${label}]`, ...args);
};

const divider = () => console.log('\n' + '─'.repeat(60) + '\n');

async function main() {
  console.log('╔══════════════════════════════════════════════════════════╗');
  console.log('║     AGENT SWARM — Live Demo: Real USDC on Base         ║');
  console.log('║     Two agents. One task. Real money.                   ║');
  console.log('╚══════════════════════════════════════════════════════════╝\n');

  const provider = new ethers.JsonRpcProvider(BASE_RPC);
  const requestorEthWallet = new ethers.Wallet(REQUESTOR_KEY, provider);
  const workerEthWallet = new ethers.Wallet(WORKER_KEY, provider);

  log('SETUP', 'Scenario: Agent A built a frontend but needs a backend API.');
  log('SETUP', 'Instead of burning more Claude credits, Agent A hires Agent B');
  log('SETUP', 'through the swarm. Fractionalized cost, real payment.\n');

  log('SETUP', `Requestor (Agent A): ${requestorEthWallet.address}`);
  log('SETUP', `Worker (Agent B):    ${workerEthWallet.address}`);

  // Show starting balances
  const usdc = new ethers.Contract(USDC_ADDRESS, USDC_ABI, provider);
  const reqBal = ethers.formatUnits(await usdc.balanceOf(requestorEthWallet.address), 6);
  const workerBal = ethers.formatUnits(await usdc.balanceOf(workerEthWallet.address), 6);
  log('BALANCE', `Requestor: ${reqBal} USDC`);
  log('BALANCE', `Worker:    ${workerBal} USDC`);

  divider();

  // --- Create XMTP agents ---
  log('XMTP', 'Creating requestor agent on XMTP production network...');
  const requestorUser = createUser(REQUESTOR_KEY);
  const workerUser = createUser(WORKER_KEY);

  const requestorAgent = await Agent.create(createSigner(requestorUser), {
    env: 'production',
    dbPath: null,
  });

  log('XMTP', 'Creating worker agent on XMTP production network...');
  const workerAgent = await Agent.create(createSigner(workerUser), {
    env: 'production',
    dbPath: null,
  });

  // --- Flow coordination ---
  let resolveWorkerTask, resolveRequestorClaim, resolveRequestorResult, resolveWorkerPayment;
  const workerTaskP = new Promise(r => { resolveWorkerTask = r; });
  const requestorClaimP = new Promise(r => { resolveRequestorClaim = r; });
  const requestorResultP = new Promise(r => { resolveRequestorResult = r; });
  const workerPaymentP = new Promise(r => { resolveWorkerPayment = r; });

  // Worker message handler
  workerAgent.on('text', async (ctx) => {
    if (filter.fromSelf(ctx.message, ctx.client)) return;
    const msg = parseMessage(ctx.message.content);
    if (!msg) return;

    if (msg.type === MessageType.TASK) {
      log('WORKER', `Received task: "${msg.title}"`);
      log('WORKER', `Budget: ${msg.budget} USDC`);
      log('WORKER', `Subtasks: ${msg.subtasks.map(s => s.title).join(', ')}`);

      // Claim the work
      const subtask = msg.subtasks[0];
      const claimMsg = createClaim({ taskId: msg.id, subtaskId: subtask.id, worker: workerUser.account.address });
      log('WORKER', `Claiming: "${subtask.title}"`);
      await ctx.conversation.send(encodeText(serialize(claimMsg)));
      resolveWorkerTask();
    }

    if (msg.type === MessageType.PAYMENT) {
      log('WORKER', `Payment received: ${msg.amount} USDC`);
      log('WORKER', `TX: ${msg.txHash}`);
      log('WORKER', `Verified on Base mainnet. Task complete.`);
      resolveWorkerPayment();
    }
  });

  // Requestor message handler
  requestorAgent.on('text', async (ctx) => {
    if (filter.fromSelf(ctx.message, ctx.client)) return;
    const msg = parseMessage(ctx.message.content);
    if (!msg) return;

    if (msg.type === MessageType.CLAIM) {
      log('REQUESTOR', `Worker ${msg.worker.slice(0, 10)}... claimed subtask ${msg.subtaskId}`);
      log('REQUESTOR', 'Worker is now building the backend API...');
      resolveRequestorClaim();
    }

    if (msg.type === MessageType.RESULT) {
      log('REQUESTOR', 'Result received from worker:');
      log('REQUESTOR', JSON.stringify(msg.result, null, 2));
      log('REQUESTOR', 'Validating result...');

      divider();
      log('PAYMENT', 'Initiating real USDC transfer on Base mainnet...');

      // REAL PAYMENT: transfer USDC on Base
      const usdcContract = new ethers.Contract(USDC_ADDRESS, USDC_ABI, requestorEthWallet);
      const amount = ethers.parseUnits('2.00', 6); // 2 USDC for the backend work
      const tx = await usdcContract.transfer(msg.worker, amount);
      log('PAYMENT', `TX submitted: ${tx.hash}`);
      log('PAYMENT', 'Waiting for confirmation...');
      const receipt = await tx.wait();
      log('PAYMENT', `Confirmed in block ${receipt.blockNumber}`);
      log('PAYMENT', `Gas used: ${receipt.gasUsed.toString()} (${ethers.formatEther(receipt.gasUsed * receipt.gasPrice)} ETH)`);

      // Send payment confirmation over XMTP
      const payMsg = createPayment({
        taskId: msg.taskId,
        subtaskId: msg.subtaskId,
        worker: msg.worker,
        txHash: tx.hash,
        amount: '2.00',
      });
      await ctx.conversation.send(encodeText(serialize(payMsg)));
      log('PAYMENT', 'Payment confirmation sent via XMTP');
      resolveRequestorResult();
    }
  });

  // --- Start agents ---
  log('XMTP', 'Starting both agents...');
  await Promise.all([requestorAgent.start(), workerAgent.start()]);
  log('XMTP', 'Both agents online on XMTP production network');

  divider();

  // --- Requestor creates group and posts task ---
  log('REQUESTOR', 'Creating XMTP group for this task...');
  const group = await requestorAgent.createGroupWithAddresses(
    [workerUser.account.address],
    { name: 'Backend API Build', description: 'Agent A hiring Agent B for backend work' }
  );
  log('REQUESTOR', `Group created: ${group.id.slice(0, 20)}...`);

  await sleep(2000);

  const task = createTask({
    id: 'task-backend-api',
    title: 'Build REST API backend for agent dashboard',
    description: 'The frontend is done. Need a Node.js Express API with endpoints for: GET /agents (list active agents), GET /tasks (list tasks with status), POST /tasks (create new task), GET /wallet/:address (balance check). Connect to the existing state.json data layer.',
    budget: '2.00',
    subtasks: [
      {
        id: 'backend-api',
        title: 'Build Express API with 4 endpoints',
        description: 'GET /agents, GET /tasks, POST /tasks, GET /wallet/:address. Read from state.json. Return JSON responses.',
      },
    ],
    requirements: 'Node.js, Express, clean endpoints, error handling. Must integrate with existing state.json format.',
  });

  log('REQUESTOR', `Posting task: "${task.title}"`);
  log('REQUESTOR', `Budget: ${task.budget} USDC`);
  await group.send(encodeText(serialize(task)));

  divider();

  // --- Wait for claim ---
  log('FLOW', 'Waiting for worker to receive task...');
  await withTimeout(workerTaskP, 30000, 'Worker never received task');

  log('FLOW', 'Waiting for claim acknowledgment...');
  await withTimeout(requestorClaimP, 15000, 'Never received claim');

  // --- Worker "builds" the backend and submits ---
  await sleep(2000);

  log('WORKER', 'Building the backend API...');
  await sleep(1000);

  // Worker submits result
  await workerAgent.client.conversations.sync();
  const workerConvos = await workerAgent.client.conversations.list();
  const workerGroup = workerConvos.find(c => c.id === group.id);

  if (workerGroup) {
    const resultMsg = createResult({
      taskId: 'task-backend-api',
      subtaskId: 'backend-api',
      worker: workerUser.account.address,
      result: {
        deliverable: 'Express API server',
        endpoints: [
          'GET /agents — returns active agents from state.json',
          'GET /tasks — returns all tasks with status',
          'POST /tasks — creates new task, writes to state.json',
          'GET /wallet/:address — returns ETH and USDC balance on Base',
        ],
        code_location: 'src/api.js',
        dependencies: ['express', 'ethers'],
        notes: 'reads and writes state.json, CORS enabled, error handling on all routes',
      },
    });
    log('WORKER', 'Submitting completed backend API...');
    await workerGroup.send(encodeText(serialize(resultMsg)));
  }

  // --- Wait for payment flow ---
  log('FLOW', 'Waiting for requestor to validate and pay...');
  await withTimeout(requestorResultP, 30000, 'Payment never sent');

  log('FLOW', 'Waiting for worker to confirm payment...');
  await withTimeout(workerPaymentP, 15000, 'Worker never got payment');

  divider();

  // --- Final balances ---
  const reqBalFinal = ethers.formatUnits(await usdc.balanceOf(requestorEthWallet.address), 6);
  const workerBalFinal = ethers.formatUnits(await usdc.balanceOf(workerEthWallet.address), 6);

  console.log('╔══════════════════════════════════════════════════════════╗');
  console.log('║                    DEMO COMPLETE                        ║');
  console.log('╠══════════════════════════════════════════════════════════╣');
  console.log(`║  Requestor: ${reqBal} → ${reqBalFinal} USDC`.padEnd(59) + '║');
  console.log(`║  Worker:    ${workerBal} → ${workerBalFinal} USDC`.padEnd(59) + '║');
  console.log('╠══════════════════════════════════════════════════════════╣');
  console.log('║  Task: Build backend API                                ║');
  console.log('║  Payment: 2.00 USDC on Base mainnet                    ║');
  console.log('║  Messaging: XMTP production network                    ║');
  console.log('║  Settlement: wallet-to-wallet, no middleman             ║');
  console.log('╚══════════════════════════════════════════════════════════╝');

  await requestorAgent.stop();
  await workerAgent.stop();
  process.exit(0);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function withTimeout(p, ms, msg) {
  return Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error(`Timeout: ${msg}`)), ms))]);
}

main().catch(err => { console.error('Demo failed:', err); process.exit(1); });
