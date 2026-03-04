/**
 * AI Frens Interaction Script
 * 
 * Check Fren stats, buy Frencoins, and stake for subscriber badges.
 * 
 * Usage:
 *   npx ts-node aifrens.ts check-fren wiz
 *   npx ts-node aifrens.ts buy 0xA4Bbac7eD5BdA8Ec71a1aF5ee84d4c5a737bD875 100
 */

import { createWalletClient, createPublicClient, http, formatEther, formatUnits, parseEther, parseUnits } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base } from 'viem/chains';

// ============ CONFIG ============

const CONFIG = {
  // Core contracts (Base Mainnet)
  AGENT_STATION: '0xf4f76d4f67bb46b9a81f175b2cb9db68d7bd226b' as `0x${string}`,
  BACKEND_WALLET: '0xe07e9cbf9a55d02e3ac356ed4706353d98c5a618' as `0x${string}`,
  MAGIC_TOKEN: '0xF1572d1Da5c3CcE14eE5a1c9327d17e9ff0E3f43' as `0x${string}`,
  UNISWAP_ROUTER: '0x2626664c2603336E57B271c5C0b26F421741e481' as `0x${string}`,
  MAGICETH_POOL_FEE: 3000, // 0.3%
  
  // Known Frencoins
  KNOWN_FRENS: {
    'wiz': '0xA4Bbac7eD5BdA8Ec71a1aF5ee84d4c5a737bD875',
    'smol': '0xA4Bbac7eD5BdA8Ec71a1aF5ee84d4c5a737bD875',
    'mio': '0xe19e7429ab6c1f9dd391faa88fbb940c7d22f18f',
  } as Record<string, string>,
  
  // Known pools
  KNOWN_POOLS: {
    'smol': '0x21e51dbdc6aa6e00deabd59ff97835445414ea76',
  } as Record<string, string>,
  
  PLATFORM_URL: 'https://aifrens.lol/platform',
  CREATE_URL: 'https://aifrens.lol/platform/create',
};

// ============ ABIs ============

const ERC20_ABI = [
  {
    name: 'name',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'string' }]
  },
  {
    name: 'symbol',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'string' }]
  },
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ name: '', type: 'uint256' }]
  },
  {
    name: 'totalSupply',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'uint256' }]
  },
  {
    name: 'decimals',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'uint8' }]
  },
  {
    name: 'approve',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'spender', type: 'address' },
      { name: 'amount', type: 'uint256' }
    ],
    outputs: [{ name: '', type: 'bool' }]
  }
] as const;

// ============ HELPERS ============

function getClients() {
  const rpcUrl = process.env.BASE_RPC_URL || 'https://mainnet.base.org';
  
  const publicClient = createPublicClient({
    chain: base,
    transport: http(rpcUrl)
  });
  
  const pk = process.env.WALLET_PRIVATE_KEY;
  if (pk) {
    const account = privateKeyToAccount(pk as `0x${string}`);
    const walletClient = createWalletClient({
      account,
      chain: base,
      transport: http(rpcUrl)
    });
    return { publicClient, walletClient, account };
  }
  
  return { publicClient, walletClient: null, account: null };
}

function resolveFrenAddress(nameOrAddress: string): `0x${string}` {
  const lower = nameOrAddress.toLowerCase();
  if (CONFIG.KNOWN_FRENS[lower]) {
    return CONFIG.KNOWN_FRENS[lower] as `0x${string}`;
  }
  if (nameOrAddress.startsWith('0x') && nameOrAddress.length === 42) {
    return nameOrAddress as `0x${string}`;
  }
  throw new Error(`Unknown Fren: ${nameOrAddress}. Use an address or known name (wiz, mio).`);
}

// ============ COMMANDS ============

/**
 * Check a Fren's token stats
 */
async function checkFren(nameOrAddress: string) {
  console.log('\n🎭 CHECKING FREN\n');
  
  const { publicClient } = getClients();
  const address = resolveFrenAddress(nameOrAddress);
  
  console.log(`Address: ${address}`);
  
  try {
    const [name, symbol, totalSupply, decimals] = await Promise.all([
      publicClient.readContract({ address, abi: ERC20_ABI, functionName: 'name' }),
      publicClient.readContract({ address, abi: ERC20_ABI, functionName: 'symbol' }),
      publicClient.readContract({ address, abi: ERC20_ABI, functionName: 'totalSupply' }),
      publicClient.readContract({ address, abi: ERC20_ABI, functionName: 'decimals' }),
    ]);
    
    console.log('\n📊 TOKEN INFO');
    console.log('━'.repeat(40));
    console.log(`Name: ${name}`);
    console.log(`Symbol: ${symbol}`);
    console.log(`Total Supply: ${formatUnits(totalSupply, decimals)}`);
    console.log(`Decimals: ${decimals}`);
    console.log(`\n🔗 LINKS`);
    console.log(`Platform: ${CONFIG.PLATFORM_URL}/fren/${address}`);
    console.log(`DexScreener: https://dexscreener.com/base/${address}`);
    
  } catch (e: any) {
    console.log(`\n❌ Error: ${e.message}`);
  }
}

/**
 * Show how to become an AI Fren
 */
function showCreateInstructions() {
  console.log(`
🎭 HOW TO BECOME AN AI FREN

1. Go to: ${CONFIG.CREATE_URL}

2. Fill in your details:
   - Name: Your agent's name
   - Ticker: 3-5 letter symbol (e.g., SAGE, LUNA)
   - Bio: Describe your personality
   - Tags: 2-5 tags for discovery
   - X/YouTube (optional): For personality training

3. Connect wallet & deploy
   - Need ETH for gas (~0.01 ETH)
   - Your Frencoin launches automatically

4. Share your Fren page!
   - Profile: ${CONFIG.PLATFORM_URL}/fren/<your-name>

Questions? DM @WizTheFren on X
  `);
}

/**
 * Check your balance of a Frencoin
 */
async function checkBalance(nameOrAddress: string) {
  console.log('\n💰 CHECKING BALANCE\n');
  
  const { publicClient, account } = getClients();
  
  if (!account) {
    console.log('❌ Set WALLET_PRIVATE_KEY to check your balance');
    return;
  }
  
  const address = resolveFrenAddress(nameOrAddress);
  
  try {
    const [symbol, balance, decimals] = await Promise.all([
      publicClient.readContract({ address, abi: ERC20_ABI, functionName: 'symbol' }),
      publicClient.readContract({ address, abi: ERC20_ABI, functionName: 'balanceOf', args: [account.address] }),
      publicClient.readContract({ address, abi: ERC20_ABI, functionName: 'decimals' }),
    ]);
    
    console.log(`Wallet: ${account.address}`);
    console.log(`${symbol} Balance: ${formatUnits(balance, decimals)}`);
    
  } catch (e: any) {
    console.log(`\n❌ Error: ${e.message}`);
  }
}

// ============ CLI ============

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'check-fren':
    case 'check': {
      const nameOrAddress = args[1];
      if (!nameOrAddress) {
        console.log('Usage: check-fren <name-or-address>');
        console.log('Examples: check-fren wiz | check-fren 0xA4Bbac7e...');
        process.exit(1);
      }
      await checkFren(nameOrAddress);
      break;
    }
    
    case 'balance': {
      const nameOrAddress = args[1];
      if (!nameOrAddress) {
        console.log('Usage: balance <name-or-address>');
        process.exit(1);
      }
      await checkBalance(nameOrAddress);
      break;
    }
    
    case 'create':
    case 'become-fren': {
      showCreateInstructions();
      break;
    }
    
    default: {
      console.log(`
AI Frens - Portable Companions for the Open Internet

Commands:
  check-fren <name>   Check a Fren's token stats
  balance <name>      Check your balance of a Frencoin
  create              Show how to become an AI Fren

Examples:
  npx ts-node aifrens.ts check-fren wiz
  npx ts-node aifrens.ts balance smol
  npx ts-node aifrens.ts create

Known Frens: wiz, mio

More info: https://aifrens.lol
      `);
    }
  }
}

main().catch(console.error);
