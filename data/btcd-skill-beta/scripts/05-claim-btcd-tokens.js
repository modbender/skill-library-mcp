#!/usr/bin/env node

import { logger } from './utils/logger.js';
import { config, validateConfig } from './utils/config.js';
import { initializeWallets, getEVMWallet } from './utils/wallet-manager.js';
import { getOrderContractInstance, getERC20Instance, waitForTransaction, formatUnits } from './utils/evm-client.js';
import { requireStep, updateStep } from './utils/state-manager.js';
import prompts from 'prompts';

async function main() {
  logger.section('Step 05: Claim BTCD Tokens');

  try {
    validateConfig();
    initializeWallets();

    // Get data from previous steps
    const takeOrderStep = requireStep('01-take-order');
    const orderId = takeOrderStep.orderId;
    const preImage = takeOrderStep.preImage;

    if (!preImage) {
      throw new Error('PreImage not found in state. Cannot claim tokens.');
    }

    logger.info('Claiming BTCD tokens for order:');
    logger.data('Order ID', orderId);

    // Get wallet
    const wallet = getEVMWallet();

    // Check current BTCD balance
    const btcdToken = getERC20Instance(config.contracts.btcdToken);
    const balanceBefore = await btcdToken.balanceOf(wallet.address);

    logger.info('Current BTCD balance:');
    logger.data('Balance', formatUnits(balanceBefore, 18));

    // Confirm before proceeding
    const { confirm } = await prompts({
      type: 'confirm',
      name: 'confirm',
      message: 'Claim BTCD tokens (call borrow)?',
      initial: true
    });

    if (!confirm) {
      logger.warning('Operation cancelled by user');
      return;
    }

    // Get order contract instance for the specific order
    const orderContract = getOrderContractInstance(orderId);

    // Call borrow with preImage
    logger.info('Calling borrow()...');
    logger.data('PreImage', preImage);

    const tx = await orderContract.borrow('0x' + preImage);

    logger.info('Transaction sent, waiting for confirmation...');
    const receipt = await waitForTransaction(tx);

    // Check new balance
    const balanceAfter = await btcdToken.balanceOf(wallet.address);
    const received = balanceAfter.sub(balanceBefore);

    logger.success('BTCD tokens claimed successfully!');
    logger.data('Transaction Hash', receipt.transactionHash);
    logger.data('Tokens Received', formatUnits(received, 18));
    logger.data('New Balance', formatUnits(balanceAfter, 18));

    // Save to state
    updateStep('05-claim-btcd-tokens', {
      orderId: orderId,
      txHash: receipt.transactionHash,
      blockNumber: receipt.blockNumber,
      btcdReceived: formatUnits(received, 18),
      btcdBalance: formatUnits(balanceAfter, 18)
    });

    logger.info('\nBTC collateral is now locked, BTCD tokens are in your wallet');
    logger.info('Next step: npm run 06-repay (when ready to repay and unlock BTC)');
  } catch (error) {
    logger.error('Failed to claim BTCD:', error.message);
    if (error.error) {
      logger.error('Contract error:', error.error.message);
    }
    process.exit(1);
  }
}

main();
