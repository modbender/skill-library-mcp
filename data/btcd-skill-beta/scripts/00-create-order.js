#!/usr/bin/env node

import { logger } from './utils/logger.js';
import { config, validateConfig } from './utils/config.js';
import { initializeWallets, getEVMWallet } from './utils/wallet-manager.js';
import {
  getIssuerContractInstance,
  getLoanContractInstance,
  waitForTransaction,
  parseUnits
} from './utils/evm-client.js';
import { loadState, updateStep } from './utils/state-manager.js';
import prompts from 'prompts';

async function main() {
  logger.section('Step 00: Create Order');

  try {
    validateConfig();
    initializeWallets();

    const state = loadState();
    const wallet = getEVMWallet();

    // Get order parameters
    const lendingAmount = config.test.lendingAmount;
    let lendingDays = config.test.lendingDays;

    const ALLOWED_DAYS = [90, 180];
    const MIN_AMOUNT = 10;

    if (parseFloat(lendingAmount) < MIN_AMOUNT) {
      throw new Error(`LENDING_AMOUNT must be at least ${MIN_AMOUNT} BTCD (got ${lendingAmount})`);
    }

    if (!ALLOWED_DAYS.includes(lendingDays)) {
      const closest = ALLOWED_DAYS.reduce((a, b) => Math.abs(b - lendingDays) < Math.abs(a - lendingDays) ? b : a);
      logger.warning(`LENDING_DAYS=${lendingDays} is not valid. Allowed values: ${ALLOWED_DAYS.join(', ')}. Forcing to ${closest}.`);
      lendingDays = closest;
    }

    logger.info('Order parameters:');
    logger.data('Lending Amount', `${lendingAmount} BTCD`);
    logger.data('Duration', `${lendingDays} days`);
    logger.data('Issuer Contract', config.contracts.issuer);

    // Confirm before proceeding
    const { confirm } = await prompts({
      type: 'confirm',
      name: 'confirm',
      message: 'Create order with these parameters?',
      initial: true
    });

    if (!confirm) {
      logger.warning('Operation cancelled by user');
      return;
    }

    // Get issuer contract instance
    const issuerContract = getIssuerContractInstance(config.contracts.issuer);

    // Get loan contract instance (factory) to parse events
    const loanContract = getLoanContractInstance(config.contracts.loanContract);

    // Convert lending amount to contract value (18 decimals for BTCD)
    const contractLendingAmount = parseUnits(lendingAmount, 18);

    logger.info('Creating order...');
    logger.data('Contract Amount', contractLendingAmount.toString());

    // Create order transaction
    const tx = await issuerContract.createOrder(contractLendingAmount, lendingDays);

    logger.info('Transaction sent, waiting for confirmation...');
    const receipt = await waitForTransaction(tx);

    // Parse OrderCreated event to get order ID
    // Note: OrderCreated event is emitted by LoanContract (factory), not Issuer
    let orderId = null;
    for (const log of receipt.logs) {
      try {
        const parsedLog = loanContract.interface.parseLog(log);
        if (parsedLog.name === 'OrderCreated') {
          orderId = parsedLog.args.orderId;
          logger.info('Found OrderCreated event');
          logger.data('  Order Type', parsedLog.args.orderType.toString());
          logger.data('  Collateral', parsedLog.args.collateral.toString());
          logger.data('  Token', parsedLog.args.token);
          logger.data('  Token Amount', parsedLog.args.tokenAmount.toString());
          break;
        }
      } catch (e) {
        // Not the event we're looking for, continue
      }
    }

    if (!orderId) {
      throw new Error('Failed to extract order ID from transaction receipt');
    }

    logger.success('Order created successfully!');
    logger.data('Order ID', orderId);
    logger.data('Transaction Hash', receipt.transactionHash);

    // Save to state
    updateStep('00-create-order', {
      orderId: orderId,
      lendingAmount: lendingAmount,
      lendingDays: lendingDays,
      txHash: receipt.transactionHash,
      blockNumber: receipt.blockNumber
    });

    logger.info('\nNext step: npm run 01-take-order');
  } catch (error) {
    logger.error('Failed to create order:', error.message);
    if (error.error) {
      logger.error('Contract error:', error.error.message);
    }
    process.exit(1);
  }
}

main();
