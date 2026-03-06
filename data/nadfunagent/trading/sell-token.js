#!/usr/bin/env node

const { ethers } = require('ethers');

// Network configuration for Monad Mainnet (mainnet only)
const CONFIG = {
  CHAIN_ID: 143,
  RPC_URL: 'https://rpc.monad.xyz',
  LENS: '0x7e78A8DE94f21804F7a17F4E8BF9EC2c872187ea',
  BONDING_CURVE_ROUTER: '0x6F6B8F1a20703309951a5127c45B49b1CD981A22',
  DEX_ROUTER: '0x0B79d71AE99528D1dB24A4148b5f4F865cc2b137',
};

// ABIs
const lensAbi = [
  {
    name: 'getAmountOut',
    type: 'function',
    stateMutability: 'view',
    inputs: [
      { name: 'token', type: 'address' },
      { name: 'amount', type: 'uint256' },
      { name: 'isBuy', type: 'bool' }
    ],
    outputs: [
      { name: 'router', type: 'address' },
      { name: 'amountOut', type: 'uint256' }
    ]
  }
];

const routerAbi = [
  {
    name: 'sell',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      {
        name: 'params',
        type: 'tuple',
        components: [
          { name: 'amountIn', type: 'uint256' },
          { name: 'amountOutMin', type: 'uint256' },
          { name: 'token', type: 'address' },
          { name: 'to', type: 'address' },
          { name: 'deadline', type: 'uint256' }
        ]
      }
    ],
    outputs: [{ name: 'amountOut', type: 'uint256' }]
  }
];

const erc20Abi = [
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ type: 'uint256' }]
  },
  {
    name: 'approve',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'spender', type: 'address' },
      { name: 'amount', type: 'uint256' }
    ],
    outputs: [{ type: 'bool' }]
  },
  {
    name: 'symbol',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ type: 'string' }]
  },
  {
    name: 'decimals',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ type: 'uint8' }]
  }
];

async function main() {
  const args = process.argv.slice(2);
  let tokenAddress = null;
  let slippageBps = 100n;
  let sellAll = false;
  let amountToSell = null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--token' && i + 1 < args.length) {
      tokenAddress = args[i + 1];
      i++;
    } else if (args[i] === '--amount' && i + 1 < args.length) {
      if (args[i + 1].toLowerCase() === 'all') {
        sellAll = true;
      } else {
        amountToSell = args[i + 1];
      }
      i++;
    } else if (args[i] === '--slippage' && i + 1 < args.length) {
      slippageBps = BigInt(args[i + 1]);
      i++;
    }
  }

  if (!tokenAddress) {
    console.error('❌ Error: --token required');
    process.exit(1);
  }

  const privateKey = process.env.NAD_PRIVATE_KEY || process.env.MONAD_PRIVATE_KEY;
  if (!privateKey) {
    console.error('❌ Error: NAD_PRIVATE_KEY or MONAD_PRIVATE_KEY not set');
    process.exit(1);
  }

  const rpcUrl = process.env.MONAD_RPC_URL || CONFIG.RPC_URL;
  console.log('\n🔄 Nad.fun Token Sell (mainnet)');
  console.log('='.repeat(50));
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const wallet = new ethers.Wallet(privateKey, provider);
  console.log(`👛 Wallet: ${wallet.address}`);
  console.log(`🪙 Token: ${tokenAddress}`);

  const tokenContract = new ethers.Contract(tokenAddress, erc20Abi, provider);
  let tokenSymbol = 'TOKEN';
  let tokenDecimals = 18;
  try {
    tokenSymbol = await tokenContract.symbol();
    tokenDecimals = await tokenContract.decimals();
    console.log(`📊 Token: ${tokenSymbol} (${tokenDecimals} decimals)`);
  } catch (e) {
    console.log('⚠️  Could not fetch token info, using defaults');
  }

  console.log('\n📊 Step 1: Checking token balance...');
  const balanceBefore = await tokenContract.balanceOf(wallet.address);
  console.log(`Balance: ${ethers.formatUnits(balanceBefore, tokenDecimals)} ${tokenSymbol}`);
  if (balanceBefore === 0n) {
    console.error('❌ Error: No tokens to sell');
    process.exit(1);
  }

  let amountIn;
  if (sellAll) {
    amountIn = balanceBefore;
    console.log(`💰 Selling ALL tokens: ${ethers.formatUnits(amountIn, tokenDecimals)} ${tokenSymbol}`);
  } else if (amountToSell) {
    amountIn = ethers.parseUnits(amountToSell, tokenDecimals);
    console.log(`💰 Selling: ${ethers.formatUnits(amountIn, tokenDecimals)} ${tokenSymbol}`);
  } else {
    amountIn = balanceBefore;
    console.log(`💰 Selling ALL tokens (default): ${ethers.formatUnits(amountIn, tokenDecimals)} ${tokenSymbol}`);
  }
  if (amountIn > balanceBefore) {
    console.error('❌ Error: Insufficient balance');
    process.exit(1);
  }

  console.log('\n💡 Step 2: Getting quote from LENS (nad.fun quote contract)...');
  const lensContract = new ethers.Contract(CONFIG.LENS, lensAbi, provider);
  let router, amountOut;
  try {
    [router, amountOut] = await lensContract.getAmountOut(tokenAddress, amountIn, false);
    console.log(`Router: ${router}`);
    console.log(`Expected MON out: ${ethers.formatEther(amountOut)} MON`);
  } catch (e) {
    console.error('❌ Error getting quote:', e.message);
    process.exit(1);
  }

  const amountOutMin = (amountOut * (10000n - slippageBps)) / 10000n;
  const slippagePercent = Number(slippageBps) / 100;
  console.log(`⚖️  Slippage: ${slippagePercent}% (Min MON: ${ethers.formatEther(amountOutMin)} MON)`);

  console.log('\n✅ Step 3: Approving router...');
  const tokenContractWithSigner = tokenContract.connect(wallet);
  try {
    const approveTx = await tokenContractWithSigner.approve(router, amountIn);
    console.log(`Approve TX: ${approveTx.hash}`);
    await approveTx.wait();
    console.log('✅ Approval confirmed');
  } catch (e) {
    console.error('❌ Error approving:', e.message);
    process.exit(1);
  }

  console.log('\n💸 Step 4: Executing sell...');
  const deadline = BigInt(Math.floor(Date.now() / 1000) + 300);
  const routerContract = new ethers.Contract(router, routerAbi, wallet);
  const sellParams = {
    amountIn: amountIn,
    amountOutMin: amountOutMin,
    token: tokenAddress,
    to: wallet.address,
    deadline: deadline
  };
  try {
    const sellTx = await routerContract.sell(sellParams);
    console.log(`Sell TX: ${sellTx.hash}`);
    console.log(`Explorer: https://explorer.monad.xyz/tx/${sellTx.hash}`);
    const receipt = await sellTx.wait();
    console.log(`✅ Sell confirmed in block ${receipt.blockNumber}`);
  } catch (e) {
    console.error('❌ Error executing sell:', e.message);
    process.exit(1);
  }

  console.log('\n🔍 Step 5: Verifying balance change...');
  const balanceAfter = await tokenContract.balanceOf(wallet.address);
  const balanceChange = balanceBefore - balanceAfter;
  console.log(`Balance Before: ${ethers.formatUnits(balanceBefore, tokenDecimals)} ${tokenSymbol}`);
  console.log(`Balance After: ${ethers.formatUnits(balanceAfter, tokenDecimals)} ${tokenSymbol}`);
  console.log(`Tokens Sold: ${ethers.formatUnits(balanceChange, tokenDecimals)} ${tokenSymbol}`);
  if (balanceChange === 0n) {
    console.error('⚠️  WARNING: Balance did not decrease!');
    process.exit(1);
  }
  console.log('\n✅ Sell completed successfully!');
  console.log('='.repeat(50));
}

main().catch((error) => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
