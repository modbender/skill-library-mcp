#!/usr/bin/env node
const fs = require('fs').promises;
const { createPublicClient, createWalletClient, http, parseEther, encodeFunctionData, erc20Abi } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { monadMainnet, monadTestnet } = require('./monad-chains');

const args = process.argv.slice(2);
const tokenAddress = args.find(a => a.startsWith('0x'));
const amountMON = args.find(a => !a.startsWith('0x') && !a.startsWith('--'));
const slippageBps = args.find(a => a.startsWith('--slippage'))?.split('=')[1] || '100';

if (!tokenAddress || !amountMON) {
  console.error('Usage: node buy-token.js <token-address> <MON-amount> [--slippage=100]');
  console.error('Example: node buy-token.js 0x123...abc 0.15 --slippage=300');
  process.exit(1);
}

const privateKey = process.env.NAD_PRIVATE_KEY || process.env.MONAD_PRIVATE_KEY;
if (!privateKey) {
  console.error('❌ Error: NAD_PRIVATE_KEY or MONAD_PRIVATE_KEY not set');
  process.exit(1);
}

const network = process.env.MONAD_NETWORK || 'mainnet';
const chain = network === 'testnet' ? monadTestnet : monadMainnet;

const CONFIG = {
  mainnet: {
    LENS: '0x7e78A8DE94f21804F7a17F4E8BF9EC2c872187ea',
    BONDING_CURVE_ROUTER: '0x6F6B8F1a20703309951a5127c45B49b1CD981A22',
    DEX_ROUTER: '0x0B79d71AE99528D1dB24A4148b5f4F865cc2b137',
    WMON: '0x3bd359C1119dA7Da1D913D1C4D2B7c461115433A',
  },
  testnet: {
    LENS: '0xB056d79CA5257589692699a46623F901a3BB76f1',
    BONDING_CURVE_ROUTER: '0x865054F0F6A288adaAc30261731361EA7E908003',
    DEX_ROUTER: '0x5D4a4f430cA3B1b2dB86B9cFE48a5316800F5fb2',
    WMON: '0x9B68a67e45E03d5a0e0b6e79F6e6F8f5e0C7b2C8',
  }
};

const config = CONFIG[network];
const rpcUrl = process.env.MONAD_RPC_URL || 'https://monad-mainnet.drpc.org';

const account = privateKeyToAccount(privateKey);
const publicClient = createPublicClient({ chain, transport: http(rpcUrl) });
const walletClient = createWalletClient({ account, chain, transport: http(rpcUrl) });

const lensAbi = [
  { name: 'getAmountOut', type: 'function', stateMutability: 'view',
    inputs: [
      { name: 'token', type: 'address' },
      { name: 'amountIn', type: 'uint256' },
      { name: 'isBuy', type: 'bool' }
    ],
    outputs: [
      { name: 'router', type: 'address' },
      { name: 'amountOut', type: 'uint256' }
    ]
  }
];

const bondingCurveRouterAbi = [
  { name: 'buy', type: 'function',
    inputs: [{
      type: 'tuple',
      components: [
        { name: 'amountOutMin', type: 'uint256' },
        { name: 'token', type: 'address' },
        { name: 'to', type: 'address' },
        { name: 'deadline', type: 'uint256' }
      ]
    }],
    outputs: [{ type: 'uint256' }],
    stateMutability: 'payable'
  }
];

const wmonAbi = [
  { name: 'deposit', type: 'function', inputs: [], outputs: [], stateMutability: 'payable' }
];

const dexRouterAbi = [
  { name: 'swapExactTokensForTokens', type: 'function',
    inputs: [
      { name: 'amountIn', type: 'uint256' },
      { name: 'amountOutMin', type: 'uint256' },
      { name: 'path', type: 'address[]' },
      { name: 'to', type: 'address' },
      { name: 'deadline', type: 'uint256' }
    ],
    outputs: [{ name: 'amounts', type: 'uint256[]' }],
    stateMutability: 'nonpayable'
  }
];

async function main() {
  console.log(`\n🔍 Buying ${amountMON} MON worth of token ${tokenAddress}...`);
  console.log(`   Network: ${network} (${chain.name})`);
  console.log(`   Wallet: ${account.address}`);
  console.log(`   Slippage: ${slippageBps} bps (${Number(slippageBps) / 100}%)\n`);

  const monAmount = parseEther(amountMON);
  console.log('📊 Getting quote from LENS (nad.fun quote contract)...');
  const [router, amountOut] = await publicClient.readContract({
    address: config.LENS,
    abi: lensAbi,
    functionName: 'getAmountOut',
    args: [tokenAddress, monAmount, true]
  });

  console.log(`   Router: ${router}`);
  console.log(`   Expected output: ${amountOut.toString()} tokens`);

  const isBondingCurve = router.toLowerCase() === config.BONDING_CURVE_ROUTER.toLowerCase();
  const isDEX = router.toLowerCase() === config.DEX_ROUTER.toLowerCase();
  if (!isBondingCurve && !isDEX) {
    console.error(`❌ Unknown router: ${router}`);
    process.exit(1);
  }
  console.log(`   Market: ${isBondingCurve ? 'Bonding Curve' : 'DEX'}`);

  const slippage = BigInt(slippageBps);
  const amountOutMin = (amountOut * (10000n - slippage)) / 10000n;
  const deadline = BigInt(Math.floor(Date.now() / 1000) + 300);
  console.log(`   Min output (with slippage): ${amountOutMin.toString()} tokens\n`);

  let hash;
  if (isBondingCurve) {
    console.log('💰 Buying on bonding curve...');
    const callData = encodeFunctionData({
      abi: bondingCurveRouterAbi,
      functionName: 'buy',
      args: [{ amountOutMin, token: tokenAddress, to: account.address, deadline }]
    });
    hash = await walletClient.sendTransaction({
      account, to: router, data: callData, value: monAmount, chain
    });
  } else {
    console.log('💱 Buying on DEX (wrap MON → WMON, then swap)...');
    console.log('   1️⃣ Wrapping MON to WMON...');
    const wrapData = encodeFunctionData({ abi: wmonAbi, functionName: 'deposit', args: [] });
    const wrapTx = await walletClient.sendTransaction({
      account, to: config.WMON, data: wrapData, value: monAmount, chain
    });
    console.log(`   Wrap TX: ${wrapTx}`);
    await publicClient.waitForTransactionReceipt({ hash: wrapTx });
    console.log('   ✅ Wrapped');
    console.log('   2️⃣ Approving DEX router...');
    const approveData = encodeFunctionData({
      abi: erc20Abi, functionName: 'approve', args: [config.DEX_ROUTER, monAmount]
    });
    const approveTx = await walletClient.sendTransaction({
      account, to: config.WMON, data: approveData, chain
    });
    await publicClient.waitForTransactionReceipt({ hash: approveTx });
    console.log('   ✅ Approved');
    console.log('   3️⃣ Swapping WMON for token...');
    const path = [config.WMON, tokenAddress];
    const swapData = encodeFunctionData({
      abi: dexRouterAbi,
      functionName: 'swapExactTokensForTokens',
      args: [monAmount, amountOutMin, path, account.address, deadline]
    });
    hash = await walletClient.sendTransaction({
      account, to: router, data: swapData, chain
    });
  }

  console.log(`   TX submitted: ${hash}`);
  console.log('   Waiting for confirmation...');
  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  console.log(`\n✅ Buy complete! Block: ${receipt.blockNumber}`);
  const balance = await publicClient.readContract({
    address: tokenAddress, abi: erc20Abi, functionName: 'balanceOf', args: [account.address]
  });
  console.log(`   New balance: ${balance.toString()} tokens`);

  if (receipt.status === 'success') {
    try {
      let tokenSymbol = 'UNKNOWN';
      try {
        tokenSymbol = await publicClient.readContract({
          address: tokenAddress, abi: erc20Abi, functionName: 'symbol'
        });
      } catch {}
      await recordEntryPrice(tokenAddress, parseFloat(amountMON), account.address, tokenSymbol);
      console.log(`   ✅ Entry price recorded: ${amountMON} MON`);
    } catch (e) {
      console.log(`   ⚠️  Could not record entry price: ${e.message}`);
    }
  }
  console.log(`\n✅ Done! Explorer: https://explorer.monad.xyz/tx/${hash}\n`);
}

async function recordEntryPrice(tokenAddress, entryValueMON, walletAddress, tokenSymbol) {
  let report = { timestamp: new Date().toISOString(), wallet: walletAddress, cycle: 'buy_record', positionsCount: 0, positions: [], summary: {} };
  try {
    const existing = await fs.readFile(reportPath, 'utf-8');
    report = JSON.parse(existing);
  } catch {}
  const existingIdx = report.positions.findIndex(p => (p.address || '').toLowerCase() === tokenAddress.toLowerCase());
  const position = existingIdx >= 0 ? report.positions[existingIdx] : {
    address: tokenAddress, symbol: tokenSymbol, name: '', balance: 0, balanceOnChain: 0,
    currentValueMON: entryValueMON, entryValueMON: entryValueMON, pnlPercent: 0, dataSource: 'buy_record', updatedAt: new Date().toISOString()
  };
  position.entryValueMON = entryValueMON;
  position.currentValueMON = entryValueMON;
  position.pnlPercent = 0;
  position.symbol = tokenSymbol;
  position.updatedAt = new Date().toISOString();
  if (existingIdx >= 0) report.positions[existingIdx] = position;
  else report.positions.push(position);
  report.timestamp = new Date().toISOString();
  report.wallet = walletAddress;
  report.positionsCount = report.positions.length;
  const dir = require('path').dirname(reportPath);
  await fs.mkdir(dir, { recursive: true }).catch(() => {});
  await fs.writeFile(reportPath, JSON.stringify(report, null, 2), 'utf-8');
}

main().catch(error => {
  console.error('\n❌ Error:', error.message);
  process.exit(1);
});
