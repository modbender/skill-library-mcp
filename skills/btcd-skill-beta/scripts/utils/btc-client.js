import * as bitcoin from 'bitcoinjs-lib';
import axios from 'axios';
import { config } from './config.js';
import { logger } from './logger.js';
import { getBTCKeyPair, getBTCNetwork } from './wallet-manager.js';

const nowNodesUrl = config.api.nowNodesBtc;
const MEMPOOL_API = 'https://mempool.space/api';

// Create axios instance with timeout
const axiosInstance = axios.create({
  timeout: 30000 // 30 second timeout
});

export async function getUTXOs(address) {
  // Try mempool.space API first (more reliable)
  try {
    logger.info(`Fetching UTXOs from mempool.space for ${address}...`);
    const response = await axiosInstance.get(`${MEMPOOL_API}/address/${address}/utxo`);
    logger.success(`Found ${response.data.length} UTXOs`);
    return response.data;
  } catch (mempoolError) {
    logger.warning('Mempool API failed, trying NowNodes:', mempoolError.message);

    // Fallback to NowNodes
    try {
      const response = await axiosInstance.get(`${nowNodesUrl}/address/${address}/utxo`);
      return response.data;
    } catch (nowNodesError) {
      logger.error('Both APIs failed to fetch UTXOs');
      logger.error('Mempool error:', mempoolError.message);
      logger.error('NowNodes error:', nowNodesError.message);
      throw new Error('Failed to fetch UTXOs from all available APIs');
    }
  }
}

export async function getTransactionDetails(txId) {
  // Try mempool.space API first
  try {
    const response = await axiosInstance.get(`${MEMPOOL_API}/tx/${txId}`);
    return response.data;
  } catch (mempoolError) {
    logger.warning('Mempool API failed, trying NowNodes:', mempoolError.message);

    // Fallback to NowNodes
    try {
      const response = await axiosInstance.get(`${nowNodesUrl}/tx/${txId}`);
      return response.data;
    } catch (nowNodesError) {
      logger.error('Both APIs failed to fetch transaction');
      throw new Error(`Failed to fetch transaction ${txId} from all available APIs`);
    }
  }
}

export async function getBlock(blockHash) {
  // Try mempool.space API first
  try {
    const response = await axiosInstance.get(`${MEMPOOL_API}/block/${blockHash}`);
    const txIdsResponse = await axiosInstance.get(`${MEMPOOL_API}/block/${blockHash}/txids`);
    return {
      blockInfo: response.data,
      txIds: txIdsResponse.data
    };
  } catch (mempoolError) {
    logger.warning('Mempool API failed, trying NowNodes:', mempoolError.message);

    // Fallback to NowNodes
    try {
      const response = await axiosInstance.get(`${nowNodesUrl}/block/${blockHash}`);
      return {
        blockInfo: response.data,
        txIds: response.data.tx.map(tx => (typeof tx === 'string' ? tx : tx.txid))
      };
    } catch (nowNodesError) {
      logger.error('Both APIs failed to fetch block');
      throw new Error(`Failed to fetch block ${blockHash} from all available APIs`);
    }
  }
}

export async function broadcastTransaction(rawTxHex) {
  logger.info('Broadcasting BTC transaction...');

  // Try mempool.space API first
  try {
    const response = await axiosInstance.post(`${MEMPOOL_API}/tx`, rawTxHex);
    const txId = response.data;
    logger.success('Transaction broadcast successfully via mempool.space!');
    logger.btcTxHash(txId);
    return txId;
  } catch (mempoolError) {
    logger.warning('Mempool API failed, trying NowNodes:', mempoolError.response?.data || mempoolError.message);

    // Fallback to NowNodes
    try {
      const response = await axiosInstance.post(`${nowNodesUrl}/tx`, rawTxHex, {
        headers: { 'Content-Type': 'text/plain' }
      });
      const txId = response.data;
      logger.success('Transaction broadcast successfully via NowNodes!');
      logger.btcTxHash(txId);
      return txId;
    } catch (nowNodesError) {
      logger.error('Failed to broadcast via both APIs');
      logger.error('Mempool error:', mempoolError.response?.data || mempoolError.message);
      logger.error('NowNodes error:', nowNodesError.response?.data || nowNodesError.message);
      throw new Error('Failed to broadcast transaction to all available APIs');
    }
  }
}

export async function estimateFeeRate() {
  try {
    const response = await axiosInstance.get(`${MEMPOOL_API}/v1/fees/recommended`);
    // Use hourFee for ~1 hour confirmation
    const feeRate = response.data.hourFee || response.data.halfHourFee || 20;
    logger.info(`Estimated fee rate: ${feeRate} sats/vB`);
    return Math.ceil(feeRate);
  } catch (error) {
    logger.warning('Failed to estimate fee from mempool.space, using default 20 sats/vB');
    return 20;
  }
}

export async function createAndSignTransaction(toAddress, amountSats, satsPerVB = null) {
  const keyPair = getBTCKeyPair();
  const network = getBTCNetwork();
  const fromAddress = bitcoin.payments.p2wpkh({ pubkey: keyPair.publicKey, network }).address;

  // Get UTXOs
  const utxos = await getUTXOs(fromAddress);
  if (!utxos || utxos.length === 0) {
    throw new Error(`No UTXOs found for address ${fromAddress}`);
  }

  // Get fee rate
  const feeRate = satsPerVB || (await estimateFeeRate());
  logger.info(`Using fee rate: ${feeRate} sats/vB`);

  // Create transaction
  const psbt = new bitcoin.Psbt({ network });

  let totalInput = 0;
  for (const utxo of utxos) {
    // Fetch the full transaction to get the output script
    const txDetails = await getTransactionDetails(utxo.txid);

    // Get scriptPubKey - handle different API response formats
    let scriptPubKey;
    const vout = txDetails.vout[utxo.vout];

    if (vout.scriptpubkey) {
      // mempool.space format
      scriptPubKey = Buffer.from(vout.scriptpubkey, 'hex');
    } else if (vout.scriptPubKey?.hex) {
      // NowNodes format
      scriptPubKey = Buffer.from(vout.scriptPubKey.hex, 'hex');
    } else {
      logger.error('Unknown scriptPubKey format:', JSON.stringify(vout));
      throw new Error('Cannot extract scriptPubKey from transaction output');
    }

    // Get value - handle different formats
    const utxoValue = utxo.value || (vout.value ? Math.floor(vout.value * 100000000) : 0);

    psbt.addInput({
      hash: utxo.txid,
      index: utxo.vout,
      witnessUtxo: {
        script: scriptPubKey,
        value: utxoValue
      }
    });

    totalInput += utxoValue;

    // Use first UTXO for simplicity, or accumulate until we have enough
    if (totalInput >= amountSats + 1000) break; // 1000 sats for fees estimate
  }

  // Add output
  psbt.addOutput({
    address: toAddress,
    value: amountSats
  });

  // Estimate fee
  const estimatedSize = 140 * psbt.txInputs.length + 34 * 2 + 10; // Rough estimate
  const estimatedFee = Math.ceil(estimatedSize * feeRate);

  // Add change output if needed
  const change = totalInput - amountSats - estimatedFee;
  if (change > 546) {
    // Dust threshold
    psbt.addOutput({
      address: fromAddress,
      value: change
    });
  }

  // Sign all inputs
  psbt.signAllInputs(keyPair);
  psbt.finalizeAllInputs();

  const tx = psbt.extractTransaction();
  logger.info('Transaction created:');
  logger.data('  From', fromAddress);
  logger.data('  To', toAddress);
  logger.data('  Amount', `${amountSats} sats`);
  logger.data('  Fee', `${estimatedFee} sats`);
  logger.data('  Total Input', `${totalInput} sats`);
  logger.data('  Change', `${change} sats`);

  return {
    hex: tx.toHex(),
    txId: tx.getId()
  };
}

export async function waitForConfirmations(txId, requiredConfirmations = 3) {
  logger.info(`Waiting for ${requiredConfirmations} confirmations...`);

  let confirmations = 0;
  let currentBlockHeight = null;

  while (confirmations < requiredConfirmations) {
    await new Promise(resolve => setTimeout(resolve, 30000)); // Wait 30 seconds

    try {
      const txDetails = await getTransactionDetails(txId);

      // Handle different API response formats for confirmations
      if (txDetails.confirmations !== undefined) {
        // NowNodes format - direct confirmations field
        confirmations = txDetails.confirmations;
      } else if (txDetails.status) {
        // mempool.space format - calculate from block heights
        if (txDetails.status.confirmed && txDetails.status.block_height) {
          // Get current block height
          if (!currentBlockHeight) {
            try {
              const tipResponse = await axiosInstance.get(`${MEMPOOL_API}/blocks/tip/height`);
              currentBlockHeight = tipResponse.data;
            } catch (e) {
              logger.warning('Could not fetch current block height');
            }
          }

          if (currentBlockHeight) {
            confirmations = currentBlockHeight - txDetails.status.block_height + 1;
          } else {
            // If we can't get current height, assume confirmed = 1 confirmation
            confirmations = txDetails.status.confirmed ? 1 : 0;
          }
        } else {
          confirmations = 0; // Not confirmed yet
        }
      } else {
        confirmations = 0;
      }

      logger.info(`Current confirmations: ${confirmations}/${requiredConfirmations}`);

      // Update current block height periodically
      if (confirmations > 0 && confirmations < requiredConfirmations) {
        try {
          const tipResponse = await axiosInstance.get(`${MEMPOOL_API}/blocks/tip/height`);
          currentBlockHeight = tipResponse.data;
        } catch (e) {
          // Ignore, will retry next loop
        }
      }
    } catch (error) {
      logger.warning('Failed to check confirmations, retrying...', error.message);
    }
  }

  logger.success(`Transaction has ${confirmations} confirmations!`);
  return confirmations;
}
