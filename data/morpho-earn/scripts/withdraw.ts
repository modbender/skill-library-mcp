#!/usr/bin/env npx tsx
/**
 * Withdraw from Moonwell Flagship USDC vault
 * Usage: npx tsx withdraw.ts <amount|all>
 * Examples:
 *   npx tsx withdraw.ts 100   # Withdraw 100 USDC
 *   npx tsx withdraw.ts all   # Withdraw entire position
 */

import {
  loadConfig,
  getClients,
  VAULT_ADDRESS,
  USDC_ADDRESS,
  VAULT_ABI,
  ERC20_ABI,
  formatUSDC,
  parseUSDC,
  isValidUSDCAmount,
  verifyContracts,
  waitForTransaction,
  simulateAndWrite,
  logTransaction,
  handleError,
} from './config.js';

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: npx tsx withdraw.ts <amount|all>');
    console.log('Examples:');
    console.log('  npx tsx withdraw.ts 100   # Withdraw 100 USDC');
    console.log('  npx tsx withdraw.ts all   # Withdraw entire position');
    process.exit(1);
  }
  
  const amountArg = args[0].toLowerCase();
  const withdrawAll = amountArg === 'all';
  
  // Validate amount format if not "all"
  if (!withdrawAll && !isValidUSDCAmount(amountArg)) {
    console.error('❌ Invalid amount format');
    console.error('   Use a number like: 100, 100.50, 1,000.00');
    console.error('   Or use "all" to withdraw entire position');
    process.exit(1);
  }
  
  const config = loadConfig();
  const { publicClient, walletClient, account } = getClients(config);
  
  console.log('🌜🌛 Moonwell Flagship USDC Vault — Withdraw\n');
  console.log(`Wallet: ${account.address}\n`);
  
  // Verify contracts before proceeding
  console.log('🔐 Verifying contracts...');
  try {
    await verifyContracts(publicClient);
    console.log('   ✅ Contracts verified\n');
  } catch (err) {
    handleError(err, 'Contract verification failed');
  }
  
  // Get current position
  const vaultShares = await publicClient.readContract({
    address: VAULT_ADDRESS,
    abi: VAULT_ABI,
    functionName: 'balanceOf',
    args: [account.address],
  });
  
  if (vaultShares === 0n) {
    console.error('❌ No position to withdraw');
    console.error('   You have 0 shares in the vault.');
    process.exit(1);
  }
  
  const currentPositionValue = await publicClient.readContract({
    address: VAULT_ADDRESS,
    abi: VAULT_ABI,
    functionName: 'convertToAssets',
    args: [vaultShares],
  });
  
  console.log(`Current position: ${formatUSDC(currentPositionValue)} USDC (${formatUSDC(vaultShares)} shares)\n`);
  
  // Check ETH for gas
  const ethBalance = await publicClient.getBalance({ address: account.address });
  if (ethBalance < BigInt(1e14)) {
    console.error(`❌ Insufficient ETH for gas`);
    console.error(`   Available: ${(Number(ethBalance) / 1e18).toFixed(6)} ETH`);
    process.exit(1);
  }
  
  let sharesToRedeem: bigint;
  let expectedAssets: bigint;
  
  if (withdrawAll) {
    // Redeem all shares
    sharesToRedeem = vaultShares;
    expectedAssets = await publicClient.readContract({
      address: VAULT_ADDRESS,
      abi: VAULT_ABI,
      functionName: 'previewRedeem',
      args: [sharesToRedeem],
    });
  } else {
    // Withdraw specific amount
    const withdrawAmount = parseUSDC(amountArg);
    
    if (withdrawAmount <= 0n) {
      console.error('❌ Amount must be greater than 0');
      process.exit(1);
    }
    
    if (withdrawAmount > currentPositionValue) {
      console.error(`❌ Withdrawal amount exceeds position`);
      console.error(`   Requested: ${formatUSDC(withdrawAmount)} USDC`);
      console.error(`   Available: ${formatUSDC(currentPositionValue)} USDC`);
      process.exit(1);
    }
    
    // Convert desired assets to shares
    sharesToRedeem = await publicClient.readContract({
      address: VAULT_ADDRESS,
      abi: VAULT_ABI,
      functionName: 'convertToShares',
      args: [withdrawAmount],
    });
    
    expectedAssets = withdrawAmount;
  }
  
  // Get current USDC balance for comparison
  const currentUsdcBalance = await publicClient.readContract({
    address: USDC_ADDRESS,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: [account.address],
  });
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📋 Transaction Preview');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`Redeeming:         ${formatUSDC(sharesToRedeem)} mwUSDC`);
  console.log(`Expected USDC:     ${formatUSDC(expectedAssets)} USDC`);
  console.log(`Shares remaining:  ${formatUSDC(vaultShares - sharesToRedeem)} mwUSDC`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  
  // Execute withdrawal
  console.log('📝 Withdrawing from vault...');
  
  try {
    const redeemHash = await simulateAndWrite(publicClient, walletClient, {
      address: VAULT_ADDRESS,
      abi: VAULT_ABI,
      functionName: 'redeem',
      args: [sharesToRedeem, account.address, account.address],
      account,
    });
    
    console.log(`   Tx: ${redeemHash}`);
    console.log('   Waiting for confirmation...');
    
    const receipt = await waitForTransaction(publicClient, redeemHash);
    
    if (receipt.status === 'success') {
      console.log('   ✅ Withdrawal successful!\n');
      
      // Get updated balances
      const [newUsdcBalance, newShares] = await Promise.all([
        publicClient.readContract({
          address: USDC_ADDRESS,
          abi: ERC20_ABI,
          functionName: 'balanceOf',
          args: [account.address],
        }),
        publicClient.readContract({
          address: VAULT_ADDRESS,
          abi: VAULT_ABI,
          functionName: 'balanceOf',
          args: [account.address],
        }),
      ]);
      
      const usdcReceived = newUsdcBalance - currentUsdcBalance;
      
      logTransaction('withdraw', redeemHash, {
        sharesRedeemed: sharesToRedeem.toString(),
        usdcReceived: usdcReceived.toString(),
        remainingShares: newShares.toString(),
      });
      
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('🎉 Withdrawal Complete!');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log(`USDC received:     ${formatUSDC(usdcReceived)} USDC`);
      console.log(`New USDC balance:  ${formatUSDC(newUsdcBalance)} USDC`);
      console.log(`Remaining shares:  ${formatUSDC(newShares)} mwUSDC`);
      console.log(`View on BaseScan:  https://basescan.org/tx/${redeemHash}`);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      
      if (newShares === 0n) {
        console.log('\n📤 Fully exited from the vault.');
      }
    } else {
      handleError(new Error('Transaction reverted'), 'Withdraw failed');
    }
  } catch (err) {
    handleError(err, 'Withdraw failed');
  }
}

main().catch((err) => handleError(err, 'Withdraw failed'));
