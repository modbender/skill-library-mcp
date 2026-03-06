#!/usr/bin/env node

import { logger } from './utils/logger.js';
import { config, validateConfig } from './utils/config.js';
import { initializeWallets } from './utils/wallet-manager.js';
import { getOrderData, formatUnits } from './utils/evm-client.js';
import { requireStep, updateStep, getStep } from './utils/state-manager.js';
import { createAndSignTransaction, broadcastTransaction, waitForConfirmations } from './utils/btc-client.js';

async function main() {
  logger.section('Step 02: Lock BTC Collateral');

  try {
    validateConfig();
    initializeWallets();

    // Get data from previous step
    const takeOrderStep = requireStep('01-take-order');
    const orderId = takeOrderStep.orderId;

    // Check if this step was already partially or fully completed
    const existingStep = getStep('02-lock-btc-collateral');
    if (existingStep?.confirmations >= 3) {
      logger.success('This step was already completed!');
      logger.data('Transaction ID', existingStep.btcTxId);
      logger.data('Confirmations', existingStep.confirmations);
      logger.info('\nNext step: npm run 03-submit-proof');
      return;
    }

    if (existingStep?.btcTxId) {
      logger.warning('Found existing BTC transaction in state — resuming (NOT sending new BTC)');
      logger.data('Transaction ID', existingStep.btcTxId);

      const confirmations = await waitForConfirmations(existingStep.btcTxId, 3);

      updateStep('02-lock-btc-collateral', {
        ...existingStep,
        confirmations: confirmations
      });

      logger.success('BTC locked successfully!');
      logger.info('\nNext step: npm run 03-submit-proof');
      return;
    }

    logger.info('Locking BTC for order:');
    logger.data('Order ID', orderId);

    // Get order details to find script address and collateral amount
    const orderData = await getOrderData(config.contracts.loanContract, orderId);

    if (orderData.status !== 1) {
      throw new Error(`Order status is ${orderData.status}, expected 1 (TAKEN)`);
    }

    const scriptAddress = orderData.lenderBtcAddress;

    // Default to standard (no staking) collateral amount
    const COLLATERAL_NO_DISCOUNT_FACTOR = 1.625;
    const discountedAmountSats = orderData.collateralAmount.toNumber();
    const standardAmountSats = Math.ceil(discountedAmountSats * COLLATERAL_NO_DISCOUNT_FACTOR);

    const collateralAmountSats = standardAmountSats;
    const collateralAmountBTC = (collateralAmountSats / 100000000).toFixed(8);

    logger.info('Collateral amount (standard, no staking discount):');
    logger.data('Amount', `${collateralAmountBTC} BTC (${collateralAmountSats} sats)`);
    logger.data('Script Address', scriptAddress);

    // Create and sign BTC transaction
    logger.info('Creating BTC transaction...');
    const { hex: txHex, txId } = await createAndSignTransaction(scriptAddress, collateralAmountSats);

    logger.data('Transaction ID', txId);
    logger.data('Transaction Size', `${txHex.length / 2} bytes`);

    // Broadcast transaction
    logger.info('Broadcasting transaction...');
    const broadcastedTxId = await broadcastTransaction(txHex);

    if (broadcastedTxId !== txId) {
      logger.warning('Broadcasted TX ID differs from computed TX ID');
      logger.data('Computed', txId);
      logger.data('Broadcasted', broadcastedTxId);
    }

    // Save transaction ID immediately (before waiting for confirmations)
    updateStep('02-lock-btc-collateral', {
      orderId: orderId,
      scriptAddress: scriptAddress,
      btcTxId: broadcastedTxId,
      amountBTC: collateralAmountBTC,
      amountSats: collateralAmountSats,
      confirmations: 0,
      broadcasted: true
    });

    logger.success('Transaction broadcast saved to state!');
    logger.info('Safe to resume if interrupted during confirmation waiting');

    // Wait for confirmations
    logger.info('Waiting for 3 confirmations (this may take ~30 minutes)...');
    const confirmations = await waitForConfirmations(broadcastedTxId, 3);

    logger.success('BTC locked successfully!');

    // Update state with confirmations
    updateStep('02-lock-btc-collateral', {
      orderId: orderId,
      scriptAddress: scriptAddress,
      btcTxId: broadcastedTxId,
      amountBTC: collateralAmountBTC,
      amountSats: collateralAmountSats,
      confirmations: confirmations
    });

    logger.info('\nNext step: npm run 03-submit-proof');
  } catch (error) {
    logger.error('Failed to lock BTC:', error.message);
    process.exit(1);
  }
}

main();
