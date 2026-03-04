#!/usr/bin/env npx tsx
// Distribute accumulated USDC from a PaymentRouter

import { getClient, getWalletAddress, getEthBalance } from '../core/client.js';
import { parseArgs, formatCrypto, truncateAddress, formatError } from '../core/utils.js';
import { getConfig, getUsdcAddress } from '../core/config.js';
import { formatUnits, parseUnits } from 'viem';

const ERC20_BALANCE_ABI = [{
  name: 'balanceOf',
  type: 'function',
  stateMutability: 'view',
  inputs: [{ name: 'account', type: 'address' }],
  outputs: [{ name: '', type: 'uint256' }],
}] as const;

const PAYMENT_ROUTER_ABI = [{
  name: 'distribute',
  type: 'function',
  stateMutability: 'nonpayable',
  inputs: [
    { name: 'token', type: 'address' },
    { name: 'amount', type: 'uint256' },
  ],
  outputs: [],
}] as const;

const MIN_ETH_FOR_GAS = 0.0001; // Minimum ETH required for gas

async function main() {
  const { positional, flags } = parseArgs(process.argv.slice(2));

  if (positional.length === 0 || flags.help || flags.h) {
    console.log(`
x402 distribute - Distribute USDC from a PaymentRouter

Usage: x402 distribute <router-address> [options]

Arguments:
  router-address   The PaymentRouter contract address

Options:
  --amount <amt>   Distribute a specific USDC amount (e.g., "10.00"). Defaults to full balance.
  --force          Skip gas balance warning
  --json           Output as JSON
  -h, --help       Show this help

Examples:
  x402 distribute 0x1234...5678
  x402 distribute 0x1234...5678 --amount 5.00
  x402 distribute 0x1234...5678 --force --json
`);
    process.exit(0);
  }

  const config = getConfig();
  const jsonOutput = flags.json === true;
  const force = flags.force === true;
  const specifiedAmount = flags.amount as string | undefined;

  // Validate router address
  const routerAddress = positional[0];
  if (!routerAddress.startsWith('0x') || routerAddress.length !== 42) {
    const msg = 'Invalid router address. Must be a 0x-prefixed 40-character hex string.';
    if (jsonOutput) {
      console.log(JSON.stringify({ success: false, error: msg }));
    } else {
      console.error(`Error: ${msg}`);
    }
    process.exit(1);
  }

  try {
    const client = getClient();
    const walletAddress = getWalletAddress();
    const usdcAddress = getUsdcAddress(config.chainId);
    const routerAddr = routerAddress as `0x${string}`;

    // Read router's USDC balance
    const routerBalance = await client.publicClient.readContract({
      address: usdcAddress,
      abi: ERC20_BALANCE_ABI,
      functionName: 'balanceOf',
      args: [routerAddr],
    });

    const routerBalanceFormatted = formatUnits(routerBalance, 6);

    if (routerBalance === 0n) {
      if (jsonOutput) {
        console.log(JSON.stringify({ success: false, error: 'Router has no USDC balance to distribute' }));
      } else {
        console.log('Router has no USDC balance to distribute.');
      }
      return;
    }

    // Determine amount to distribute
    let distributeAmount: bigint;
    if (specifiedAmount) {
      distributeAmount = parseUnits(specifiedAmount, 6);
      if (distributeAmount > routerBalance) {
        const msg = `Requested amount (${specifiedAmount} USDC) exceeds router balance (${routerBalanceFormatted} USDC)`;
        if (jsonOutput) {
          console.log(JSON.stringify({ success: false, error: msg }));
        } else {
          console.error(`Error: ${msg}`);
        }
        process.exit(1);
      }
    } else {
      distributeAmount = routerBalance;
    }

    // Check ETH for gas
    if (!force) {
      const eth = await getEthBalance();
      const ethNum = parseFloat(eth.formatted);
      if (ethNum < MIN_ETH_FOR_GAS) {
        const msg = `Low ETH balance (${formatCrypto(eth.formatted, 'ETH', 6)}). Need at least ${MIN_ETH_FOR_GAS} ETH for gas. Use --force to skip this check.`;
        if (jsonOutput) {
          console.log(JSON.stringify({ success: false, error: msg }));
        } else {
          console.error(`Warning: ${msg}`);
        }
        process.exit(1);
      }
    }

    const distributeFormatted = formatUnits(distributeAmount, 6);

    if (!jsonOutput) {
      console.log('Distributing USDC from PaymentRouter');
      console.log('====================================');
      console.log('');
      console.log(`Router:  ${routerAddress}`);
      console.log(`Balance: ${formatCrypto(routerBalanceFormatted, 'USDC', 2)}`);
      console.log(`Amount:  ${formatCrypto(distributeFormatted, 'USDC', 2)}`);
      console.log(`Caller:  ${truncateAddress(walletAddress)}`);
      console.log('');
      console.log('Submitting transaction...');
    }

    // Call distribute(token, amount)
    const txHash = await client.walletClient.writeContract({
      address: routerAddr,
      abi: PAYMENT_ROUTER_ABI,
      functionName: 'distribute',
      args: [usdcAddress, distributeAmount],
    });

    if (!jsonOutput) {
      console.log(`TX submitted: ${txHash}`);
      console.log('Waiting for confirmation...');
    }

    // Wait for receipt
    const receipt = await client.publicClient.waitForTransactionReceipt({ hash: txHash });

    const success = receipt.status === 'success';

    if (jsonOutput) {
      console.log(JSON.stringify({
        success,
        routerAddress,
        amount: distributeFormatted,
        amountRaw: distributeAmount.toString(),
        transactionHash: txHash,
        blockNumber: receipt.blockNumber.toString(),
        status: receipt.status,
      }));
      return;
    }

    if (success) {
      console.log('');
      console.log('Distribution successful!');
      console.log(`TX: ${txHash}`);
      console.log(`Block: ${receipt.blockNumber}`);
      console.log(`Distributed: ${formatCrypto(distributeFormatted, 'USDC', 2)}`);
    } else {
      console.error('');
      console.error('Transaction reverted.');
      console.error(`TX: ${txHash}`);
      process.exit(1);
    }

  } catch (error) {
    if (jsonOutput) {
      console.log(JSON.stringify({ success: false, error: formatError(error) }));
    } else {
      console.error('Error:', formatError(error));
    }
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
