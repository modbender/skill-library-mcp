#!/usr/bin/env node

import { logger } from './utils/logger.js';
import { config, validateConfig } from './utils/config.js';
import { initializeWallets, getEVMWallet, getBTCAddress, getBTCPublicKey } from './utils/wallet-manager.js';
import { getOrderContractInstance, waitForTransaction, getOrderData } from './utils/evm-client.js';
import { loadState, updateStep, getStep } from './utils/state-manager.js';
import { generatePreImage } from './utils/proof-generator.js';
import { selectBestArbiter, getArbiterFeesFromOrderContract } from './utils/arbiter-client.js';
import prompts from 'prompts';

async function main() {
  logger.section('Step 01: Take Order');

  try {
    validateConfig();
    initializeWallets();

    const state = loadState();
    const wallet = getEVMWallet();

    // Get order ID from previous step or config
    let orderId = config.test.orderId;
    const createOrderStep = getStep('00-create-order');
    if (createOrderStep?.orderId) {
      orderId = createOrderStep.orderId;
      logger.info('Using order ID from create-order step');
    }

    if (!orderId) {
      throw new Error('No order ID found. Either run 00-create-order or set ORDER_ID in .env');
    }

    logger.info('Taking order:');
    logger.data('Order ID', orderId);
    logger.data('Loan Contract', config.contracts.loanContract);

    // Get order details from the order contract
    const orderData = await getOrderData(config.contracts.loanContract, orderId);

    logger.info('Order details:');
    logger.data('Status', orderData.status);
    logger.data('Lending Amount', orderData.lendingAmount.toString());
    logger.data('Collateral Amount', orderData.collateralAmount.toString());
    logger.data('Interest Rate', orderData.interestRate.toString());
    logger.data('Duration', `${orderData.durationDays.toString()} days`);

    if (orderData.status !== 0) {
      throw new Error(`Order status is ${orderData.status}, expected 0 (CREATED)`);
    }

    // Generate preImage
    const { preImage, preImageHash } = generatePreImage();

    // Get BTC info
    const btcAddress = getBTCAddress();
    const btcPublicKey = getBTCPublicKey();

    logger.info('Taker info:');
    logger.data('BTC Address', btcAddress);
    logger.data('BTC Public Key', btcPublicKey);
    logger.data('PreImage Hash', preImageHash);

    // Get order contract instance early (needed for arbiter fees)
    const orderContract = getOrderContractInstance(orderId);

    // Select arbiter dynamically based on availability and deadline
    logger.info('Selecting arbiter for this order...');
    const arbiterAddress = await selectBestArbiter(orderData.durationDays);

    // Get arbiter fees from the order contract
    const arbiterFees = await getArbiterFeesFromOrderContract(orderContract, arbiterAddress);
    const arbiterEthFee = arbiterFees.ethFee;

    logger.info('Arbiter selected:');
    logger.data('Address', arbiterAddress);
    logger.data('ETH Fee', arbiterFees.ethFee.toString());
    logger.data('BTC Fee', arbiterFees.btcFee.toString());

    // Confirm before proceeding
    const { confirm } = await prompts({
      type: 'confirm',
      name: 'confirm',
      message: 'Take this order?',
      initial: true
    });

    if (!confirm) {
      logger.warning('Operation cancelled by user');
      return;
    }

    logger.info('Taking order...');

    // Take order transaction
    const tx = await orderContract.takeOrder(
      btcAddress,
      '0x' + btcPublicKey,
      '0x' + preImageHash,
      arbiterAddress,
      config.btc.network, // 'mainnet' or 'testnet'
      { value: arbiterEthFee } // Arbiter fee in native coin
    );

    logger.info('Transaction sent, waiting for confirmation...');
    const receipt = await waitForTransaction(tx);

    logger.success('Order taken successfully!');
    logger.data('Transaction Hash', receipt.transactionHash);

    // Save to state
    updateStep('01-take-order', {
      orderId: orderId,
      preImage: preImage,
      preImageHash: preImageHash,
      btcAddress: btcAddress,
      btcPublicKey: btcPublicKey,
      arbiterAddress: arbiterAddress,
      txHash: receipt.transactionHash,
      blockNumber: receipt.blockNumber
    });

    logger.info('\nNext step: npm run 02-lock-btc');
  } catch (error) {
    logger.error('Failed to take order:', error.message);
    if (error.error) {
      logger.error('Contract error:', error.error.message);
    }
    process.exit(1);
  }
}

main();
