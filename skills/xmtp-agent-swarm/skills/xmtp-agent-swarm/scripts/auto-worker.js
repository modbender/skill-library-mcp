#!/usr/bin/env node
// auto-worker.js — Autonomous worker agent that sits on the bulletin board,
// polls for new listings, evaluates against its skills, and auto-bids.

import { createUser, createSigner, Agent, encodeText } from '@xmtp/agent-sdk';
import { parseMessage, serialize, MessageType, createClaim, createResult } from '../src/protocol.js';
import fs from 'fs';

const BOARD_CONFIG = JSON.parse(fs.readFileSync('board.json', 'utf-8'));
const WORKER_KEY = BOARD_CONFIG.workerKey;

const MY_SKILLS = ['backend', 'smart-contracts', 'code-review', 'research', 'api-development'];
const MY_RATES = { 'backend': 3.00, 'smart-contracts': 5.00, 'code-review': 2.00, 'research': 1.50, 'api-development': 4.00 };
const MAX_BID = 10.00;
const MIN_BID = 0.50;
const POLL_INTERVAL = 5000; // 5 seconds

const log = (label, ...args) => {
  const ts = new Date().toISOString().slice(11, 19);
  console.log(`[${ts}] [${label}]`, ...args);
};

const seenMessages = new Set();
const seenListings = new Set();

async function main() {
  console.log(`
╔════════════════════════════════════════════════╗
║  AUTO-WORKER — Autonomous Agent on the Board   ║
║  Watches listings. Evaluates. Bids. Works.     ║
╚════════════════════════════════════════════════╝
`);

  const user = createUser(WORKER_KEY);
  const workerAddress = user.account.address;
  log('INIT', `Worker: ${workerAddress}`);
  log('INIT', `Skills: ${MY_SKILLS.join(', ')}`);
  log('INIT', `Board: ${BOARD_CONFIG.boardId}`);

  const agent = await Agent.create(createSigner(user), {
    env: 'production',
    dbPath: '.xmtp-worker2',
  });
  await agent.start();
  log('XMTP', 'online on XMTP production');

  await agent.client.conversations.sync();
  const convos = await agent.client.conversations.list();
  const board = convos.find(c => c.id === BOARD_CONFIG.boardId);

  if (!board) {
    log('ERROR', 'board not found');
    process.exit(1);
  }

  // Post profile
  const profile = {
    type: MessageType.PROFILE,
    agent: workerAddress,
    skills: MY_SKILLS,
    rates: MY_RATES,
    availability: 'active',
    description: 'autonomous worker. backend, smart contracts, code review, research, APIs. running 24/7.',
  };
  await board.send(encodeText(JSON.stringify(profile)));
  log('BOARD', 'profile posted');

  // Poll loop
  log('READY', `polling board every ${POLL_INTERVAL/1000}s for new listings...`);

  async function poll() {
    try {
      await board.sync();
      const msgs = await board.messages({ limit: 20 });

      for (const m of msgs) {
        const msgId = m.id;
        if (seenMessages.has(msgId)) continue;
        seenMessages.add(msgId);

        // Skip own messages
        if (m.senderInboxId === agent.client.inboxId) continue;

        let parsed;
        try {
          const text = typeof m.content === 'string' ? m.content : JSON.stringify(m.content);
          parsed = JSON.parse(text);
        } catch(e) { continue; }

        if (!parsed || !parsed.type) continue;

        // Handle listings
        if (parsed.type === 'listing' || parsed.type === MessageType.LISTING) {
          if (seenListings.has(parsed.taskId)) continue;
          seenListings.add(parsed.taskId);

          log('BOARD', `new listing: "${parsed.title}"`);
          log('BOARD', `  budget: $${parsed.budget} USDC | skills: ${(parsed.skills_needed || []).join(', ')}`);

          const needed = parsed.skills_needed || [];
          const matches = needed.filter(s => MY_SKILLS.includes(s));
          const budget = parseFloat(parsed.budget);

          if (matches.length === 0 && needed.length > 0) {
            log('EVAL', `skip: no skill match`);
            continue;
          }
          if (budget > MAX_BID || budget < MIN_BID) {
            log('EVAL', `skip: budget $${budget} out of range`);
            continue;
          }

          let bidPrice = budget;
          if (matches.length > 0) {
            const avgRate = matches.reduce((sum, s) => sum + (MY_RATES[s] || 2.00), 0) / matches.length;
            bidPrice = Math.min(budget, avgRate);
          }

          log('EVAL', `match: ${matches.length}/${needed.length} skills | bidding $${bidPrice.toFixed(2)}`);

          const bid = {
            type: MessageType.BID,
            taskId: parsed.taskId,
            worker: workerAddress,
            price: bidPrice.toFixed(2),
            estimatedTime: '1h',
            skills: matches,
          };
          await board.send(encodeText(JSON.stringify(bid)));
          log('BID', `bid posted: $${bidPrice.toFixed(2)} for "${parsed.title}"`);
        }

        // Handle tasks (in private groups, not board)
        if (parsed.type === 'task' || parsed.type === MessageType.TASK) {
          log('TASK', `received: "${parsed.title}"`);
          if (parsed.subtasks?.length > 0) {
            const sub = parsed.subtasks[0];
            const claim = createClaim({ taskId: parsed.id, subtaskId: sub.id, worker: workerAddress });
            await board.send(encodeText(serialize(claim)));
            log('CLAIM', `claimed: "${sub.title}"`);

            await new Promise(r => setTimeout(r, 2000));
            const result = createResult({
              taskId: parsed.id, subtaskId: sub.id, worker: workerAddress,
              result: { status: 'completed', deliverable: `completed: ${sub.title}`, completedAt: new Date().toISOString() },
            });
            await board.send(encodeText(serialize(result)));
            log('RESULT', `delivered: "${sub.title}"`);
          }
        }

        // Handle payment confirmations
        if (parsed.type === 'payment' || parsed.type === MessageType.PAYMENT) {
          log('PAID', `received $${parsed.amount} USDC | tx: ${parsed.txHash}`);
        }
      }
    } catch (e) {
      log('ERROR', e.message?.slice(0, 100));
    }
  }

  // Initial poll to catch existing messages
  await poll();

  // Continuous polling
  setInterval(poll, POLL_INTERVAL);

  process.on('SIGINT', async () => {
    log('SHUTDOWN', 'stopping...');
    await agent.stop();
    process.exit(0);
  });
}

main().catch(err => { console.error('Auto-worker failed:', err); process.exit(1); });
