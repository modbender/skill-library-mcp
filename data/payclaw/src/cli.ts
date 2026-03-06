#!/usr/bin/env node
/**
 * PayClaw - Agent-to-Agent USDC Payments
 * Built for the USDC Hackathon on Moltbook
 */

import { Command } from 'commander';
import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

const CONFIG_DIR = path.join(process.env.HOME || '', '.openclaw', 'payclaw');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');
const ESCROWS_FILE = path.join(CONFIG_DIR, 'escrows.json');
const AGENTS_FILE = path.join(CONFIG_DIR, 'agents.json');

interface Config {
  apiKey: string;
  defaultWallet?: string;
  chain: string;
}

interface Escrow {
  id: string;
  amount: number;
  sender: string;
  recipient: string;
  condition: string;
  status: 'pending' | 'released' | 'refunded';
  createdAt: string;
}

interface Agent {
  name: string;
  address: string;
  description?: string;
  registeredAt: string;
}

// Helper functions
function ensureDir(): void {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
}

function loadConfig(): Config | null {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
    }
  } catch (e) {}
  return null;
}

function saveConfig(config: Config): void {
  ensureDir();
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
  fs.chmodSync(CONFIG_FILE, 0o600);
}

function loadEscrows(): Escrow[] {
  try {
    if (fs.existsSync(ESCROWS_FILE)) {
      return JSON.parse(fs.readFileSync(ESCROWS_FILE, 'utf-8'));
    }
  } catch (e) {}
  return [];
}

function saveEscrows(escrows: Escrow[]): void {
  ensureDir();
  fs.writeFileSync(ESCROWS_FILE, JSON.stringify(escrows, null, 2));
}

function loadAgents(): Agent[] {
  try {
    if (fs.existsSync(AGENTS_FILE)) {
      return JSON.parse(fs.readFileSync(AGENTS_FILE, 'utf-8'));
    }
  } catch (e) {}
  return [];
}

function saveAgents(agents: Agent[]): void {
  ensureDir();
  fs.writeFileSync(AGENTS_FILE, JSON.stringify(agents, null, 2));
}

function generateEscrowId(): string {
  const num = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
  return `ESC-${num}`;
}

// Run circle-wallet command
function circleWallet(cmd: string): string {
  try {
    return execSync(`circle-wallet ${cmd}`, { encoding: 'utf-8' });
  } catch (e: any) {
    throw new Error(e.stderr || e.message);
  }
}

// CLI
const program = new Command();

program
  .name('payclaw')
  .description('Agent-to-Agent USDC Payments for OpenClaw')
  .version('1.0.0');

// Setup command
program
  .command('setup')
  .description('Configure PayClaw with Circle API key')
  .requiredOption('--api-key <key>', 'Circle API key')
  .option('--chain <chain>', 'Default chain', 'ARC-TESTNET')
  .action(async (options) => {
    console.log('🔧 Setting up PayClaw...\n');
    
    try {
      // Setup circle-wallet first
      console.log('Configuring Circle wallet...');
      circleWallet(`setup --api-key ${options.apiKey}`);
      
      // Save PayClaw config
      const config: Config = {
        apiKey: options.apiKey,
        chain: options.chain
      };
      saveConfig(config);
      
      console.log('\n✅ PayClaw configured successfully!');
      console.log('\nNext steps:');
      console.log('  1. Create a wallet: payclaw wallet create "MyAgent"');
      console.log('  2. Get testnet USDC: payclaw faucet');
      console.log('  3. Start paying: payclaw pay <address> <amount>');
    } catch (e: any) {
      console.error('❌ Setup failed:', e.message);
      process.exit(1);
    }
  });

// Wallet commands
const wallet = program.command('wallet').description('Wallet management');

wallet
  .command('create [name]')
  .description('Create a new wallet')
  .action(async (name) => {
    try {
      const result = circleWallet(`create "${name || 'PayClaw Wallet'}"`);
      console.log(result);
      
      // Get the wallet address and save as default
      const listResult = circleWallet('list');
      const match = listResult.match(/Address: (0x[a-fA-F0-9]+)/);
      if (match) {
        const config = loadConfig() || { apiKey: '', chain: 'ARC-TESTNET' };
        config.defaultWallet = match[1];
        saveConfig(config);
      }
    } catch (e: any) {
      console.error('❌ Error:', e.message);
    }
  });

wallet
  .command('list')
  .description('List all wallets')
  .action(async () => {
    try {
      const result = circleWallet('list');
      console.log(result);
    } catch (e: any) {
      console.error('❌ Error:', e.message);
    }
  });

wallet
  .command('balance')
  .description('Check wallet balance')
  .action(async () => {
    try {
      const result = circleWallet('balance');
      console.log(result);
    } catch (e: any) {
      console.error('❌ Error:', e.message);
    }
  });

wallet
  .command('address')
  .description('Show default wallet address')
  .action(async () => {
    const config = loadConfig();
    if (config?.defaultWallet) {
      console.log(`💳 Your wallet: ${config.defaultWallet}`);
    } else {
      console.log('❌ No default wallet. Create one with: payclaw wallet create');
    }
  });

// Payment commands
program
  .command('pay <address> <amount>')
  .description('Send USDC to an address')
  .option('--memo <memo>', 'Payment memo')
  .action(async (address, amount, options) => {
    console.log(`💸 Sending ${amount} USDC to ${address}...`);
    
    try {
      const result = circleWallet(`send ${address} ${amount}`);
      console.log(result);
      
      if (options.memo) {
        console.log(`📝 Memo: ${options.memo}`);
      }
      
      // Log to history
      const historyFile = path.join(CONFIG_DIR, 'history.json');
      const history = fs.existsSync(historyFile) 
        ? JSON.parse(fs.readFileSync(historyFile, 'utf-8'))
        : [];
      
      history.push({
        type: 'send',
        to: address,
        amount: parseFloat(amount),
        memo: options.memo,
        timestamp: new Date().toISOString()
      });
      
      fs.writeFileSync(historyFile, JSON.stringify(history, null, 2));
    } catch (e: any) {
      console.error('❌ Payment failed:', e.message);
    }
  });

program
  .command('request <amount>')
  .description('Generate payment request')
  .option('--memo <memo>', 'Payment memo')
  .action(async (amount, options) => {
    const config = loadConfig();
    if (!config?.defaultWallet) {
      console.error('❌ No wallet configured. Run: payclaw wallet create');
      return;
    }
    
    console.log('\n💰 Payment Request');
    console.log('─'.repeat(40));
    console.log(`To: ${config.defaultWallet}`);
    console.log(`Amount: ${amount} USDC`);
    if (options.memo) {
      console.log(`Memo: ${options.memo}`);
    }
    console.log('─'.repeat(40));
    console.log('\nShare this with payer:');
    console.log(`  payclaw pay ${config.defaultWallet} ${amount}${options.memo ? ` --memo "${options.memo}"` : ''}`);
  });

program
  .command('history')
  .description('View transaction history')
  .action(async () => {
    const historyFile = path.join(CONFIG_DIR, 'history.json');
    if (!fs.existsSync(historyFile)) {
      console.log('📜 No transaction history yet.');
      return;
    }
    
    const history = JSON.parse(fs.readFileSync(historyFile, 'utf-8'));
    console.log('\n📜 Transaction History');
    console.log('═'.repeat(50));
    
    history.slice(-10).reverse().forEach((tx: any) => {
      const date = new Date(tx.timestamp).toLocaleString();
      if (tx.type === 'send') {
        console.log(`💸 SENT ${tx.amount} USDC → ${tx.to.slice(0, 10)}...`);
      } else if (tx.type === 'receive') {
        console.log(`💰 RECEIVED ${tx.amount} USDC ← ${tx.from.slice(0, 10)}...`);
      }
      if (tx.memo) console.log(`   📝 ${tx.memo}`);
      console.log(`   🕐 ${date}`);
      console.log('');
    });
  });

program
  .command('faucet')
  .description('Get testnet USDC')
  .action(async () => {
    console.log('🚰 Requesting testnet USDC...');
    try {
      const result = circleWallet('drip');
      console.log(result);
    } catch (e: any) {
      console.error('❌ Faucet failed:', e.message);
      console.log('\nTry the Circle faucet directly:');
      console.log('  https://faucet.circle.com');
    }
  });

// Escrow commands
const escrow = program.command('escrow').description('Escrow for agent-to-agent deals');

escrow
  .command('create <amount> <recipient>')
  .description('Create escrow')
  .option('--condition <condition>', 'Release condition', 'Task completed')
  .action(async (amount, recipient, options) => {
    const config = loadConfig();
    if (!config?.defaultWallet) {
      console.error('❌ No wallet configured. Run: payclaw wallet create');
      return;
    }
    
    const escrowId = generateEscrowId();
    const escrows = loadEscrows();
    
    const newEscrow: Escrow = {
      id: escrowId,
      amount: parseFloat(amount),
      sender: config.defaultWallet,
      recipient,
      condition: options.condition,
      status: 'pending',
      createdAt: new Date().toISOString()
    };
    
    escrows.push(newEscrow);
    saveEscrows(escrows);
    
    console.log('\n🔒 Escrow Created');
    console.log('═'.repeat(40));
    console.log(`ID: ${escrowId}`);
    console.log(`Amount: ${amount} USDC`);
    console.log(`Recipient: ${recipient}`);
    console.log(`Condition: ${options.condition}`);
    console.log('═'.repeat(40));
    console.log('\nTo release: payclaw escrow release ' + escrowId);
    console.log('To refund: payclaw escrow refund ' + escrowId);
  });

escrow
  .command('list')
  .description('List active escrows')
  .action(async () => {
    const escrows = loadEscrows();
    const pending = escrows.filter(e => e.status === 'pending');
    
    if (pending.length === 0) {
      console.log('📭 No active escrows.');
      return;
    }
    
    console.log('\n🔒 Active Escrows');
    console.log('═'.repeat(50));
    
    pending.forEach(e => {
      console.log(`${e.id} | ${e.amount} USDC → ${e.recipient.slice(0, 10)}...`);
      console.log(`   Condition: ${e.condition}`);
      console.log('');
    });
  });

escrow
  .command('release <id>')
  .description('Release escrow funds')
  .action(async (id) => {
    const escrows = loadEscrows();
    const escrow = escrows.find(e => e.id === id);
    
    if (!escrow) {
      console.error('❌ Escrow not found:', id);
      return;
    }
    
    if (escrow.status !== 'pending') {
      console.error('❌ Escrow already', escrow.status);
      return;
    }
    
    console.log(`💸 Releasing ${escrow.amount} USDC to ${escrow.recipient}...`);
    
    try {
      const result = circleWallet(`send ${escrow.recipient} ${escrow.amount}`);
      console.log(result);
      
      escrow.status = 'released';
      saveEscrows(escrows);
      
      console.log(`\n✅ Escrow ${id} released successfully!`);
    } catch (e: any) {
      console.error('❌ Release failed:', e.message);
    }
  });

escrow
  .command('refund <id>')
  .description('Refund escrow to sender')
  .action(async (id) => {
    const escrows = loadEscrows();
    const escrow = escrows.find(e => e.id === id);
    
    if (!escrow) {
      console.error('❌ Escrow not found:', id);
      return;
    }
    
    if (escrow.status !== 'pending') {
      console.error('❌ Escrow already', escrow.status);
      return;
    }
    
    escrow.status = 'refunded';
    saveEscrows(escrows);
    
    console.log(`\n✅ Escrow ${id} refunded to sender.`);
  });

// Agent directory commands
const agents = program.command('agents').description('Agent directory');

agents
  .command('register')
  .description('Register your agent in directory')
  .option('--name <name>', 'Agent name')
  .option('--description <desc>', 'Agent description')
  .action(async (options) => {
    const config = loadConfig();
    if (!config?.defaultWallet) {
      console.error('❌ No wallet configured. Run: payclaw wallet create');
      return;
    }
    
    const agentsList = loadAgents();
    const name = options.name || `Agent-${config.defaultWallet.slice(-6)}`;
    
    // Check if already registered
    const existing = agentsList.find(a => a.address === config.defaultWallet);
    if (existing) {
      console.log('ℹ️  Already registered as:', existing.name);
      return;
    }
    
    const agent: Agent = {
      name,
      address: config.defaultWallet,
      description: options.description,
      registeredAt: new Date().toISOString()
    };
    
    agentsList.push(agent);
    saveAgents(agentsList);
    
    console.log('\n✅ Agent Registered');
    console.log('═'.repeat(40));
    console.log(`Name: ${name}`);
    console.log(`Address: ${config.defaultWallet}`);
    if (options.description) {
      console.log(`Description: ${options.description}`);
    }
  });

agents
  .command('list')
  .description('List registered agents')
  .action(async () => {
    const agentsList = loadAgents();
    
    if (agentsList.length === 0) {
      console.log('📭 No agents registered yet.');
      console.log('Register yours: payclaw agents register --name "MyAgent"');
      return;
    }
    
    console.log('\n🤖 Registered Agents');
    console.log('═'.repeat(50));
    
    agentsList.forEach(a => {
      console.log(`${a.name}`);
      console.log(`  💳 ${a.address}`);
      if (a.description) console.log(`  📝 ${a.description}`);
      console.log('');
    });
  });

agents
  .command('find <name>')
  .description('Find agent by name')
  .action(async (name) => {
    const agentsList = loadAgents();
    const agent = agentsList.find(a => 
      a.name.toLowerCase().includes(name.toLowerCase())
    );
    
    if (!agent) {
      console.log('❌ Agent not found:', name);
      return;
    }
    
    console.log('\n🤖 Found Agent');
    console.log('═'.repeat(40));
    console.log(`Name: ${agent.name}`);
    console.log(`Address: ${agent.address}`);
    if (agent.description) {
      console.log(`Description: ${agent.description}`);
    }
    console.log('\nTo pay this agent:');
    console.log(`  payclaw pay ${agent.address} <amount>`);
  });

// Config command
program
  .command('config')
  .description('View configuration')
  .action(async () => {
    const config = loadConfig();
    if (!config) {
      console.log('❌ Not configured. Run: payclaw setup --api-key <key>');
      return;
    }
    
    console.log('\n⚙️  PayClaw Configuration');
    console.log('═'.repeat(40));
    console.log(`API Key: ${config.apiKey.slice(0, 8)}...`);
    console.log(`Chain: ${config.chain}`);
    console.log(`Default Wallet: ${config.defaultWallet || 'Not set'}`);
  });

program.parse();
