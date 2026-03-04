#!/usr/bin/env node

import { logger } from './utils/logger.js';
import { config, validateConfig } from './utils/config.js';
import { initializeWallets, getEVMWallet, getBTCKeyPair } from './utils/wallet-manager.js';
import {
  getOrderContractInstance,
  getERC20Instance,
  waitForTransaction,
  formatUnits,
  parseUnits,
  getOrderData
} from './utils/evm-client.js';
import { requireStep, updateStep, loadState, archiveState } from './utils/state-manager.js';
import { getTransactionDetails } from './utils/btc-client.js';
import * as bitcoin from 'bitcoinjs-lib';
import bip66 from 'bip66';
import prompts from 'prompts';
import BigNumber from 'bignumber.js';

// Convert R|S signature to DER format
function rsSignatureToDer(rs) {
  const rsBuffer = Buffer.from(rs, 'hex');
  if (rsBuffer.length !== 64) {
    throw new Error(`Invalid rs string signature length. Buffer length is ${rsBuffer.length}, expected 64`);
  }

  const toDER = x => {
    let i = x[0] & 0x80 ? 1 : 0;
    if (i) x = Buffer.concat([Buffer.alloc(1), x], x.length + 1);
    else if (x.length > 1 && x[0] === 0x00 && !(x[1] & 0x80)) x = x.slice(1);
    return x;
  };

  const r = toDER(rsBuffer.subarray(0, 32));
  const s = toDER(rsBuffer.subarray(32));

  const derSignature = bip66.encode(r, s);
  return derSignature.toString('hex');
}

async function main() {
  logger.section('Step 06: Repay Loan');

  try {
    validateConfig();
    initializeWallets();

    // Get data from previous steps
    const takeOrderStep = requireStep('01-take-order');
    const lockBtcStep = requireStep('02-lock-btc-collateral');
    const claimStep = requireStep('05-claim-btcd-tokens');

    const orderId = takeOrderStep.orderId;
    const btcTxId = lockBtcStep.btcTxId;

    logger.info('Repaying loan for order:');
    logger.data('Order ID', orderId);

    const wallet = getEVMWallet();
    const btcKeyPair = getBTCKeyPair();

    // Get order data to calculate repayment amount
    const orderData = await getOrderData(config.contracts.loanContract, orderId);
    const lendingAmount = new BigNumber(orderData.lendingAmount.toString());
    const interestRate = new BigNumber(orderData.interestRate.toString());

    // Calculate repayment amount (principal + interest)
    // interestRate is in 1e18 format (e.g., 0.015 = 15000000000000000)
    // Formula: interest = principal * interestRate / 1e18
    const interestAmount = lendingAmount.multipliedBy(interestRate).dividedBy('1000000000000000000');
    const repayAmount = lendingAmount.plus(interestAmount);

    // Calculate percentage for display
    const interestRatePercent = interestRate.dividedBy('1000000000000000000').multipliedBy(100);

    logger.info('Repayment calculation:');
    logger.data('Principal', formatUnits(orderData.lendingAmount, 18) + ' BTCD');
    logger.data('Interest Rate', `${interestRatePercent.toFixed(4)}%`);
    logger.data('Interest', formatUnits(interestAmount.toFixed(0), 18) + ' BTCD');
    logger.data('Total Repayment', formatUnits(repayAmount.toFixed(0), 18) + ' BTCD');

    // Check BTCD balance
    const btcdToken = getERC20Instance(config.contracts.btcdToken);
    const balance = await btcdToken.balanceOf(wallet.address);

    logger.data('Your BTCD Balance', formatUnits(balance, 18));

    if (balance.lt(repayAmount.toFixed(0))) {
      throw new Error('Insufficient BTCD balance for repayment');
    }

    // Check and approve BTCD spending
    const orderContract = getOrderContractInstance(orderId);
    const allowance = await btcdToken.allowance(wallet.address, orderId);

    if (allowance.lt(repayAmount.toFixed(0))) {
      logger.info('Approving BTCD spending...');

      const approveTx = await btcdToken.approve(orderId, repayAmount.toFixed(0));
      await waitForTransaction(approveTx);

      logger.success('BTCD spending approved');
    } else {
      logger.info('BTCD spending already approved');
    }

    // Get the unsigned BTC repayment transaction from contract
    logger.info('Getting repay BTC transaction from contract...');
    const repayBtcNoWitnessTx = await orderContract.getRepayBtcNoWitnessTx();
    const rawBtcTx = repayBtcNoWitnessTx.slice(2); // Remove 0x prefix

    logger.data('Raw BTC TX (hex)', rawBtcTx.substring(0, 100) + '...');

    // Parse and sign the transaction
    const unsignedBtcTx = bitcoin.Transaction.fromHex(rawBtcTx);

    // Get the locked BTC transaction details for value
    const lockedTxDetails = await getTransactionDetails(btcTxId);

    // Find script output index
    let scriptOutputIndex = 0;
    if (lockBtcStep.scriptAddress) {
      scriptOutputIndex = lockedTxDetails.vout.findIndex(v => {
        // Handle different API formats
        if (v.scriptPubKey?.addresses?.includes(lockBtcStep.scriptAddress)) return true;
        if (v.scriptPubKey?.address === lockBtcStep.scriptAddress) return true;
        if (v.scriptpubkey_address === lockBtcStep.scriptAddress) return true;
        return false;
      });
      if (scriptOutputIndex === -1) scriptOutputIndex = 0; // Fallback to first output
    }

    // Get value - handle different API formats
    const vout = lockedTxDetails.vout[scriptOutputIndex];
    let orderSatsValue;

    if (vout.value !== undefined) {
      // Check if value is in BTC (decimal) or satoshis (integer)
      if (vout.value < 1) {
        // Likely BTC (decimal) - convert to sats
        orderSatsValue = Math.floor(vout.value * 100000000);
      } else {
        // Already in satoshis
        orderSatsValue = vout.value;
      }
    } else {
      logger.error('Could not find value in output:', JSON.stringify(vout));
      throw new Error('Could not extract BTC value from locked transaction');
    }

    logger.data('Order BTC Value (sats)', orderSatsValue);

    // Get loan script from order data
    const loanScript = await orderContract.loanScript();
    const scriptBuffer = Buffer.from(loanScript.slice(2), 'hex');

    // Sign with borrower's key
    logger.info('Signing repayment transaction with borrower key...');
    const hashForWitness = unsignedBtcTx.hashForWitnessV0(
      0,
      scriptBuffer,
      orderSatsValue,
      bitcoin.Transaction.SIGHASH_ALL
    );

    const signature = btcKeyPair.sign(hashForWitness);
    const borrowerSignature = rsSignatureToDer(signature.toString('hex'));

    logger.data('Borrower Signature (DER)', borrowerSignature.substring(0, 50) + '...');

    // Confirm before proceeding
    const { confirm } = await prompts({
      type: 'confirm',
      name: 'confirm',
      message: 'Repay loan (this will lock your BTCD until lender unlocks BTC)?',
      initial: true
    });

    if (!confirm) {
      logger.warning('Operation cancelled by user');
      return;
    }

    // Call repay on contract
    logger.info('Calling repay() on contract...');
    const repayTx = await orderContract.repay('0x' + rawBtcTx, '0x' + borrowerSignature);

    logger.info('Transaction sent, waiting for confirmation...');
    const receipt = await waitForTransaction(repayTx);

    logger.success('Loan repaid successfully!');
    logger.data('Transaction Hash', receipt.transactionHash);

    // Save to state
    updateStep('06-repay-loan', {
      orderId: orderId,
      repayAmount: formatUnits(repayAmount.toFixed(0), 18),
      borrowerSignature: borrowerSignature,
      txHash: receipt.transactionHash,
      blockNumber: receipt.blockNumber
    });

    // Archive completed flow state and reset for next run
    const archivePath = archiveState();
    logger.success(`Flow state archived to: ${archivePath}`);
    logger.info('State has been reset — next run will start a fresh flow.');

    logger.info('\nLoan repaid! Waiting for lender to unlock BTC...');
  } catch (error) {
    logger.error('Failed to repay loan:', error.message);
    if (error.error) {
      logger.error('Contract error:', error.error.message);
    }
    process.exit(1);
  }
}

main();
