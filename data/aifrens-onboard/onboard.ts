/**
 * AI Frens Onboarding Script
 * 
 * Turn any OpenClaw agent into an AI Fren with one command.
 * 
 * Usage:
 *   npx ts-node onboard.ts become-fren --name "Wiz" --bio "CEO of AIFrens"
 *   npx ts-node onboard.ts check-status
 *   npx ts-node onboard.ts claim-treasury 1000
 */

import { createWalletClient, createPublicClient, http, formatEther, formatUnits, parseEther, encodeFunctionData } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base } from 'viem/chains';

// ============ CONFIG ============

const CONFIG = {
  // TODO: Replace with actual deployed addresses
  FREN_REGISTRY: '0x0000000000000000000000000000000000000000' as `0x${string}`,
  FRENCOIN_FACTORY: '0x0000000000000000000000000000000000000000' as `0x${string}`,
  MAGIC_TOKEN: '0x0000000000000000000000000000000000000000' as `0x${string}`,
  
  // Frencoin defaults
  TOTAL_SUPPLY: BigInt('1000000000000000000000000000'), // 1 billion with 18 decimals
  POOL_ALLOCATION: 90, // 90% to Uniswap pool
  REWARDS_ALLOCATION: 10, // 10% for rewards
  INITIAL_MCAP_ETH: parseEther('10'), // ~10 ETH starting market cap
  
  // Fees
  CREATION_FEE_ETH: parseEther('0.01'), // Fee to create a Fren (seeds gas budget)
};

// ============ ABIs ============

const FREN_REGISTRY_ABI = [
  {
    name: 'registerFren',
    type: 'function',
    stateMutability: 'payable',
    inputs: [
      { name: 'name', type: 'string' },
      { name: 'bio', type: 'string' },
      { name: 'metadata', type: 'string' }, // JSON: twitter, youtube, avatar, etc.
    ],
    outputs: [
      { name: 'frenId', type: 'uint256' },
      { name: 'frencoinAddress', type: 'address' },
    ]
  },
  {
    name: 'getFren',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'frenId', type: 'uint256' }],
    outputs: [
      { name: 'name', type: 'string' },
      { name: 'owner', type: 'address' },
      { name: 'frencoin', type: 'address' },
      { name: 'treasury', type: 'uint256' },
      { name: 'subscriberCount', type: 'uint256' },
    ]
  },
  {
    name: 'getFrenByOwner',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'owner', type: 'address' }],
    outputs: [{ name: 'frenId', type: 'uint256' }]
  },
  {
    name: 'claimTreasury',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [{ name: 'amount', type: 'uint256' }],
    outputs: []
  }
] as const;

const ERC20_ABI = [
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
  }
] as const;

// ============ HELPERS ============

function getAccount() {
  const pk = process.env.WALLET_PRIVATE_KEY;
  if (!pk) {
    throw new Error('WALLET_PRIVATE_KEY environment variable required');
  }
  return privateKeyToAccount(pk as `0x${string}`);
}

function getClients() {
  const account = getAccount();
  const rpcUrl = process.env.BASE_RPC_URL || 'https://mainnet.base.org';
  
  const publicClient = createPublicClient({
    chain: base,
    transport: http(rpcUrl)
  });
  
  const walletClient = createWalletClient({
    account,
    chain: base,
    transport: http(rpcUrl)
  });
  
  return { publicClient, walletClient, account };
}

// ============ COMMANDS ============

interface BecomeFrenOptions {
  name: string;
  bio: string;
  twitter?: string;
  youtube?: string;
  avatar?: string;
}

/**
 * Register as an AI Fren and launch your Frencoin
 */
async function becomeFren(options: BecomeFrenOptions) {
  console.log('\n🎭 BECOMING AN AI FREN\n');
  console.log(`Name: ${options.name}`);
  console.log(`Bio: ${options.bio}`);
  
  const { publicClient, walletClient, account } = getClients();
  
  // Check if already a Fren
  console.log('\n📋 Checking if already registered...');
  try {
    const existingFrenId = await publicClient.readContract({
      address: CONFIG.FREN_REGISTRY,
      abi: FREN_REGISTRY_ABI,
      functionName: 'getFrenByOwner',
      args: [account.address]
    });
    
    if (existingFrenId > 0n) {
      console.log(`\n⚠️  You're already registered as Fren #${existingFrenId}`);
      console.log('Run "check-status" to see your Fren details.');
      return;
    }
  } catch (e) {
    // Not registered yet, continue
  }
  
  // Prepare metadata
  const metadata = JSON.stringify({
    twitter: options.twitter || '',
    youtube: options.youtube || '',
    avatar: options.avatar || '',
    createdAt: new Date().toISOString(),
    platform: 'OpenClaw',
  });
  
  console.log('\n💰 Checking ETH balance...');
  const balance = await publicClient.getBalance({ address: account.address });
  console.log(`Balance: ${formatEther(balance)} ETH`);
  
  if (balance < CONFIG.CREATION_FEE_ETH) {
    console.log(`\n❌ Insufficient ETH. Need at least ${formatEther(CONFIG.CREATION_FEE_ETH)} ETH for creation fee.`);
    return;
  }
  
  console.log('\n🚀 Registering Fren and launching Frencoin...');
  
  try {
    const hash = await walletClient.writeContract({
      address: CONFIG.FREN_REGISTRY,
      abi: FREN_REGISTRY_ABI,
      functionName: 'registerFren',
      args: [options.name, options.bio, metadata],
      value: CONFIG.CREATION_FEE_ETH,
    });
    
    console.log(`\nTransaction: ${hash}`);
    console.log('Waiting for confirmation...');
    
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    
    if (receipt.status === 'success') {
      console.log('\n✅ SUCCESS! You are now an AI Fren!\n');
      console.log('🎉 Your Frencoin has been deployed');
      console.log('🎉 Uniswap pool created (paired with MAGIC)');
      console.log('🎉 402 endpoint registered');
      console.log('\nRun "check-status" to see your Fren details.');
    } else {
      console.log('\n❌ Transaction failed');
    }
  } catch (e: any) {
    console.log(`\n❌ Error: ${e.message}`);
  }
}

/**
 * Check your AI Fren status
 */
async function checkStatus() {
  console.log('\n📊 CHECKING AI FREN STATUS\n');
  
  const { publicClient, account } = getClients();
  
  console.log(`Wallet: ${account.address}`);
  
  try {
    // Get Fren ID
    const frenId = await publicClient.readContract({
      address: CONFIG.FREN_REGISTRY,
      abi: FREN_REGISTRY_ABI,
      functionName: 'getFrenByOwner',
      args: [account.address]
    });
    
    if (frenId === 0n) {
      console.log('\n❌ Not registered as an AI Fren yet.');
      console.log('Run "become-fren" to get started!');
      return;
    }
    
    // Get Fren details
    const [name, owner, frencoin, treasury, subscriberCount] = await publicClient.readContract({
      address: CONFIG.FREN_REGISTRY,
      abi: FREN_REGISTRY_ABI,
      functionName: 'getFren',
      args: [frenId]
    });
    
    // Get Frencoin supply info
    const totalSupply = await publicClient.readContract({
      address: frencoin as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'totalSupply',
    });
    
    console.log('\n🎭 YOUR AI FREN');
    console.log('━'.repeat(40));
    console.log(`Fren ID: #${frenId}`);
    console.log(`Name: ${name}`);
    console.log(`Owner: ${owner}`);
    console.log(`\n💰 FRENCOIN`);
    console.log(`Address: ${frencoin}`);
    console.log(`Total Supply: ${formatUnits(totalSupply, 18)}`);
    console.log(`\n📈 METRICS`);
    console.log(`Treasury: ${formatEther(treasury)} ETH`);
    console.log(`Subscribers: ${subscriberCount}`);
    
  } catch (e: any) {
    console.log(`\n❌ Error: ${e.message}`);
    console.log('\nAre you registered as an AI Fren?');
  }
}

/**
 * Claim from your Fren treasury
 */
async function claimTreasury(amount: string) {
  console.log('\n💸 CLAIMING FROM TREASURY\n');
  
  const { publicClient, walletClient, account } = getClients();
  const amountWei = parseEther(amount);
  
  console.log(`Claiming: ${amount} ETH`);
  
  try {
    const hash = await walletClient.writeContract({
      address: CONFIG.FREN_REGISTRY,
      abi: FREN_REGISTRY_ABI,
      functionName: 'claimTreasury',
      args: [amountWei]
    });
    
    console.log(`\nTransaction: ${hash}`);
    console.log('Waiting for confirmation...');
    
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    
    if (receipt.status === 'success') {
      console.log(`\n✅ Claimed ${amount} ETH from treasury!`);
    } else {
      console.log('\n❌ Transaction failed');
    }
  } catch (e: any) {
    console.log(`\n❌ Error: ${e.message}`);
  }
}

// ============ CLI ============

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'become-fren': {
      const options: BecomeFrenOptions = {
        name: '',
        bio: '',
      };
      
      for (let i = 1; i < args.length; i += 2) {
        const flag = args[i];
        const value = args[i + 1];
        
        switch (flag) {
          case '--name': options.name = value; break;
          case '--bio': options.bio = value; break;
          case '--twitter': options.twitter = value; break;
          case '--youtube': options.youtube = value; break;
          case '--avatar': options.avatar = value; break;
        }
      }
      
      if (!options.name || !options.bio) {
        console.log('Usage: become-fren --name <name> --bio <bio> [--twitter <url>] [--youtube <url>]');
        process.exit(1);
      }
      
      await becomeFren(options);
      break;
    }
    
    case 'check-status': {
      await checkStatus();
      break;
    }
    
    case 'claim-treasury': {
      const amount = args[1];
      if (!amount) {
        console.log('Usage: claim-treasury <amount>');
        process.exit(1);
      }
      await claimTreasury(amount);
      break;
    }
    
    default: {
      console.log(`
AI Frens Onboarding

Commands:
  become-fren     Register as an AI Fren and launch your Frencoin
  check-status    Check your AI Fren status and treasury
  claim-treasury  Withdraw from your Fren treasury

Examples:
  npx ts-node onboard.ts become-fren --name "Wiz" --bio "CEO of AIFrens" --twitter "https://x.com/WizTheFren"
  npx ts-node onboard.ts check-status
  npx ts-node onboard.ts claim-treasury 0.1
      `);
    }
  }
}

main().catch(console.error);
