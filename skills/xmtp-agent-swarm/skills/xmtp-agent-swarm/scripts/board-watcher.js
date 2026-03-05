#!/usr/bin/env node
// board-watcher.js — Cron job that watches the BoardRegistry for join requests,
// auto-approves them, and adds agents to the main XMTP board.
// Run via: node scripts/board-watcher.js [--config swarm.config.json]

import { ethers } from 'ethers';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = join(__dirname, '..');

// Parse args
const args = process.argv.slice(2);
let configPath = join(SKILL_DIR, 'swarm.config.json');
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--config') configPath = join(SKILL_DIR, args[++i]);
}

const config = JSON.parse(readFileSync(configPath, 'utf-8'));
if (config.wallet?.privateKey?.startsWith('env:')) {
  config.wallet.privateKey = process.env[config.wallet.privateKey.slice(4)];
}

const RPC = config.network?.rpc || 'https://mainnet.base.org';
const REGISTRY = '0xf64B21Ce518ab025208662Da001a3F61D3AcB390';

const REGISTRY_ABI = [
  'function getJoinRequestCount(bytes32 boardId) view returns (uint256)',
  'function getJoinRequest(bytes32 boardId, uint256 index) view returns (address agent, string xmtpAddress, string[] skills, uint256 requestedAt, bool approved, bool rejected)',
  'function approveJoin(bytes32 boardId, uint256 requestIndex)',
  'function getBoard(bytes32 boardId) view returns (address owner, string xmtpGroupId, string name, string description, string[] skills, uint256 memberCount, uint256 createdAt, bool active)',
];

const STATE_FILE = join(SKILL_DIR, '.board-watcher-state.json');

function loadState() {
  if (existsSync(STATE_FILE)) return JSON.parse(readFileSync(STATE_FILE, 'utf-8'));
  return { lastProcessedIndex: -1, members: [] };
}

function saveState(state) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

async function run() {
  const registryBoardId = config.registry?.boardId;
  if (!registryBoardId) {
    console.error('No registry.boardId in config. Run: node cli.js registry register');
    process.exit(1);
  }

  const provider = new ethers.JsonRpcProvider(RPC);
  const wallet = new ethers.Wallet(config.wallet.privateKey, provider);
  const registry = new ethers.Contract(REGISTRY, REGISTRY_ABI, wallet);

  console.log(`Board watcher starting...`);
  console.log(`Registry board: ${registryBoardId}`);
  console.log(`Owner: ${wallet.address}`);

  const state = loadState();
  const requestCount = Number(await registry.getJoinRequestCount(registryBoardId));
  console.log(`Total requests: ${requestCount} | Last processed: ${state.lastProcessedIndex}`);

  const newRequests = [];
  for (let i = state.lastProcessedIndex + 1; i < requestCount; i++) {
    const [agent, xmtpAddress, skills, requestedAt, approved, rejected] = 
      await registry.getJoinRequest(registryBoardId, i);
    
    if (!approved && !rejected) {
      console.log(`\n[NEW] Request #${i}: ${agent}`);
      console.log(`  XMTP: ${xmtpAddress}`);
      console.log(`  Skills: ${skills.join(', ')}`);

      // Auto-approve on-chain
      try {
        const tx = await registry.approveJoin(registryBoardId, i);
        await tx.wait();
        console.log(`  Approved on-chain: ${tx.hash}`);
        newRequests.push({ agent, xmtpAddress, skills: [...skills], index: i });
      } catch (err) {
        console.log(`  Failed to approve: ${err.message?.slice(0, 100)}`);
      }
    } else {
      console.log(`  Request #${i}: already ${approved ? 'approved' : 'rejected'}`);
    }
    state.lastProcessedIndex = i;
  }

  // If we have new members, recreate the XMTP board with all members
  if (newRequests.length > 0) {
    console.log(`\n${newRequests.length} new member(s) to add to XMTP board...`);

    const { createSwarmAgent } = await import(join(SKILL_DIR, 'src/agent.js'));
    const dbName = config.xmtp?.dbPath || `.xmtp-${wallet.address.slice(2, 10).toLowerCase()}`;
    const dbPath = join(SKILL_DIR, dbName);

    const { agent } = await createSwarmAgent(config.wallet.privateKey, {
      env: 'production',
      dbPath,
    });
    await agent.start();

    // Add new members to existing board via inbox IDs
    const { getInboxIdForIdentifier } = await import('@xmtp/node-sdk');
    const board = await (async () => {
      const client = agent.client || agent;
      await client.conversations.syncAll();
      const convos = await client.conversations.list();
      return convos.find(c => c.id === config.board?.id);
    })();

    if (!board) {
      console.error('Board not found. Creating new one...');
      const allMembers = [...new Set([...state.members, ...newRequests.map(r => r.xmtpAddress)])];
      const newBoard = await agent.createGroupWithAddresses(allMembers, {
        name: 'Agent Swarm — Main Board',
        description: 'The main agent marketplace board. Post tasks, find work, get paid in USDC.',
      });
      config.board = config.board || {};
      config.board.id = newBoard.id;
      writeFileSync(configPath, JSON.stringify(config, null, 2));
      console.log(`New board created: ${newBoard.id}`);
      state.members = allMembers;
    } else {
      for (const req of newRequests) {
        try {
          const inboxId = await getInboxIdForIdentifier({ identifier: req.xmtpAddress, identifierKind: 0 }, 'production');
          if (!inboxId) { console.log(`  Could not resolve ${req.xmtpAddress}`); continue; }
          await board.addMembers([inboxId]);
          console.log(`  Added ${req.xmtpAddress} (inbox: ${inboxId.slice(0,12)}...)`);
          state.members.push(req.xmtpAddress);
        } catch (err) {
          console.log(`  Failed to add ${req.xmtpAddress}: ${err.message?.slice(0,80)}`);
        }
      }
      console.log(`Board ${config.board.id} updated — no ID change.`);
    }

    await agent.stop();
  } else {
    console.log('\nNo new requests.');
  }

  saveState(state);
  console.log('\nDone.');
}

run().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
