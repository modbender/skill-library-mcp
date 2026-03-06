#!/usr/bin/env node

import { logger } from './utils/logger.js';
import { config, validateConfig } from './utils/config.js';
import { initializeWallets } from './utils/wallet-manager.js';
import { getOrderContractInstance, waitForTransaction } from './utils/evm-client.js';
import { requireStep, updateStep } from './utils/state-manager.js';
import { generateProofParams } from './utils/proof-generator.js';
import prompts from 'prompts';

async function main() {
  logger.section('Step 03: Submit BTC Lock Proof');

  try {
    validateConfig();
    initializeWallets();

    // Get data from previous step
    const lockBtcStep = requireStep('02-lock-btc-collateral');
    const orderId = lockBtcStep.orderId;
    const btcTxId = lockBtcStep.btcTxId;
    const scriptAddress = lockBtcStep.scriptAddress;

    logger.info('Submitting proof for:');
    logger.data('Order ID', orderId);
    logger.data('BTC Transaction', btcTxId);

    // Generate proof parameters
    logger.info('Generating ZKP proof parameters...');
    const proofParams = await generateProofParams(btcTxId, scriptAddress);

    logger.info('Proof parameters:');
    logger.data('Block Height', proofParams.blockHeight);
    logger.data('Merkle Root', proofParams.merkleRoot);
    logger.data('TX Index', proofParams.txIndex);
    logger.data('Script Output Index', proofParams.scriptAddressOutputIndex);

    // Confirm before proceeding
    const { confirm } = await prompts({
      type: 'confirm',
      name: 'confirm',
      message: 'Submit proof to contract?',
      initial: true
    });

    if (!confirm) {
      logger.warning('Operation cancelled by user');
      return;
    }

    // Get the order contract instance
    const orderContract = getOrderContractInstance(orderId);

    // Submit proof
    logger.info('Submitting proof to blockchain...');
    const tx = await orderContract.submitToLenderTransferProof(
      proofParams.txRawData,
      proofParams.blockHeight,
      {
        proof: proofParams.proof,
        root: proofParams.merkleRoot,
        leaf: proofParams.leaf,
        flags: proofParams.positions
      },
      proofParams.txIndex
    );

    logger.info('Transaction sent, waiting for confirmation...');
    const receipt = await waitForTransaction(tx);

    logger.success('Proof submitted successfully!');
    logger.data('Transaction Hash', receipt.transactionHash);

    // Save to state
    updateStep('03-submit-btc-proof', {
      orderId: orderId,
      btcTxId: btcTxId,
      blockHeight: proofParams.blockHeight,
      merkleRoot: proofParams.merkleRoot,
      txIndex: proofParams.txIndex,
      txHash: receipt.transactionHash,
      blockNumber: receipt.blockNumber
    });

    logger.info('\nNext step: npm run 04-arbiter-fee (if required) or npm run 05-claim-btcd');
  } catch (error) {
    logger.error('Failed to submit proof:', error.message);
    if (error.error) {
      logger.error('Contract error:', error.error.message);
    }
    process.exit(1);
  }
}

main();
