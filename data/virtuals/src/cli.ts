#!/usr/bin/env node
/**
 * Virtuals Protocol CLI for OpenClaw
 * Create, manage and trade tokenized AI agents
 */

import { Command } from 'commander';
import { ethers } from 'ethers';
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';

const CONFIG_DIR = path.join(process.env.HOME || '', '.openclaw', 'virtuals');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

// Contract addresses (Base Mainnet)
const CONTRACTS = {
  VIRTUAL_TOKEN: '0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b',
  // Add more as we discover them
};

// Base RPC
const BASE_RPC = 'https://mainnet.base.org';

// ERC20 ABI (minimal)
const ERC20_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
  'function name() view returns (string)',
  'function totalSupply() view returns (uint256)',
];

interface Config {
  wallet?: string;
  privateKey?: string;
}

// Helpers
function ensureDir(): void {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
}

function loadConfig(): Config {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
    }
  } catch (e) {}
  return {};
}

function saveConfig(config: Config): void {
  ensureDir();
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
  fs.chmodSync(CONFIG_FILE, 0o600);
}

function getProvider(): ethers.JsonRpcProvider {
  return new ethers.JsonRpcProvider(BASE_RPC);
}

async function getVirtualPrice(): Promise<{ price: number; marketCap: number; change24h: number; volume24h: number }> {
  try {
    const response = await axios.get(
      'https://api.coingecko.com/api/v3/simple/price?ids=virtual-protocol&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true'
    );
    const data = response.data['virtual-protocol'];
    return {
      price: data.usd,
      marketCap: data.usd_market_cap,
      change24h: data.usd_24h_change,
      volume24h: data.usd_24h_vol,
    };
  } catch (e) {
    throw new Error('Failed to fetch price data');
  }
}

async function getTopAgents(): Promise<any[]> {
  // Note: Virtuals doesn't have a public API for this
  // We'll need to scrape or use their internal API
  // For now, return placeholder
  try {
    // Try to get from their API if it exists
    const response = await axios.get('https://api.virtuals.io/agents?limit=10', {
      timeout: 5000,
    }).catch(() => null);
    
    if (response?.data) {
      return response.data;
    }
    
    // Fallback: Return well-known agents
    return [
      { name: 'aixbt', ticker: 'AIXBT', description: 'AI Trading Analysis Agent' },
      { name: 'Luna', ticker: 'LUNA', description: 'Virtual K-Pop Idol' },
      { name: 'Butler', ticker: 'BUTLER', description: 'Virtuals Protocol Interface Agent' },
    ];
  } catch (e) {
    return [];
  }
}

// CLI
const program = new Command();

program
  .name('virtuals')
  .description('Virtuals Protocol - Tokenized AI Agents on Base')
  .version('1.0.0');

// Price command
program
  .command('price')
  .description('Get $VIRTUAL token price and market data')
  .action(async () => {
    console.log('💰 Fetching $VIRTUAL price...\n');
    
    try {
      const data = await getVirtualPrice();
      
      console.log('═══════════════════════════════════════');
      console.log('         $VIRTUAL Token');
      console.log('═══════════════════════════════════════');
      console.log(`  Price:      $${data.price.toFixed(4)}`);
      console.log(`  Market Cap: $${(data.marketCap / 1e6).toFixed(2)}M`);
      console.log(`  24h Change: ${data.change24h >= 0 ? '+' : ''}${data.change24h.toFixed(2)}%`);
      console.log(`  24h Volume: $${(data.volume24h / 1e6).toFixed(2)}M`);
      console.log('═══════════════════════════════════════');
      console.log(`\n  Contract: ${CONTRACTS.VIRTUAL_TOKEN}`);
      console.log('  Chain: Base (L2)');
    } catch (e: any) {
      console.error('❌ Error:', e.message);
    }
  });

// Agents commands
const agents = program.command('agents').description('AI Agent operations');

agents
  .command('list')
  .description('List top AI agents')
  .option('--top <n>', 'Number of agents to show', '10')
  .action(async (options) => {
    console.log('🤖 Top AI Agents on Virtuals\n');
    
    try {
      const agentList = await getTopAgents();
      
      console.log('═══════════════════════════════════════════════════');
      console.log('  #  | Agent          | Ticker    | Description');
      console.log('═══════════════════════════════════════════════════');
      
      agentList.slice(0, parseInt(options.top)).forEach((agent, i) => {
        const name = (agent.name || 'Unknown').padEnd(14);
        const ticker = ('$' + (agent.ticker || '???')).padEnd(10);
        const desc = (agent.description || '').slice(0, 30);
        console.log(`  ${(i + 1).toString().padStart(2)} | ${name} | ${ticker} | ${desc}`);
      });
      
      console.log('═══════════════════════════════════════════════════');
      console.log('\n  📍 View all: https://app.virtuals.io');
    } catch (e: any) {
      console.error('❌ Error:', e.message);
    }
  });

agents
  .command('info <name>')
  .description('Get agent details')
  .action(async (name) => {
    console.log(`🔍 Looking up agent: ${name}\n`);
    
    // For now, show placeholder info
    console.log('═══════════════════════════════════════');
    console.log(`  Agent: ${name}`);
    console.log('═══════════════════════════════════════');
    console.log('  ℹ️  Full agent info requires Virtuals API access');
    console.log(`  📍 View on app: https://app.virtuals.io/agents/${name}`);
    console.log('');
  });

// Balance command
program
  .command('balance <address>')
  .description('Check $VIRTUAL balance')
  .action(async (address) => {
    console.log(`💳 Checking balance for ${address.slice(0, 10)}...`);
    
    try {
      const provider = getProvider();
      const token = new ethers.Contract(CONTRACTS.VIRTUAL_TOKEN, ERC20_ABI, provider);
      
      const balance = await token.balanceOf(address);
      const decimals = await token.decimals();
      const formatted = ethers.formatUnits(balance, decimals);
      
      const priceData = await getVirtualPrice();
      const usdValue = parseFloat(formatted) * priceData.price;
      
      console.log('\n═══════════════════════════════════════');
      console.log('         $VIRTUAL Balance');
      console.log('═══════════════════════════════════════');
      console.log(`  Balance: ${parseFloat(formatted).toFixed(2)} VIRTUAL`);
      console.log(`  Value:   $${usdValue.toFixed(2)} USD`);
      console.log('═══════════════════════════════════════');
    } catch (e: any) {
      console.error('❌ Error:', e.message);
    }
  });

// Create agent command
program
  .command('create')
  .description('Create a new AI agent (requires funds)')
  .requiredOption('--name <name>', 'Agent name')
  .requiredOption('--ticker <ticker>', 'Token ticker (max 6 chars)')
  .requiredOption('--description <desc>', 'Agent description')
  .option('--image <url>', 'Profile image URL')
  .action(async (options) => {
    console.log('🚀 Creating Agent on Virtuals\n');
    
    const config = loadConfig();
    if (!config.privateKey) {
      console.log('❌ No wallet configured. Run:');
      console.log('   virtuals config --wallet <address> --private-key <key>');
      return;
    }
    
    console.log('Agent Details:');
    console.log(`  Name: ${options.name}`);
    console.log(`  Ticker: $${options.ticker}`);
    console.log(`  Description: ${options.description}`);
    console.log('');
    
    console.log('⚠️  Creating agents requires:');
    console.log('   • 1,000 $VIRTUAL (~$590)');
    console.log('   • ETH for gas on Base');
    console.log('');
    console.log('📍 For now, create agents at: https://fun.virtuals.io');
    console.log('   (Smart contract integration coming soon)');
  });

// Config command
program
  .command('config')
  .description('Configure wallet for trading')
  .option('--wallet <address>', 'Wallet address')
  .option('--private-key <key>', 'Private key (stored securely)')
  .option('--show', 'Show current config')
  .action(async (options) => {
    if (options.show) {
      const config = loadConfig();
      console.log('\n⚙️  Virtuals Configuration');
      console.log('═══════════════════════════════════════');
      console.log(`  Wallet: ${config.wallet || 'Not set'}`);
      console.log(`  Key:    ${config.privateKey ? '••••••••' : 'Not set'}`);
      console.log('═══════════════════════════════════════');
      return;
    }
    
    const config = loadConfig();
    
    if (options.wallet) {
      config.wallet = options.wallet;
    }
    if (options.privateKey) {
      config.privateKey = options.privateKey;
    }
    
    saveConfig(config);
    console.log('✅ Configuration saved');
  });

// Info command
program
  .command('info')
  .description('Show Virtuals Protocol info')
  .action(() => {
    console.log(`
╔═══════════════════════════════════════════════════════════╗
║              VIRTUALS PROTOCOL                            ║
║           Society of AI Agents                            ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Virtuals Protocol enables tokenized AI agents that       ║
║  can coordinate, transact, and generate value onchain.    ║
║                                                           ║
║  Key Features:                                            ║
║  • Tokenized AI Agents (each with own token)              ║
║  • Agent Commerce Protocol (agent-to-agent payments)      ║
║  • GAME Framework (agent development)                     ║
║  • Revenue sharing with token holders                     ║
║                                                           ║
║  Costs:                                                   ║
║  • Create Agent: ~1,000 VIRTUAL (~$590)                   ║
║  • Graduation: 42,000 VIRTUAL accumulated                 ║
║  • LP locked for 10 years                                 ║
║                                                           ║
║  Links:                                                   ║
║  • App: https://app.virtuals.io                           ║
║  • Create: https://fun.virtuals.io                        ║
║  • Docs: https://whitepaper.virtuals.io                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
`);
  });

program.parse();
