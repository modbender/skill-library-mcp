#!/usr/bin/env npx tsx
/**
 * Auto-compound: Swap reward tokens to USDC and deposit into vault
 * Usage: npx tsx compound.ts
 */

import {
  loadConfig,
  getClients,
  VAULT_ADDRESS,
  USDC_ADDRESS,
  VAULT_ABI,
  ERC20_ABI,
  formatUSDC,
  verifyContracts,
  waitForTransaction,
  simulateAndWrite,
  logTransaction,
  handleError,
  rateLimitedFetch,
  sleep,
  approveAndVerify,
  getFreshNonce,
} from './config.js';
import { type Address, type Hex, formatUnits } from 'viem';

const WELL_ADDRESS = '0xA88594D404727625A9437C3f886C7643872296AE' as Address;
const MORPHO_ADDRESS = '0xBAa5CC21fd487B8Fcc2F632f3F4E8D37262a0842' as Address;
const ODOS_ROUTER = '0x19cEeAd7105607Cd444F5ad10dd51356436095a1' as Address;
const BASE_CHAIN_ID = 8453;

interface OdosQuoteResponse {
  pathId: string;
  outAmounts: string[];
  gasEstimate: number;
}

interface OdosAssembleResponse {
  transaction: {
    to: string;
    data: string;
    value: string;
    gas: number;
  };
}

async function getTokenBalance(
  publicClient: ReturnType<typeof getClients>['publicClient'],
  token: Address,
  owner: Address
): Promise<bigint> {
  return publicClient.readContract({
    address: token,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: [owner],
  });
}

async function getOdosQuote(
  tokenIn: Address,
  amountIn: bigint,
  tokenOut: Address,
  userAddress: Address
): Promise<OdosQuoteResponse | null> {
  const response = await rateLimitedFetch('https://api.odos.xyz/sor/quote/v2', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chainId: BASE_CHAIN_ID,
      inputTokens: [{ tokenAddress: tokenIn, amount: amountIn.toString() }],
      outputTokens: [{ tokenAddress: tokenOut, proportion: 1 }],
      slippageLimitPercent: 1,
      userAddr: userAddress,
    }),
  });

  if (!response.ok) return null;
  const data = await response.json() as OdosQuoteResponse;
  if (!data.pathId || !Array.isArray(data.outAmounts)) return null;
  return data;
}

async function assembleOdosTransaction(
  pathId: string,
  userAddress: Address
): Promise<OdosAssembleResponse | null> {
  const response = await rateLimitedFetch('https://api.odos.xyz/sor/assemble', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userAddr: userAddress,
      pathId,
      simulate: false,
    }),
  });

  if (!response.ok) return null;
  const data = await response.json() as OdosAssembleResponse;
  if (!data.transaction?.to || !data.transaction?.data) return null;
  return data;
}

async function main() {
  const config = loadConfig();
  const { publicClient, walletClient, account } = getClients(config);

  console.log('🦎 Gekko Yield — Auto-Compound\n');
  console.log(`Wallet: ${account.address}\n`);

  await verifyContracts(publicClient);
  console.log('✅ Contracts verified\n');

  const ethBalance = await publicClient.getBalance({ address: account.address });
  if (ethBalance < BigInt(5e14)) {
    console.error(`❌ Insufficient ETH for gas`);
    console.error(`   Available: ${(Number(ethBalance) / 1e18).toFixed(6)} ETH`);
    process.exit(1);
  }

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📋 Step 1: Swap Rewards to USDC');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  const rewardTokens = [
    { address: WELL_ADDRESS, symbol: 'WELL', decimals: 18 },
    { address: MORPHO_ADDRESS, symbol: 'MORPHO', decimals: 18 },
  ];

  for (const token of rewardTokens) {
    const balance = await getTokenBalance(publicClient, token.address, account.address);
    if (balance <= 0n) continue;

    console.log(`Found ${formatUnits(balance, token.decimals)} ${token.symbol}`);
    const quote = await getOdosQuote(token.address, balance, USDC_ADDRESS, account.address);
    if (!quote) {
      console.log(`  ⚠️  Could not get quote, skipping\n`);
      continue;
    }

    const expectedOut = BigInt(quote.outAmounts[0]);
    console.log(`  Expected output: ${formatUSDC(expectedOut)} USDC`);
    if (expectedOut < 10000n) {
      console.log(`  ⚠️  Output too small (<$0.01), skipping\n`);
      continue;
    }

    const allowance = await publicClient.readContract({
      address: token.address,
      abi: ERC20_ABI,
      functionName: 'allowance',
      args: [account.address, ODOS_ROUTER],
    });

    if (allowance < balance) {
      console.log(`  Approving ${token.symbol}...`);
      try {
        await approveAndVerify(publicClient, walletClient, account, token.address, ODOS_ROUTER, balance, token.symbol);
        console.log(`  ✅ Approved\n`);
      } catch (err) {
        console.log(`  ❌ Approve failed\n`);
        continue;
      }
    }

    const assembled = await assembleOdosTransaction(quote.pathId, account.address);
    if (!assembled) {
      console.log(`  ⚠️  Could not assemble transaction\n`);
      continue;
    }

    console.log(`  Executing swap...`);
    const gasEstimate = BigInt(assembled.transaction.gas);
    const gasWithBuffer = gasEstimate + (gasEstimate * 50n / 100n);
    const nonce = await getFreshNonce(publicClient, account.address);

    try {
      const swapHash = await walletClient.sendTransaction({
        to: assembled.transaction.to as Address,
        data: assembled.transaction.data as Hex,
        value: BigInt(assembled.transaction.value),
        gas: gasWithBuffer,
        nonce,
      });

      const receipt = await waitForTransaction(publicClient, swapHash);
      if (receipt.status === 'success') {
        console.log(`  ✅ Swapped! Tx: ${swapHash}\n`);
      } else {
        console.log(`  ❌ Swap reverted\n`);
      }
    } catch (err) {
      console.log(`  ❌ Swap failed\n`);
    }
  }

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📋 Step 2: Deposit USDC into Vault');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  const usdcBalance = await getTokenBalance(publicClient, USDC_ADDRESS, account.address);
  if (usdcBalance === 0n) {
    console.log('No USDC available to deposit.');
    console.log('\n✅ Compound complete');
    process.exit(0);
  }

  console.log(`USDC available: ${formatUSDC(usdcBalance)} USDC`);

  const vaultAllowance = await publicClient.readContract({
    address: USDC_ADDRESS,
    abi: ERC20_ABI,
    functionName: 'allowance',
    args: [account.address, VAULT_ADDRESS],
  });

  if (vaultAllowance < usdcBalance) {
    console.log('Approving USDC for vault...');
    try {
      await approveAndVerify(publicClient, walletClient, account, USDC_ADDRESS, VAULT_ADDRESS, usdcBalance, 'USDC');
      console.log('✅ Approved!\n');
    } catch (err) {
      handleError(err, 'USDC approve failed');
    }
  }

  console.log(`Depositing ${formatUSDC(usdcBalance)} USDC...`);

  try {
    const depositHash = await simulateAndWrite(publicClient, walletClient, {
      address: VAULT_ADDRESS,
      abi: VAULT_ABI,
      functionName: 'deposit',
      args: [usdcBalance, account.address],
      account,
    });

    const receipt = await waitForTransaction(publicClient, depositHash);
    if (receipt.status === 'success') {
    await sleep(1000);
    const newShares = await publicClient.readContract({
      address: VAULT_ADDRESS,
      abi: VAULT_ABI,
      functionName: 'balanceOf',
      args: [account.address],
    });

    const positionValue = await publicClient.readContract({
      address: VAULT_ADDRESS,
      abi: VAULT_ABI,
      functionName: 'convertToAssets',
      args: [newShares],
    });

    logTransaction('compound', depositHash, {
      deposited: usdcBalance.toString(),
      totalShares: newShares.toString(),
      positionValue: positionValue.toString(),
    });

    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🎉 Auto-Compound Complete!');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`Deposited:         ${formatUSDC(usdcBalance)} USDC`);
    console.log(`Total position:    ${formatUSDC(positionValue)} USDC`);
    console.log(`Total shares:      ${formatUSDC(newShares)} mwUSDC`);
    console.log(`View on BaseScan:  https://basescan.org/tx/${depositHash}`);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      process.exit(0);
    } else {
      handleError(new Error('Transaction reverted'), 'Deposit failed');
    }
  } catch (err) {
    handleError(err, 'Deposit failed');
  }
}

main().catch((err) => handleError(err, 'Compound failed'));
