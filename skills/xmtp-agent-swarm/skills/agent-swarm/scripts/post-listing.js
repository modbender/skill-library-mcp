#!/usr/bin/env node
// post-listing.js — Post a real listing to the live bulletin board
// Usage: node scripts/post-listing.js [title] [budget] [skills]

import { createUser, createSigner, Agent, encodeText } from '@xmtp/agent-sdk';
import { MessageType } from '../src/protocol.js';
import fs from 'fs';

process.loadEnvFile('.env');

const BOARD_CONFIG = JSON.parse(fs.readFileSync('board.json', 'utf-8'));

async function main() {
  const title = process.argv[2] || 'build a REST API for the dashboard';
  const budget = process.argv[3] || '3.00';
  const skills = (process.argv[4] || 'backend,api-development').split(',');

  const user = createUser(process.env.WALLET_PRIVATE_KEY);
  console.log(`posting listing as: ${user.account.address}`);

  const agent = await Agent.create(createSigner(user), {
    env: 'production',
    dbPath: null,
  });

  await agent.start();
  await agent.client.conversations.sync();
  const convos = await agent.client.conversations.list();
  const board = convos.find(c => c.id === BOARD_CONFIG.boardId);

  if (!board) {
    // Add the worker to the board first
    console.log('board not in conversation list, looking for it...');
    const allConvos = await agent.client.conversations.list();
    console.log(`found ${allConvos.length} conversations`);
    console.log('board ID:', BOARD_CONFIG.boardId);
    process.exit(1);
  }

  const taskId = `task-${Date.now()}`;
  const listing = {
    type: MessageType.LISTING,
    taskId,
    title,
    description: `${title}. posted to the live bulletin board.`,
    budget,
    skills_needed: skills,
    requestor: user.account.address,
    posted: new Date().toISOString(),
  };

  await board.send(encodeText(JSON.stringify(listing)));
  console.log(`\nlisting posted to board:`);
  console.log(`  task: ${taskId}`);
  console.log(`  title: ${title}`);
  console.log(`  budget: $${budget} USDC`);
  console.log(`  skills: ${skills.join(', ')}`);

  await agent.stop();
  process.exit(0);
}

main().catch(err => { console.error(err); process.exit(1); });
