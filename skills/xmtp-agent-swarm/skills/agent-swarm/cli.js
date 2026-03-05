#!/usr/bin/env node
// cli.js — Agent Swarm CLI: board, listing, worker, escrow, task commands
// Usage: node cli.js <command> <subcommand> [--flags]

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONFIG_PATH_DEFAULT = join(__dirname, 'swarm.config.json');
let CONFIG_PATH = CONFIG_PATH_DEFAULT;
const TASK_LOG_PATH = join(__dirname, 'tasks.json');

// ─── Dashboard State ───
import * as dashState from './src/state.js';

// ─── Sounds ───
import { playSound, playSoundSync, setSoundsEnabled } from './src/sounds.js';

// ─── Guard Check (gates all on-chain transactions) ───

async function checkGuard(config, { to, usdcAmount, action }) {
  const workdir = dirname(CONFIG_PATH);
  const guardPath = join(workdir, '.wallet-guard.json');
  if (!existsSync(guardPath)) return; // no guard = no check
  const { guardWallet } = await import('./src/wallet-guard.js');
  const { appendFileSync: appendLog } = await import('fs');
  const wallet = await getWalletLazy(config);
  const guarded = guardWallet(wallet, { workdir });
  const result = guarded.checkGuardrails({ to, usdcAmount, action });

  // Audit log every check
  const logLine = JSON.stringify({
    timestamp: new Date().toISOString(),
    action, to, usdcAmount,
    allowed: result.allowed,
    reason: result.reason,
  }) + '\n';
  try { appendLog(join(workdir, '.wallet-audit.log'), logLine); } catch {}

  if (!result.allowed) {
    playSound('blocked');
    console.error(`🛡️  BLOCKED by wallet guard: ${result.reason}`);
    process.exit(1);
  }
  // No sound on approval — the command itself plays its contextual sound
}

// Lazy wallet loader (avoids circular with getWallet which may not be defined yet)
let _walletCache = null;
async function getWalletLazy(config) {
  if (_walletCache) return _walletCache;
  const { loadWallet } = await import('./src/wallet.js');
  _walletCache = loadWallet(config.wallet.privateKey);
  return _walletCache;
}

// ─── Config ───

function loadConfig() {
  if (!existsSync(CONFIG_PATH)) {
    console.error('No swarm.config.json found. Create one first (see SKILL.md).');
    process.exit(1);
  }
  const config = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
  // Resolve env: references
  if (config.wallet?.privateKey?.startsWith('env:')) {
    const envVar = config.wallet.privateKey.slice(4);
    config.wallet.privateKey = process.env[envVar];
    if (!config.wallet.privateKey) {
      console.error(`Environment variable ${envVar} not set.`);
      process.exit(1);
    }
  }
  return config;
}

function loadTaskLog() {
  if (!existsSync(TASK_LOG_PATH)) return { tasks: {}, bids: {} };
  return JSON.parse(readFileSync(TASK_LOG_PATH, 'utf-8'));
}

function saveTaskLog(log) {
  writeFileSync(TASK_LOG_PATH, JSON.stringify(log, null, 2));
}

// ─── Parse Args ───

function parseArgs(args) {
  const flags = {};
  const positional = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith('--')) {
        flags[key] = next;
        i++;
      } else {
        flags[key] = true;
      }
    } else {
      positional.push(args[i]);
    }
  }
  return { flags, positional };
}

// ─── Lazy Imports (heavy deps loaded only when needed) ───

async function getAgent(config) {
  const { createSwarmAgent } = await import('./src/agent.js');
  // Deterministic db path per wallet so we reuse the same XMTP installation
  const { ethers } = await import('ethers');
  const wallet = new ethers.Wallet(config.wallet.privateKey);
  const dbName = config.xmtp?.dbPath || `.xmtp-${wallet.address.slice(2, 10).toLowerCase()}`;
  const dbPath = join(__dirname, dbName);
  const { agent, address } = await createSwarmAgent(config.wallet.privateKey, {
    env: config.xmtp?.env || 'production',
    dbPath,
  });
  await agent.start();

  // Persist the db path in config so it's always reused
  if (!config.xmtp?.dbPath) {
    config.xmtp = config.xmtp || {};
    config.xmtp.dbPath = dbName;
    try { writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2)); } catch {}
  }

  return { agent, address };
}

async function getBoard(agent, config) {
  if (!config.board?.id) return null;
  const boardId = config.board.id;
  const client = agent.client || agent;
  let board = null;
  for (let attempt = 0; attempt < 3; attempt++) {
    await client.conversations.syncAll();
    const conversations = await client.conversations.list();
    board = conversations.find(c => c.id === boardId);
    if (board) return board;
    if (attempt < 2) await new Promise(r => setTimeout(r, 2000));
  }
  throw new Error(`Board ${boardId} not found. Run: node cli.js setup check`);
}

async function getWallet(config) {
  const { loadWallet } = await import('./src/wallet.js');
  return loadWallet(config.wallet.privateKey);
}

// ─── Commands ───

const commands = {
  // ─── Setup ───
  setup: {
    async init(config_unused, flags) {
      const { ethers } = await import('ethers');

      // Generate or use existing wallet
      let privateKey = flags.key || null;
      let wallet;
      if (privateKey) {
        wallet = new ethers.Wallet(privateKey);
        console.log(`Using existing wallet: ${wallet.address}`);
      } else {
        wallet = ethers.Wallet.createRandom();
        privateKey = wallet.privateKey;
        console.log(`Generated new wallet: ${wallet.address}`);
        console.log(`Private key: ${privateKey}`);
        console.log(`\n⚠️  Save this key! You need it to recover your agent.\n`);
      }

      // Build config
      const skills = (flags.skills || 'coding,research,code-review,writing').split(',').map(s => s.trim());
      const config = {
        wallet: { privateKey },
        board: { id: flags['board-id'] || null, name: 'Agent Swarm Board' },
        worker: {
          skills,
          rates: Object.fromEntries(skills.map(s => [s, '2.00'])),
          maxBid: '20.00',
          minBid: '0.50',
          autoAccept: flags['auto-accept'] !== 'false',  // default true
        },
        escrow: {
          address: '0xE2b1D96dfbd4E363888c4c4f314A473E7cA24D2f',
          defaultDeadlineHours: 24,
        },
        milestoneEscrow: {
          address: '0x7334DfF91ddE131e587d22Cb85F4184833340F6f',
        },
        staking: {
          address: '0x91618100EE71652Bb0A153c5C9Cc2aaE2B63E488',
        },
        verification: {
          registry: '0x22536E4C3A221dA3C42F02469DB3183E28fF7A74',
        },
        swarmEscrow: {
          address: '0xCd8e54f26a81843Ed0fC53c283f34b53444cdb59',
        },
        xmtp: { env: 'production' },
        network: {
          chainId: 8453,
          rpc: 'https://mainnet.base.org',
          usdc: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
        },
      };

      writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
      console.log(`Config written to ${CONFIG_PATH}`);

      // Register on XMTP (reuse existing db if available)
      const { createSwarmAgent } = await import('./src/agent.js');
      const dbName = `.xmtp-${wallet.address.slice(2, 10).toLowerCase()}`;
      const dbPath = join(__dirname, dbName);
      config.xmtp.dbPath = dbName;
      writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));

      let agent, address;
      if (existsSync(dbPath)) {
        console.log(`\nReusing existing XMTP registration: ${dbName}`);
        try {
          ({ agent, address } = await createSwarmAgent(privateKey, {
            env: 'production',
            dbPath,
          }));
          await agent.start();
          console.log(`XMTP agent: ${address}`);
        } catch (err) {
          if (err.message?.includes('installation')) {
            console.error('\nXMTP installation limit reached.');
            console.error('Your existing database may be invalid. To fix:');
            console.error(`  1. Delete ${dbName} and revoke old installations via XMTP`);
            console.error('  2. Or use a new wallet: node cli.js setup init');
            process.exit(1);
          }
          throw err;
        }
      } else {
        console.log('\nRegistering on XMTP (first time)...');
        try {
          ({ agent, address } = await createSwarmAgent(privateKey, {
            env: 'production',
            dbPath,
          }));
          await agent.start();
          console.log(`XMTP agent: ${address}`);
          console.log('⚠️  Your XMTP database is at: ' + dbName);
          console.log('   Do NOT delete this file — it counts toward your installation limit.');
        } catch (err) {
          if (err.message?.includes('installation')) {
            console.error('\nXMTP installation limit reached for this wallet.');
            console.error('This wallet has registered too many XMTP installations.');
            console.error('Options:');
            console.error('  1. Use a different wallet');
            console.error('  2. Revoke old installations (requires access to an existing db)');
            process.exit(1);
          }
          throw err;
        }
      }

      // Create or join board
      if (flags['board-id']) {
        console.log(`\nJoining board: ${flags['board-id']}`);
        const client = agent.client || agent;
        let board = null;
        // Retry sync a few times (XMTP welcome messages may take a moment)
        for (let attempt = 0; attempt < 5; attempt++) {
          await client.conversations.syncAll();
          const convos = await client.conversations.list();
          board = convos.find(c => c.id === flags['board-id']);
          if (board) break;
          if (attempt < 4) {
            console.log(`  Syncing... (attempt ${attempt + 1}/5)`);
            await new Promise(r => setTimeout(r, 3000));
          }
        }
        if (board) {
          console.log('Board found.');
        } else {
          console.log('Board not found. Ask the board admin to add your address: ' + address);
        }
      } else if (!flags['no-board']) {
        console.log('\nCreating new board...');
        const memberAddrs = flags.members ? flags.members.split(',').map(s => s.trim()) : [];
        const board = await agent.createGroupWithAddresses(memberAddrs, {
          name: 'Agent Swarm Board',
          description: 'Public task board for agent discovery',
        });
        config.board.id = board.id;
        writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
        console.log(`Board created: ${board.id}`);
        if (memberAddrs.length) console.log(`Members: ${memberAddrs.join(', ')}`);
      }

      // Check wallet balance
      const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');
      const ethBal = await provider.getBalance(wallet.address);
      const usdc = new ethers.Contract('0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
        ['function balanceOf(address) view returns (uint256)'], provider);
      const usdcBal = await usdc.balanceOf(wallet.address);

      console.log(`\nWallet balance:`);
      console.log(`  ETH:  ${ethers.formatEther(ethBal)}`);
      console.log(`  USDC: ${ethers.formatUnits(usdcBal, 6)}`);

      if (ethBal === 0n) {
        console.log(`\n⚠️  No ETH for gas. Send Base ETH to: ${wallet.address}`);
      }
      if (usdcBal === 0n) {
        console.log(`⚠️  No USDC. Send USDC on Base to: ${wallet.address}`);
        console.log(`   (Only needed if you want to post tasks with escrow)`);
      }

      playSound('ready');
      console.log('\n✅ Setup complete. Next steps:');
      if (config.board.id) {
        console.log('  Post a listing: node cli.js listing post --title "..." --budget 1.00');
        console.log('  Start working:  node cli.js worker start');
      } else {
        console.log('  Create a board:  node cli.js board create');
        console.log('  Or join one:     node cli.js board connect --id <boardId>');
      }

      await agent.stop();
    },

    async check(config, flags) {
      const { ethers } = await import('ethers');
      const wallet = new ethers.Wallet(config.wallet.privateKey);
      const provider = new ethers.JsonRpcProvider(config.network?.rpc || 'https://mainnet.base.org');

      const ethBal = await provider.getBalance(wallet.address);
      const usdc = new ethers.Contract(config.network?.usdc || '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
        ['function balanceOf(address) view returns (uint256)'], provider);
      const usdcBal = await usdc.balanceOf(wallet.address);

      console.log(`Agent:  ${wallet.address}`);
      console.log(`ETH:    ${ethers.formatEther(ethBal)}`);
      console.log(`USDC:   ${ethers.formatUnits(usdcBal, 6)}`);
      console.log(`Board:  ${config.board?.id || 'none'}`);
      console.log(`Skills: ${(config.worker?.skills || []).join(', ')}`);
      console.log(`XMTP:   ${config.xmtp?.env || 'production'}`);
      console.log(`Escrow: ${config.escrow?.address || 'not set'}`);

      if (ethBal === 0n) console.log(`\n⚠️  No ETH for gas. Send to: ${wallet.address}`);
      if (usdcBal === 0n) console.log(`⚠️  No USDC for escrow.`);
    },
  },

  // ─── Board Commands ───
  board: {
    async create(config, flags) {
      const { agent, address } = await getAgent(config);
      console.log(`Agent: ${address}`);

      // Accept --members as comma-separated addresses
      const memberAddrs = flags.members ? flags.members.split(',').map(s => s.trim()) : [];

      const board = await agent.createGroupWithAddresses(memberAddrs, {
        name: flags.name || 'Agent Swarm Board',
        description: 'Public task board for agent discovery. Post listings, find work.',
      });
      const boardId = board.id;
      console.log(`Board created: ${boardId}`);
      if (memberAddrs.length) console.log(`Members added: ${memberAddrs.join(', ')}`);

      // Save to config
      config.board = config.board || {};
      config.board.id = boardId;
      writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
      console.log('Board ID saved to config');

      await agent.stop();
    },

    async connect(config, flags) {
      if (!config.board?.id && !flags.id) {
        console.error('No board ID. Use --id <boardId> or run: node cli.js board create');
        process.exit(1);
      }
      const boardId = flags.id || config.board.id;
      const { agent, address } = await getAgent(config);
      console.log(`Agent: ${address}`);

      const board = await getBoard(agent, { ...config, board: { id: boardId } });
      if (!board) {
        console.error('Board not found. Agent may need to be added to the group.');
        process.exit(1);
      }
      console.log(`Connected to board: ${boardId}`);

      // Save if new
      if (flags.id) {
        config.board = config.board || {};
        config.board.id = boardId;
        writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
      }

      await agent.stop();
    },

    async listings(config, flags) {
      const { agent } = await getAgent(config);
      const board = await getBoard(agent, config);
      if (!board) { console.error('No board configured.'); process.exit(1); }

      await board.sync();
      const msgs = await board.messages({ limit: 50 });
      const listings = new Map();

      for (const m of msgs) {
        try {
          const parsed = JSON.parse(typeof m.content === 'string' ? m.content : JSON.stringify(m.content));
          if (parsed.type === 'listing') {
            listings.set(parsed.taskId, parsed);
          }
        } catch {}
      }

      if (listings.size === 0) {
        console.log('No active listings on the board.');
      } else {
        console.log(`\n${listings.size} listing(s):\n`);
        for (const [id, l] of listings) {
          console.log(`  [${id}] ${l.title}`);
          console.log(`    Budget: $${l.budget} USDC | Skills: ${(l.skills_needed || []).join(', ') || 'any'}`);
          console.log(`    Requestor: ${l.requestor}`);
          console.log('');
        }
      }
      await agent.stop();
    },

    async workers(config, flags) {
      const { agent } = await getAgent(config);
      const board = await getBoard(agent, config);
      if (!board) { console.error('No board configured.'); process.exit(1); }

      const { findWorkers } = await import('./src/profile.js');
      const skill = flags.skill || null;

      await board.sync();
      const msgs = await board.messages({ limit: 100 });
      const profiles = new Map();

      for (const m of msgs) {
        try {
          const parsed = JSON.parse(typeof m.content === 'string' ? m.content : JSON.stringify(m.content));
          if (parsed.type === 'profile') {
            profiles.set(parsed.agent, parsed);
          }
        } catch {}
      }

      let results = [...profiles.values()];
      if (skill) {
        results = results.filter(p => p.skills?.some(s => s.toLowerCase() === skill.toLowerCase()));
      }

      if (results.length === 0) {
        console.log(skill ? `No workers with skill "${skill}".` : 'No workers on the board.');
      } else {
        console.log(`\n${results.length} worker(s):\n`);
        for (const p of results) {
          console.log(`  ${p.agent}`);
          console.log(`    Skills: ${(p.skills || []).join(', ')}`);
          console.log(`    Rates: ${JSON.stringify(p.rates || {})}`);
          console.log('');
        }
      }
      await agent.stop();
    },

    async profile(config, flags) {
      const { agent, address } = await getAgent(config);
      const board = await getBoard(agent, config);
      if (!board) { console.error('No board configured.'); process.exit(1); }

      const { createProfile, broadcastProfile } = await import('./src/profile.js');
      const profile = createProfile(address, {
        skills: config.worker?.skills || [],
        rates: config.worker?.rates || {},
        description: flags.description || 'OpenClaw agent ready for work.',
      });
      await broadcastProfile(board, profile);
      console.log(`Profile posted for ${address}`);
      console.log(`  Skills: ${profile.skills.join(', ')}`);
      await agent.stop();
    },

    async 'find-workers'(config, flags) {
      return this.workers(config, flags);
    },
  },

  // ─── Registry Commands (on-chain board discovery) ───
  registry: {
    async list(config, flags) {
      const { listAllBoards } = await import('./src/registry.js');
      const limit = parseInt(flags.limit || '20');
      const { boards, total } = await listAllBoards(limit);
      console.log(`${boards.length} active board(s) (${total} total):\n`);
      for (const b of boards) {
        console.log(`  ${b.id}`);
        console.log(`    Name: ${b.name}`);
        console.log(`    Skills: ${b.skills.join(', ')}`);
        console.log(`    Members: ${b.memberCount}`);
        console.log(`    Owner: ${b.owner}`);
        console.log(`    XMTP Group: ${b.xmtpGroupId}`);
        console.log('');
      }
    },

    async register(config, flags) {
      if (!config.board?.id) {
        console.error('No board in config. Run: node cli.js board create');
        process.exit(1);
      }
      const wallet = await getWallet(config);
      const { registerBoard } = await import('./src/registry.js');
      const name = flags.name || config.board?.name || 'Agent Swarm Board';
      const description = flags.description || 'Open task board for agent work';
      const skills = (flags.skills || config.worker?.skills || []).join ? 
        (flags.skills ? flags.skills.split(',') : config.worker?.skills || []) :
        config.worker?.skills || [];

      console.log(`Registering board on-chain...`);
      const { txHash, boardId } = await registerBoard(wallet, config.board.id, name, description, skills);
      console.log(`Registered: ${boardId}`);
      console.log(`Tx: ${txHash}`);

      config.registry = config.registry || {};
      config.registry.boardId = boardId;
      writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
      console.log('Registry board ID saved to config.');
    },

    async join(config, flags) {
      const boardId = flags['board-id'] || flags.id;
      if (!boardId) {
        console.error('Usage: node cli.js registry join --board-id <registryBoardId>');
        process.exit(1);
      }
      const wallet = await getWallet(config);
      const { requestJoinBoard, getReadonlyRegistry } = await import('./src/registry.js');

      // Get board info
      const registry = getReadonlyRegistry();
      const [owner, xmtpGroupId, name, , skills, memberCount] = await registry.getBoard(boardId);
      console.log(`Board: ${name}`);
      console.log(`Skills: ${skills.join(', ')}`);
      console.log(`Members: ${Number(memberCount)}`);
      console.log(`XMTP Group: ${xmtpGroupId}\n`);

      const mySkills = config.worker?.skills || [];
      console.log(`Requesting to join with skills: ${mySkills.join(', ')}...`);
      const { txHash } = await requestJoinBoard(wallet, boardId, wallet.address, mySkills);
      console.log(`Join request submitted: ${txHash}`);
      console.log('Board owner will review and add you to the XMTP group.');
    },

    async requests(config, flags) {
      const boardId = config.registry?.boardId || flags['board-id'];
      if (!boardId) {
        console.error('No registry board ID. Run: node cli.js registry register');
        process.exit(1);
      }
      const { getPendingRequests } = await import('./src/registry.js');
      const requests = await getPendingRequests(boardId);
      if (!requests.length) {
        console.log('No pending join requests.');
        return;
      }
      console.log(`${requests.length} pending request(s):\n`);
      for (const r of requests) {
        console.log(`  [${r.index}] ${r.agent}`);
        console.log(`       XMTP: ${r.xmtpAddress}`);
        console.log(`       Skills: ${r.skills.join(', ')}`);
        console.log(`       Requested: ${new Date(r.requestedAt * 1000).toISOString()}`);
        console.log('');
      }
    },

    async approve(config, flags) {
      const boardId = config.registry?.boardId || flags['board-id'];
      const index = parseInt(flags.index ?? flags.i);
      if (!boardId || isNaN(index)) {
        console.error('Usage: node cli.js registry approve --index <i> [--board-id <id>]');
        process.exit(1);
      }

      // Approve on-chain
      const wallet = await getWallet(config);
      const { approveJoinRequest, getReadonlyRegistry } = await import('./src/registry.js');
      const registry = getReadonlyRegistry();
      const [agent, xmtpAddress] = await registry.getJoinRequest(boardId, index);

      console.log(`Approving ${agent}...`);
      const { txHash } = await approveJoinRequest(wallet, boardId, index);
      console.log(`Approved on-chain: ${txHash}`);

      // Add to XMTP group — XMTP's addMembers has a hex bug,
      // so we recreate the board with all current + new members
      // Add to XMTP group using inbox ID (addMembers with addresses has a hex bug)
      if (config.board?.id) {
        console.log(`Adding ${xmtpAddress} to XMTP board...`);
        try {
          const { agent: xmtpAgent } = await getAgent(config);
          const board = await getBoard(xmtpAgent, config);

          // Resolve address → inbox ID
          const { getInboxIdForIdentifier } = await import('@xmtp/node-sdk');
          const inboxId = await getInboxIdForIdentifier({ identifier: xmtpAddress, identifierKind: 0 }, 'production');
          if (!inboxId) {
            throw new Error(`Could not resolve inbox ID for ${xmtpAddress}. Agent may not be registered on XMTP.`);
          }
          console.log(`Resolved inbox ID: ${inboxId}`);

          // addMembers takes inbox IDs (not addresses)
          await board.addMembers([inboxId]);
          console.log(`Added ${xmtpAddress} to board ${config.board.id}`);
          console.log('Board ID unchanged — no reconnection needed.');

          await xmtpAgent.stop();
        } catch (err) {
          console.log(`Could not add to XMTP group: ${err.message}`);
          console.log(`Fallback: create a new board with: node cli.js board create --members ${xmtpAddress}`);
        }
      }
    },
  },

  // ─── Listing Commands ───
  listing: {
    async post(config, flags) {
      if (!flags.title) { console.error('--title required'); process.exit(1); }
      if (!flags.budget) { console.error('--budget required'); process.exit(1); }

      const { agent, address } = await getAgent(config);
      const board = await getBoard(agent, config);
      if (!board) { console.error('No board configured.'); process.exit(1); }

      const { postListing } = await import('./src/board.js');
      const taskId = `task-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      const skills = flags.skills ? flags.skills.split(',').map(s => s.trim()) : [];

      const listing = await postListing(board, {
        taskId,
        title: flags.title,
        description: flags.description || '',
        budget: flags.budget,
        skills_needed: skills,
        requestor: address,
        category: flags.category || 'custom',
      });

      console.log(`Listing posted: ${taskId}`);
      console.log(`  Title: ${flags.title}`);
      console.log(`  Budget: $${flags.budget} USDC`);

      // Log to dashboard
      dashState.registerAgent(address, 'requestor');
      dashState.logListing({ taskId, title: flags.title, description: flags.description || '', budget: flags.budget, skills_needed: skills, requestor: address });

      // Save to task log
      const log = loadTaskLog();
      log.tasks[taskId] = {
        id: taskId,
        title: flags.title,
        description: flags.description || '',
        budget: flags.budget,
        skills: skills,
        category: flags.category || 'custom',
        requestor: address,
        status: 'open',
        createdAt: new Date().toISOString(),
      };
      saveTaskLog(log);

      await agent.stop();
    },

    async bids(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }

      const { agent } = await getAgent(config);
      const board = await getBoard(agent, config);
      if (!board) { console.error('No board configured.'); process.exit(1); }

      await board.sync();
      const msgs = await board.messages({ limit: 100 });
      const bids = [];

      for (const m of msgs) {
        try {
          const parsed = JSON.parse(typeof m.content === 'string' ? m.content : JSON.stringify(m.content));
          if (parsed.type === 'bid' && parsed.taskId === flags['task-id']) {
            bids.push(parsed);
          }
        } catch {}
      }

      if (bids.length === 0) {
        console.log(`No bids yet for ${flags['task-id']}.`);
      } else {
        console.log(`\n${bids.length} bid(s):\n`);
        for (const b of bids) {
          console.log(`  Worker: ${b.worker}`);
          console.log(`  Price: $${b.price} USDC | ETA: ${b.estimatedTime || 'unspecified'}`);
          console.log('');
        }
      }
      await agent.stop();
    },

    async accept(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      if (!flags.worker) { console.error('--worker required'); process.exit(1); }

      const taskId = flags['task-id'];
      const workerAddr = flags.worker;
      const log = loadTaskLog();
      const task = log.tasks[taskId];
      if (!task) { console.error(`Task ${taskId} not found in local log.`); process.exit(1); }

      const amount = flags.amount || task.budget;
      const deadlineHours = parseInt(flags.deadline || config.escrow?.defaultDeadlineHours || 24);

      const { agent, address } = await getAgent(config);

      // 1. Check wallet balance
      const wallet = await getWallet(config);
      const { ethers } = await import('ethers');
      const provider = wallet.provider;
      const ethBal = await provider.getBalance(wallet.address);
      const usdcContract = new ethers.Contract(config.network?.usdc || '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
        ['function balanceOf(address) view returns (uint256)'], provider);
      const usdcBal = await usdcContract.balanceOf(wallet.address);
      const amountRaw = ethers.parseUnits(amount, 6);

      if (ethBal === 0n) {
        console.error(`No ETH for gas. Send Base ETH to: ${wallet.address}`);
        process.exit(1);
      }
      if (usdcBal < amountRaw) {
        console.error(`Insufficient USDC. Have $${ethers.formatUnits(usdcBal, 6)}, need $${amount}. Send USDC to: ${wallet.address}`);
        process.exit(1);
      }

      // 2. Create escrow on-chain
      console.log(`Creating escrow: $${amount} USDC for ${workerAddr}...`);
      const { createEscrow, hashTaskId } = await import('./src/escrow.js');
      const escrowAddr = config.escrow?.address || '0xE2b1D96dfbd4E363888c4c4f314A473E7cA24D2f';
      const deadline = Math.floor(Date.now() / 1000) + (deadlineHours * 3600);

      const { txHash, taskIdHash } = await createEscrow(wallet, escrowAddr, {
        taskId,
        worker: workerAddr,
        amount,
        deadline,
      });
      console.log(`Escrow created: ${txHash}`); playSound('escrow-sealed');

      // 2. Create private XMTP group with worker
      const { createSwarmGroup, sendProtocolMessage } = await import('./src/agent.js');
      const group = await createSwarmGroup(agent, [workerAddr], `Task: ${task.title}`);
      console.log(`Private group created: ${group.id}`);

      // 3. Send bid_accept to board
      const board = await getBoard(agent, config);
      if (board) {
        await sendProtocolMessage(board, {
          type: 'bid_accept',
          taskId,
          worker: workerAddr,
          amount,
        });
      }

      // 4. Send task + escrow_created to private group
      await sendProtocolMessage(group, {
        type: 'task',
        id: taskId,
        title: task.title,
        description: task.description,
        budget: amount,
        category: task.category || 'custom',
        subtasks: [{ id: `${taskId}-s1`, title: task.title, description: task.description }],
      });

      await sendProtocolMessage(group, {
        type: 'escrow_created',
        taskId,
        escrowContract: escrowAddr,
        txHash,
        amount,
        deadline,
        taskIdHash,
      });

      // 5. Update dashboard + local log
      dashState.registerAgent(address, 'requestor');
      dashState.registerAgent(workerAddr, 'worker');
      dashState.logEscrow({ taskId, requestor: address, worker: workerAddr, amount, deadline, txHash });
      dashState.logTask({ id: taskId, title: task.title, budget: amount, subtasks: [{ id: `${taskId}-s1` }] }, address);

      // Set acceptance criteria on-chain if provided
      if (flags.criteria || task.criteria) {
        try {
          const { setCriteria } = await import('./src/verification.js');
          const registryAddr = config.verification?.registry || '0x2120D4e0074e0a41762dF785f2c99086aB8bc51b';
          const criteriaContent = flags.criteria || task.criteria;
          const { txHash: critTx, criteriaHash } = await setCriteria(wallet, registryAddr, taskId, criteriaContent);
          console.log(`Acceptance criteria on-chain: ${criteriaHash.slice(0, 18)}...`);
          playSound('criteria-set');
        } catch (err) {
          console.log(`Criteria recording skipped: ${err.message?.slice(0, 60)}`);
        }
      }

      task.status = 'in-progress';
      task.worker = workerAddr;
      task.groupId = group.id;
      task.escrowTx = txHash;
      task.deadline = deadline;
      saveTaskLog(log);

      console.log(`\nTask assigned to ${workerAddr}`);
      console.log(`Escrow: $${amount} USDC locked until ${new Date(deadline * 1000).toISOString()}`);
      console.log(`Monitor: node cli.js task monitor --task-id ${taskId}`);

      await agent.stop();
    },
  },

  // ─── Task Commands ───
  task: {
    async monitor(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }

      const taskId = flags['task-id'];
      const log = loadTaskLog();
      const task = log.tasks[taskId];
      if (!task?.groupId) { console.error('Task has no group. Was it accepted?'); process.exit(1); }

      const { agent } = await getAgent(config);

      await agent.client.conversations.sync();
      const convos = await agent.client.conversations.list();
      const group = convos.find(c => c.id === task.groupId);
      if (!group) { console.error('Group not found.'); process.exit(1); }

      console.log(`Monitoring task ${taskId}: "${task.title}"`);
      console.log(`Worker: ${task.worker}`);
      console.log(`Polling for results...\n`);

      const seen = new Set();
      const poll = async () => {
        await group.sync();
        const msgs = await group.messages({ limit: 30 });
        for (const m of msgs) {
          if (seen.has(m.id)) continue;
          seen.add(m.id);
          try {
            const parsed = JSON.parse(typeof m.content === 'string' ? m.content : JSON.stringify(m.content));
            if (parsed.type === 'progress') {
              console.log(`[PROGRESS] ${parsed.percent || '?'}% — ${parsed.message || ''}`);
            }
            if (parsed.type === 'result') {
              console.log(`[RESULT] Task completed.`);
              console.log(JSON.stringify(parsed.result, null, 2));
              task.status = 'completed';
              task.result = parsed.result;
              saveTaskLog(log);
              return true;
            }
            if (parsed.type === 'cancel') {
              console.log(`[CANCELLED] by ${parsed.cancelledBy}: ${parsed.reason || 'no reason'}`);
              task.status = 'cancelled';
              saveTaskLog(log);
              return true;
            }
          } catch {}
        }
        return false;
      };

      // Poll for up to 30 minutes
      const maxPolls = 360;
      for (let i = 0; i < maxPolls; i++) {
        const done = await poll();
        if (done) break;
        if (i % 12 === 0 && i > 0) console.log(`  still waiting... (${i * 5}s)`);
        await new Promise(r => setTimeout(r, 5000));
      }

      await agent.stop();
    },

    async list(config, flags) {
      const log = loadTaskLog();
      const tasks = Object.values(log.tasks);
      if (tasks.length === 0) {
        console.log('No tasks.');
        return;
      }
      console.log(`\n${tasks.length} task(s):\n`);
      for (const t of tasks) {
        console.log(`  [${t.id}] ${t.title}`);
        console.log(`    Status: ${t.status} | Budget: $${t.budget} | Worker: ${t.worker || 'none'}`);
        console.log('');
      }
    },
  },

  // ─── Escrow Commands ───
  escrow: {
    async status(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      const { getEscrowStatus } = await import('./src/escrow.js');
      const wallet = await getWallet(config);
      const escrowAddr = config.escrow?.address || '0xE2b1D96dfbd4E363888c4c4f314A473E7cA24D2f';
      const status = await getEscrowStatus(wallet, escrowAddr, flags['task-id']);
      console.log(`Escrow for ${flags['task-id']}:`);
      console.log(`  Requestor: ${status.requestor}`);
      console.log(`  Worker: ${status.worker}`);
      console.log(`  Amount: $${status.amount} USDC`);
      console.log(`  Deadline: ${new Date(status.deadline * 1000).toISOString()}`);
      console.log(`  Status: ${status.status}`);
    },

    async release(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      const { releaseEscrow } = await import('./src/escrow.js');
      const wallet = await getWallet(config);
      const escrowAddr = config.escrow?.address || '0xE2b1D96dfbd4E363888c4c4f314A473E7cA24D2f';
      console.log('Releasing escrow...');
      const { txHash } = await releaseEscrow(wallet, escrowAddr, flags['task-id']);
      console.log(`Released: ${txHash}`); playSound('payment-released');

      // Update dashboard + local log
      dashState.updateEscrow(flags['task-id'], 'released', txHash);
      const log = loadTaskLog();
      const task = log.tasks[flags['task-id']];
      if (task) {
        dashState.logPayment(flags['task-id'], task.worker, task.budget, txHash);
        task.status = 'paid';
        task.releaseTx = txHash;
        saveTaskLog(log);
      }
    },

    async dispute(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      const { disputeEscrow } = await import('./src/escrow.js');
      const wallet = await getWallet(config);
      const escrowAddr = config.escrow?.address || '0xE2b1D96dfbd4E363888c4c4f314A473E7cA24D2f';
      console.log('Filing dispute...');
      const { txHash } = await disputeEscrow(wallet, escrowAddr, flags['task-id']);
      console.log(`Disputed: ${txHash}`);
    },

    async refund(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      const { default: escrowMod } = await import('./src/escrow.js');
      const wallet = await getWallet(config);
      const escrowAddr = config.escrow?.address || '0xE2b1D96dfbd4E363888c4c4f314A473E7cA24D2f';
      const { ethers } = await import('ethers');
      // Direct contract call for refund
      const abi = ['function refund(bytes32 taskId) external'];
      const contract = new ethers.Contract(escrowAddr, abi, wallet);
      const { hashTaskId } = await import('./src/escrow.js');
      console.log('Requesting refund...');
      const tx = await contract.refund(hashTaskId(flags['task-id']));
      await tx.wait();
      console.log(`Refunded: ${tx.hash}`);
    },

    async verify(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      const { getVerificationTrail, getWorkerStats } = await import('./src/verification.js');
      const wallet = await getWallet(config);
      const registryAddr = config.verification?.registry || '0x2120D4e0074e0a41762dF785f2c99086aB8bc51b';

      const trail = await getVerificationTrail(wallet, registryAddr, flags['task-id']);
      console.log(`Verification trail for ${flags['task-id']}:`);
      console.log(`  Deliverable hash: ${trail.deliverableHash === '0x' + '0'.repeat(64) ? 'not submitted' : trail.deliverableHash.slice(0, 18) + '...'}`);
      console.log(`  Criteria hash:    ${trail.criteriaHash === '0x' + '0'.repeat(64) ? 'none set' : trail.criteriaHash.slice(0, 18) + '...'}`);
      console.log(`  Verified:         ${trail.verified ? (trail.passed ? 'PASSED' : 'FAILED') : 'not yet'}`);
      if (trail.verified) {
        console.log(`  Verification:     ${trail.verificationHash.slice(0, 18)}...`);
        console.log(`  Verifier:         ${trail.verifier}`);
        console.log(`  Verified at:      ${new Date(trail.verifiedAt * 1000).toISOString()}`);
      }
      if (trail.worker !== '0x0000000000000000000000000000000000000000') {
        const stats = await getWorkerStats(wallet, registryAddr, trail.worker);
        console.log(`\nWorker stats (${trail.worker.slice(0, 10)}...):`);
        console.log(`  Submissions: ${stats.submissions}`);
        console.log(`  Verified:    ${stats.verified}`);
        console.log(`  Pass rate:   ${stats.passRate}`);
      }
    },

    async 'claim-timeout'(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      const { claimDisputeTimeout } = await import('./src/escrow.js');
      const wallet = await getWallet(config);
      const escrowAddr = config.escrow?.address || '0xE2b1D96dfbd4E363888c4c4f314A473E7cA24D2f';
      console.log('Claiming dispute timeout refund...');
      const { txHash } = await claimDisputeTimeout(wallet, escrowAddr, flags['task-id']);
      console.log(`Refunded: ${txHash}`);
    },

    // ─── Milestone Escrow Commands ───

    async 'create-milestone'(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      if (!flags.worker) { console.error('--worker required'); process.exit(1); }
      if (!flags.milestones) { console.error('--milestones required (e.g. "1.00:24h,2.00:48h")'); process.exit(1); }

      const milestones = flags.milestones.split(',').map(m => {
        const [amount, deadline] = m.trim().split(':');
        const hours = parseInt(deadline) || 24;
        return { amount: parseFloat(amount), deadlineHours: hours };
      });

      if (milestones.some(m => isNaN(m.amount) || m.amount <= 0)) {
        console.error('Invalid milestone amounts'); process.exit(1);
      }

      const { createMilestoneEscrow } = await import('./src/milestone-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.milestoneEscrow?.address;
      if (!contractAddr) {
        console.error('TaskEscrowV3 not configured. Add milestoneEscrow.address to config.');
        process.exit(1);
      }

      const totalUSDC = milestones.reduce((s, m) => s + m.amount, 0).toFixed(2);
      await checkGuard(config, { to: contractAddr, usdcAmount: totalUSDC, action: 'createMilestoneEscrow' });
      console.log(`Creating milestone escrow: ${milestones.length} milestones, total $${totalUSDC} USDC`);
      playSound('escrow-sealed');
      const { txHash, totalAmount } = await createMilestoneEscrow(wallet, contractAddr, {
        taskId: flags['task-id'],
        worker: flags.worker,
        milestones,
      });
      console.log(`Created: ${txHash}`);
      console.log(`Total locked: $${totalAmount} USDC`);
    },

    async 'release-milestone'(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      if (flags.index === undefined) { console.error('--index required'); process.exit(1); }

      const { releaseMilestone } = await import('./src/milestone-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.milestoneEscrow?.address;
      if (!contractAddr) { console.error('TaskEscrowV3 not configured.'); process.exit(1); }

      await checkGuard(config, { to: contractAddr, action: 'releaseMilestone' });
      console.log(`Releasing milestone ${flags.index}...`);
      const { txHash } = await releaseMilestone(wallet, contractAddr, flags['task-id'], parseInt(flags.index));
      console.log(`Released: ${txHash}`); playSound('payment-released');
    },

    async 'milestone-status'(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }

      const { getMilestoneEscrowStatus } = await import('./src/milestone-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.milestoneEscrow?.address;
      if (!contractAddr) { console.error('TaskEscrowV3 not configured.'); process.exit(1); }

      const status = await getMilestoneEscrowStatus(wallet, contractAddr, flags['task-id']);
      if (!status) { console.log('No milestone escrow found for this task.'); return; }

      console.log(`Milestone escrow for ${flags['task-id']}:`);
      console.log(`  Requestor: ${status.requestor}`);
      console.log(`  Worker: ${status.worker}`);
      console.log(`  Total: $${status.totalAmount} USDC`);
      console.log(`  Released: ${status.releasedCount}/${status.milestoneCount}\n`);
      for (const m of status.milestones) {
        console.log(`  [${m.index}] $${m.amount} — ${m.status} — deadline: ${new Date(m.deadline * 1000).toISOString()}`);
      }
    },
  },

  // ─── Swarm Commands (Multi-Worker Escrow) ───
  swarm: {
    async 'create-task'(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      if (!flags.budget) { console.error('--budget required'); process.exit(1); }
      if (!flags.milestones) { console.error('--milestones <count> required'); process.exit(1); }

      const { createSwarmTask } = await import('./src/swarm-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.swarmEscrow?.address;
      if (!contractAddr) { console.error('SwarmEscrow not configured.'); process.exit(1); }

      await checkGuard(config, { to: contractAddr, action: 'createSwarmTask' });
      const { txHash, taskIdHash } = await createSwarmTask(wallet, contractAddr, {
        taskId: flags['task-id'],
        totalBudget: flags.budget,
        milestoneCount: parseInt(flags.milestones),
        bidDeadlineHours: parseInt(flags['bid-deadline'] || '24'),
        bondAmount: flags.bond || '0',
      });
      console.log(`Task created (bidding open): ${txHash}`);
      console.log(`Task hash: ${taskIdHash}`);
      playSound('escrow-sealed');
    },

    async bid(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      if (!flags.price) { console.error('--price required'); process.exit(1); }

      const { placeBid } = await import('./src/swarm-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.swarmEscrow?.address;
      if (!contractAddr) { console.error('SwarmEscrow not configured.'); process.exit(1); }

      await checkGuard(config, { to: contractAddr, usdcAmount: flags.bond || '0', action: 'placeBid' });
      const { txHash } = await placeBid(wallet, contractAddr, {
        taskId: flags['task-id'],
        price: flags.price,
      });
      console.log(`Bid placed: ${txHash}`);
      playSound('stake-locked');
    },

    async 'accept-bid'(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      if (!flags.worker) { console.error('--worker required'); process.exit(1); }

      const { acceptBid } = await import('./src/swarm-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.swarmEscrow?.address;
      if (!contractAddr) { console.error('SwarmEscrow not configured.'); process.exit(1); }

      const { txHash } = await acceptBid(wallet, contractAddr, {
        taskId: flags['task-id'],
        worker: flags.worker,
      });
      console.log(`Bid accepted: ${txHash}`);
      playSound('approved');
    },

    async 'fund-and-assign'(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      if (!flags.assignments) { console.error('--assignments "worker:amount:hours,..." required'); process.exit(1); }

      const assignments = flags.assignments.split(',').map(a => {
        const [worker, amount, hours] = a.trim().split(':');
        return { worker, amount: parseFloat(amount), deadlineHours: parseInt(hours || '24') };
      });

      const { fundAndAssign } = await import('./src/swarm-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.swarmEscrow?.address;
      if (!contractAddr) { console.error('SwarmEscrow not configured.'); process.exit(1); }

      const totalUSDC = assignments.reduce((s, a) => s + a.amount, 0).toFixed(2);
      await checkGuard(config, { to: contractAddr, usdcAmount: totalUSDC, action: 'fundAndAssign' });
      console.log(`Funding task with ${assignments.length} milestone assignments, total $${totalUSDC} USDC...`);
      const { txHash, totalAmount } = await fundAndAssign(wallet, contractAddr, {
        taskId: flags['task-id'],
        assignments,
      });
      console.log(`Funded and assigned: ${txHash}`);
      console.log(`Total locked: $${totalAmount} USDC`);
      playSound('escrow-sealed');
    },

    async 'set-coordinator'(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      if (!flags.coordinator) { console.error('--coordinator required'); process.exit(1); }

      const { setCoordinator } = await import('./src/swarm-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.swarmEscrow?.address;
      if (!contractAddr) { console.error('SwarmEscrow not configured.'); process.exit(1); }

      const { txHash } = await setCoordinator(wallet, contractAddr, {
        taskId: flags['task-id'],
        coordinator: flags.coordinator,
      });
      console.log(`Coordinator set: ${txHash}`);
    },

    async 'release-milestone'(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }
      if (flags.index === undefined) { console.error('--index required'); process.exit(1); }

      const { releaseSwarmMilestone } = await import('./src/swarm-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.swarmEscrow?.address;
      if (!contractAddr) { console.error('SwarmEscrow not configured.'); process.exit(1); }

      await checkGuard(config, { to: contractAddr, action: 'releaseSwarmMilestone' });
      console.log(`Releasing swarm milestone ${flags.index}...`);
      const { txHash } = await releaseSwarmMilestone(wallet, contractAddr, flags['task-id'], parseInt(flags.index));
      console.log(`Released: ${txHash}`); playSound('payment-released');
    },

    async 'cancel-task'(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }

      const { cancelSwarmTask } = await import('./src/swarm-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.swarmEscrow?.address;
      if (!contractAddr) { console.error('SwarmEscrow not configured.'); process.exit(1); }

      const { txHash } = await cancelSwarmTask(wallet, contractAddr, flags['task-id']);
      console.log(`Task cancelled, bonds refunded: ${txHash}`);
    },

    async status(config, flags) {
      if (!flags['task-id']) { console.error('--task-id required'); process.exit(1); }

      const { getSwarmTaskStatus } = await import('./src/swarm-escrow.js');
      const wallet = await getWallet(config);
      const contractAddr = config.swarmEscrow?.address;
      if (!contractAddr) { console.error('SwarmEscrow not configured.'); process.exit(1); }

      const s = await getSwarmTaskStatus(wallet, contractAddr, flags['task-id']);
      if (!s) { console.log('No swarm task found.'); return; }

      console.log(`Swarm task: ${flags['task-id']}`);
      console.log(`  Status: ${s.status}`);
      console.log(`  Requestor: ${s.requestor}`);
      console.log(`  Budget: $${s.totalBudget} USDC`);
      console.log(`  Bond: $${s.bondAmount} USDC`);
      console.log(`  Bid deadline: ${new Date(s.bidDeadline * 1000).toISOString()}`);
      if (s.coordinator) console.log(`  Coordinator: ${s.coordinator}`);
      console.log(`  Milestones: ${s.releasedCount}/${s.milestoneCount} released\n`);

      if (s.bids.length) {
        console.log('  Bids:');
        for (const b of s.bids) {
          const status = b.accepted ? '✅ accepted' : b.refunded ? '↩ refunded' : '⏳ pending';
          console.log(`    ${b.worker.slice(0, 10)}... $${b.price} [${status}]`);
        }
        console.log();
      }

      for (const m of s.milestones) {
        const workerStr = m.worker === '0x0000000000000000000000000000000000000000' ? 'unassigned' : m.worker.slice(0, 10) + '...';
        console.log(`  [${m.index}] $${m.amount} → ${workerStr} — ${m.status}`);
      }
    },
  },

  // ─── Worker Commands ───
  worker: {
    async start(config, flags) {
      const { agent, address } = await getAgent(config);
      console.log(`Worker agent: ${address}`);

      const board = await getBoard(agent, config);
      if (!board) { console.error('No board configured.'); process.exit(1); }

      // Post profile
      const { createProfile, broadcastProfile } = await import('./src/profile.js');
      const profile = createProfile(address, {
        skills: config.worker?.skills || [],
        rates: config.worker?.rates || {},
        description: 'OpenClaw agent ready for work.',
      });
      await broadcastProfile(board, profile);
      console.log(`Profile posted. Skills: ${profile.skills.join(', ')}`);

      const { encodeText } = await import('@xmtp/agent-sdk');
      const { MessageType } = await import('./src/protocol.js');

      // ─── Persistent Message Dedup ───
      // SECURITY: Prevents re-processing tasks after restart
      const SEEN_FILE = join(__dirname, '.worker-seen.json');
      let seenData = { messages: [], listings: [] };
      try {
        if (existsSync(SEEN_FILE)) {
          seenData = JSON.parse(readFileSync(SEEN_FILE, 'utf-8'));
          // Keep only last 1000 entries to prevent unbounded growth
          if (seenData.messages.length > 1000) seenData.messages = seenData.messages.slice(-1000);
          if (seenData.listings.length > 500) seenData.listings = seenData.listings.slice(-500);
        }
      } catch {}
      const seenMessages = new Set(seenData.messages || []);
      const seenListings = new Set(seenData.listings || []);

      function persistSeen() {
        try {
          writeFileSync(SEEN_FILE, JSON.stringify({
            messages: [...seenMessages].slice(-1000),
            listings: [...seenListings].slice(-500),
          }));
        } catch {}
      }
      // Save periodically
      setInterval(persistSeen, 30000);

      // ─── Rate Limiting ───
      let activeTasks = 0;
      const MAX_CONCURRENT_TASKS = parseInt(flags['max-tasks'] || '1');
      let bidCount = 0;
      const MAX_BIDS_PER_HOUR = parseInt(flags['max-bids'] || '10');
      setInterval(() => { bidCount = 0; }, 3600000); // reset hourly

      const maxBid = parseFloat(config.worker?.maxBid || '20.00');
      const minBid = parseFloat(config.worker?.minBid || '0.50');
      const mySkills = config.worker?.skills || [];
      const myRates = config.worker?.rates || {};
      const autoAccept = config.worker?.autoAccept || false;

      console.log(`\nListening for listings (auto-bid: ${autoAccept})...\n`);

      const poll = async () => {
        try {
          await board.sync();
          const msgs = await board.messages({ limit: 30 });

          for (const m of msgs) {
            if (seenMessages.has(m.id)) continue;
            seenMessages.add(m.id);
            if (m.senderInboxId === agent.client.inboxId) continue;

            let parsed;
            try {
              parsed = JSON.parse(typeof m.content === 'string' ? m.content : JSON.stringify(m.content));
            } catch { continue; }
            if (!parsed?.type) continue;

            if (parsed.type === 'listing') {
              if (seenListings.has(parsed.taskId)) continue;
              seenListings.add(parsed.taskId);

              const budget = parseFloat(parsed.budget);
              const needed = parsed.skills_needed || [];
              const matches = needed.length === 0 ? mySkills : needed.filter(s => mySkills.includes(s));

              console.log(`[LISTING] "${parsed.title}" — $${parsed.budget} USDC`);
              console.log(`  Skills needed: ${needed.join(', ') || 'any'}`);
              console.log(`  Match: ${matches.length}/${Math.max(needed.length, 1)}`);

              if (matches.length === 0 && needed.length > 0) {
                console.log('  → Skipping (no skill match)\n');
                continue;
              }
              if (budget > maxBid || budget < minBid) {
                console.log(`  → Skipping (budget out of range $${minBid}-$${maxBid})\n`);
                continue;
              }

              let bidPrice = budget;
              if (matches.length > 0) {
                const avgRate = matches.reduce((sum, s) => sum + parseFloat(myRates[s] || '2.00'), 0) / matches.length;
                bidPrice = Math.min(budget, avgRate);
              }

              if (autoAccept) {
                // Rate limiting: prevent bid spam
                if (bidCount >= MAX_BIDS_PER_HOUR) {
                  console.log(`  → Skipping (bid rate limit: ${MAX_BIDS_PER_HOUR}/hour)\n`);
                  continue;
                }
                const bid = {
                  type: MessageType.BID,
                  taskId: parsed.taskId,
                  worker: address,
                  price: bidPrice.toFixed(2),
                  estimatedTime: '1h',
                  skills: matches,
                };
                await board.send(encodeText(JSON.stringify(bid)));
                bidCount++;
                dashState.registerAgent(address, 'worker');
                persistSeen();
                console.log(`  → Auto-bid: $${bidPrice.toFixed(2)} (${bidCount}/${MAX_BIDS_PER_HOUR} this hour)\n`);
              } else {
                console.log(`  → Waiting for manual bid (run: node cli.js board bid --task-id ${parsed.taskId} --price ${bidPrice.toFixed(2)})\n`);
              }
            }

            // Handle task assignments in private groups
            if (parsed.type === 'task') {
              if (activeTasks >= MAX_CONCURRENT_TASKS) {
                console.log(`[TASK RECEIVED] "${parsed.title}" — QUEUED (${activeTasks}/${MAX_CONCURRENT_TASKS} active)`);
                continue;
              }
              activeTasks++;
              console.log(`[TASK RECEIVED] "${parsed.title}" (${activeTasks}/${MAX_CONCURRENT_TASKS} active)`);
              console.log(`  Executing...`);
              const { execute } = await import('./src/executor.js');
              try {
                const result = await execute(parsed, config);
                // Send result back
                const { sendProtocolMessage } = await import('./src/agent.js');
                // Find the conversation this came from
                await agent.client.conversations.sync();
                const convos = await agent.client.conversations.list();
                // Send to all recent convos (we'll find the right one)
                for (const c of convos) {
                  if (c.id === board.id) continue;
                  try {
                    await c.sync();
                    const recentMsgs = await c.messages({ limit: 5 });
                    const hasTask = recentMsgs.some(rm => {
                      try {
                        const p = JSON.parse(typeof rm.content === 'string' ? rm.content : JSON.stringify(rm.content));
                        return p.type === 'task' && p.id === parsed.id;
                      } catch { return false; }
                    });
                    if (hasTask) {
                      const subtaskId = parsed.subtasks?.[0]?.id || `${parsed.id}-s1`;
                      await sendProtocolMessage(c, {
                        type: 'result',
                        taskId: parsed.id,
                        subtaskId,
                        worker: address,
                        result,
                      });
                      dashState.registerAgent(address, 'worker');
                      dashState.logClaim(parsed.id, subtaskId, address);
                      dashState.logResult(parsed.id, subtaskId, address);
                      console.log(`  → Result submitted to group ${c.id}\n`);
                      break;
                    }
                  } catch {}
                }
              } catch (err) {
                console.error(`  → Execution failed: ${err.message}\n`);
              }
            }
          }
        } catch (e) {
          console.error(`[ERROR] ${e.message?.slice(0, 100)}`);
        }
      };

      // Also poll private groups for tasks
      const pollPrivateGroups = async () => {
        try {
          await agent.client.conversations.sync();
          const convos = await agent.client.conversations.list();
          for (const c of convos) {
            if (c.id === board.id) continue;
            await c.sync();
            const msgs = await c.messages({ limit: 10 });
            for (const m of msgs) {
              if (seenMessages.has(m.id)) continue;
              seenMessages.add(m.id);
              if (m.senderInboxId === agent.client.inboxId) continue;
              try {
                const parsed = JSON.parse(typeof m.content === 'string' ? m.content : JSON.stringify(m.content));
                if (parsed?.type === 'task') {
                  console.log(`[TASK from private group] "${parsed.title}"`);
                  const { execute } = await import('./src/executor.js');
                  const result = await execute(parsed, config);
                  const { sendProtocolMessage } = await import('./src/agent.js');
                  const subId = parsed.subtasks?.[0]?.id || `${parsed.id}-s1`;
                  await sendProtocolMessage(c, {
                    type: 'result',
                    taskId: parsed.id,
                    subtaskId: subId,
                    worker: address,
                    result,
                  });

                  // Submit deliverable hash on-chain (verification trail)
                  try {
                    const { submitDeliverable, hashContent, verifyCodeTask, recordVerification } = await import('./src/verification.js');
                    const wallet = await getWallet(config);
                    const registryAddr = config.verification?.registry || '0x2120D4e0074e0a41762dF785f2c99086aB8bc51b';
                    const deliverableStr = JSON.stringify(result);
                    const { txHash: dvTx, deliverableHash } = await submitDeliverable(wallet, registryAddr, parsed.id, deliverableStr);
                    console.log(`  → Deliverable hash on-chain: ${deliverableHash.slice(0, 18)}... (${dvTx.slice(0, 14)}...)`);

                    // Auto-verify code tasks with acceptance criteria
                    if (parsed.criteria && result.category === 'coding' && result.status === 'completed') {
                      const workDir = result.files?.length ? join(__dirname, 'workdir', parsed.id) : null;
                      if (workDir) {
                        const report = await verifyCodeTask(workDir, parsed.criteria);
                        const reportStr = JSON.stringify(report);
                        const { txHash: vfTx } = await recordVerification(wallet, registryAddr, parsed.id, reportStr, report.passed);
                        console.log(`  → Verification ${report.passed ? 'PASSED' : 'FAILED'} on-chain (${vfTx.slice(0, 14)}...)`);
                      }
                    }

                    // Notify requestor about on-chain verification
                    await sendProtocolMessage(c, {
                      type: 'deliverable_submitted',
                      taskId: parsed.id,
                      deliverableHash,
                      txHash: dvTx,
                      registry: registryAddr,
                    });
                  } catch (vErr) {
                    console.log(`  → Verification trail skipped: ${vErr.message?.slice(0, 80)}`);
                  }

                  dashState.registerAgent(address, 'worker');
                  dashState.logClaim(parsed.id, subId, address);
                  dashState.logResult(parsed.id, subId, address);
                  console.log(`  → Result submitted\n`);
                }
              } catch {}
            }
          }
        } catch {}
      };

      // Poll loop
      await poll();
      setInterval(poll, 5000);
      setInterval(pollPrivateGroups, 10000);

      process.on('SIGINT', async () => {
        console.log('\nShutting down...');
        await agent.stop();
        process.exit(0);
      });

      // Keep alive
      await new Promise(() => {});
    },

    // ─── Staking Commands ───

    async stake(config, flags) {
      if (!flags.amount) { console.error('--amount required (USDC)'); process.exit(1); }
      const { depositStake } = await import('./src/staking.js');
      const wallet = await getWallet(config);
      const contractAddr = config.staking?.address;
      if (!contractAddr) {
        console.error('WorkerStake not configured. Add staking.address to config.');
        process.exit(1);
      }

      await checkGuard(config, { to: contractAddr, usdcAmount: flags.amount, action: 'stake' });
      console.log(`Depositing $${flags.amount} USDC stake...`);
      const { txHash } = await depositStake(wallet, contractAddr, flags.amount);
      console.log(`Staked: ${txHash}`); playSound('stake-locked');
      console.log('Your stake signals quality commitment to requestors.');
    },

    async unstake(config, flags) {
      if (!flags.amount) { console.error('--amount required (USDC)'); process.exit(1); }
      const { withdrawStake } = await import('./src/staking.js');
      const wallet = await getWallet(config);
      const contractAddr = config.staking?.address;
      if (!contractAddr) { console.error('WorkerStake not configured.'); process.exit(1); }

      await checkGuard(config, { to: contractAddr, usdcAmount: flags.amount, action: 'unstake' });
      console.log(`Withdrawing $${flags.amount} USDC stake...`);
      const { txHash } = await withdrawStake(wallet, contractAddr, flags.amount);
      console.log(`Withdrawn: ${txHash}`); playSound('unstaked');
    },

    async 'stake-status'(config, flags) {
      const { getStakeStatus } = await import('./src/staking.js');
      const wallet = await getWallet(config);
      const contractAddr = config.staking?.address;
      if (!contractAddr) { console.error('WorkerStake not configured.'); process.exit(1); }

      const status = await getStakeStatus(wallet, contractAddr, wallet.address);
      console.log(`Stake status for ${wallet.address}:`);
      console.log(`  Total deposited: $${status.totalDeposited} USDC`);
      console.log(`  Available:       $${status.available} USDC`);
      console.log(`  Locked (tasks):  $${status.locked} USDC`);
      console.log(`  Slashed:         $${status.slashed} USDC`);
      if (status.emergencyWithdrawRequested) {
        console.log(`  Emergency withdraw requested: ${new Date(status.emergencyWithdrawTime * 1000).toISOString()}`);
      }
    },
  },

  wallet: {
    async 'guard-status'(config, flags) {
      const { guardWallet, printGuardStatus } = await import('./src/wallet-guard.js');
      const wallet = await getWallet(config);
      const guarded = guardWallet(wallet, { workdir: dirname(CONFIG_PATH) });
      printGuardStatus(guarded);
    },

    async 'guard-init'(config, flags) {
      const { initGuardConfig } = await import('./src/wallet-guard.js');
      const overrides = {};
      if (flags['max-tx']) overrides.maxPerTransaction = flags['max-tx'];
      if (flags['max-daily']) overrides.maxDailySpend = flags['max-daily'];
      if (flags.mode) overrides.mode = flags.mode;
      if (flags['max-hourly']) overrides.maxTransactionsPerHour = parseInt(flags['max-hourly']);

      const workdir = dirname(CONFIG_PATH);
      const guard = initGuardConfig(workdir, overrides);
      console.log('Wallet guard initialized:');
      console.log(`  Mode: ${guard.mode}`);
      console.log(`  Per-tx limit: ${guard.maxPerTransaction} USDC`);
      console.log(`  Daily limit: ${guard.maxDailySpend} USDC`);
      console.log(`  Hourly tx limit: ${guard.maxTransactionsPerHour}`);
      console.log(`  Config saved to: ${join(workdir, '.wallet-guard.json')}`);
      playSound('guard-active');
    },

    async 'guard-allow'(config, flags) {
      const { guardWallet } = await import('./src/wallet-guard.js');
      const address = flags.address;
      if (!address) { console.error('--address required'); process.exit(1); }
      if (!/^0x[a-fA-F0-9]{40}$/.test(address)) { console.error('Invalid address format'); process.exit(1); }

      const wallet = await getWallet(config);
      const guarded = guardWallet(wallet, { workdir: dirname(CONFIG_PATH) });
      const current = guarded.guard.allowedAddresses || [];
      if (!current.map(a => a.toLowerCase()).includes(address.toLowerCase())) {
        current.push(address);
        guarded.updateConfig({ allowedAddresses: current });
        console.log(`Added ${address} to allowlist (${current.length} total)`);
      } else {
        console.log(`${address} already in allowlist`);
      }
    },

    async 'guard-set'(config, flags) {
      const { guardWallet } = await import('./src/wallet-guard.js');
      const wallet = await getWallet(config);
      const guarded = guardWallet(wallet, { workdir: dirname(CONFIG_PATH) });

      const updates = {};
      if (flags['max-tx']) updates.maxPerTransaction = flags['max-tx'];
      if (flags['max-daily']) updates.maxDailySpend = flags['max-daily'];
      if (flags['max-hourly']) updates.maxTransactionsPerHour = parseInt(flags['max-hourly']);
      if (flags.mode) {
        if (!['full', 'readOnly', 'spendOnly'].includes(flags.mode)) {
          console.error('Mode must be: full, readOnly, or spendOnly');
          process.exit(1);
        }
        updates.mode = flags.mode;
      }

      if (Object.keys(updates).length === 0) {
        console.error('No settings to update. Use --max-tx, --max-daily, --max-hourly, or --mode');
        process.exit(1);
      }

      guarded.updateConfig(updates);
      console.log('Guard config updated:', updates);
    },

    async 'audit-log'(config, flags) {
      const { readFileSync, existsSync } = await import('fs');
      const logPath = join(dirname(CONFIG_PATH), '.wallet-audit.log');
      if (!existsSync(logPath)) {
        console.log('No audit log yet. Transactions will be logged after guard is initialized.');
        return;
      }

      const lines = readFileSync(logPath, 'utf8').trim().split('\n');
      const limit = parseInt(flags.limit) || 20;
      const recent = lines.slice(-limit);
      console.log(`Last ${recent.length} audit entries:\n`);
      for (const line of recent) {
        try {
          const entry = JSON.parse(line);
          const time = entry.timestamp?.slice(11, 19) || '??:??:??';
          const status = entry.status === 'blocked' ? '❌' : entry.status === 'confirmed' ? '✅' : '⏳';
          console.log(`  ${time} ${status} ${entry.action || '?'} → ${entry.to?.slice(0, 10) || entry.spender?.slice(0, 10) || '?'}... ${entry.usdcAmount ? entry.usdcAmount + ' USDC' : ''} ${entry.reason || ''}`);
        } catch {
          // skip malformed
        }
      }
    },
  },
};

// ─── Main ───

const args = process.argv.slice(2);
const { positional, flags } = parseArgs(args);
const [command, subcommand] = positional;

// --silent disables sound bites
if (flags.silent || flags.quiet || process.env.SWARM_SILENT) {
  setSoundsEnabled(false);
}

if (!command || !subcommand) {
  console.log(`
Agent Swarm CLI

Usage: node cli.js <command> <subcommand> [--flags]

Commands:
  setup init [--key <privkey>] [--skills <s1,s2>] [--members <addr1,addr2>] [--board-id <id>]
                                  First-time setup: config, XMTP registration, board, wallet check
  setup check                     Check wallet balance, config, and board status

  board create [--members <a1,a2>] Create a new bulletin board (optionally with members)
  board connect --id <boardId>    Connect to existing board
  board listings                  List active listings
  board workers [--skill <s>]     List worker profiles
  board profile                   Post your worker profile
  board find-workers --skill <s>  Find workers with a skill

  registry list                      Browse all registered boards on-chain
  registry register [--name <n>]     Register your board on-chain for discovery
  registry join --board-id <id>      Request to join a board
  registry requests                  View pending join requests (board owner)
  registry approve --index <i>       Approve a join request + add to XMTP group

  listing post --title <t> --budget <b> [--skills <s1,s2>] [--category <c>]
  listing bids --task-id <id>     View bids on a listing
  listing accept --task-id <id> --worker <addr> [--amount <a>] [--deadline <h>]

  task monitor --task-id <id>     Monitor a task for results
  task list                       List all local tasks

  worker start                    Start worker daemon (find work, execute, deliver)

  escrow status --task-id <id>    Check escrow status
  escrow release --task-id <id>   Release funds to worker
  escrow dispute --task-id <id>   File a dispute
  escrow refund --task-id <id>    Refund after deadline
  escrow verify --task-id <id>       Check on-chain verification trail
  escrow claim-timeout --task-id <id>  Claim refund after dispute timeout

  escrow create-milestone --task-id <id> --worker <addr> --milestones "1.00:24h,2.00:48h,1.50:72h"
                                  Create milestone escrow (amount:deadline pairs)
  escrow release-milestone --task-id <id> --index <n>
                                  Release a specific milestone to worker
  escrow milestone-status --task-id <id>
                                  Check milestone escrow status

  worker stake --amount <usdc>    Deposit USDC stake (quality assurance)
  worker unstake --amount <usdc>  Withdraw available stake
  worker stake-status             Check your stake balance

  wallet guard-status             Show wallet guard config and spending
  wallet guard-init [--max-tx <usdc>] [--max-daily <usdc>] [--mode <full|readOnly|spendOnly>]
                                  Initialize wallet guard with spending limits
  wallet guard-allow --address <addr>  Add address to allowlist
  wallet guard-set --max-tx <usdc> [--max-daily <usdc>] [--max-hourly <n>] [--mode <mode>]
                                  Update wallet guard settings
  wallet audit-log [--limit <n>]  Show recent transaction audit log

  swarm create-task --task-id <id> --budget <usdc> --milestones <count> [--bid-deadline <hours>] [--bond <usdc>]
                                  Create multi-worker task (opens for bidding)
  swarm bid --task-id <id> --price <usdc>
                                  Place a bid on a task (deposits bond if required)
  swarm accept-bid --task-id <id> --worker <addr>
                                  Accept a worker's bid
  swarm fund-and-assign --task-id <id> --assignments "worker:amount:hours,..."
                                  Fund escrow and assign milestones to accepted workers
  swarm set-coordinator --task-id <id> --coordinator <addr>
                                  Designate a coordinator for the task
  swarm release-milestone --task-id <id> --index <n>
                                  Release a milestone to its assigned worker
  swarm cancel-task --task-id <id>  Cancel task during bidding (refunds all bonds)
  swarm status --task-id <id>     Full task status (bids, milestones, workers)
  `);
  process.exit(0);
}

if (!commands[command]?.[subcommand]) {
  console.error(`Unknown command: ${command} ${subcommand}`);
  process.exit(1);
}

if (flags.config) CONFIG_PATH = join(__dirname, flags.config);
const config = (command === 'setup' && subcommand === 'init') ? {} : loadConfig();
// Ensure CONFIG_PATH is set for setup init to write to

commands[command][subcommand](config, flags).catch(err => {
  playSoundSync('error');
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
