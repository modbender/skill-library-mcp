import { MerkleTree } from 'merkletreejs';
import crypto from 'crypto';
import axios from 'axios';
import { getTransactionDetails, getBlock } from './btc-client.js';
import { logger } from './logger.js';

function sha256(data) {
  return crypto.createHash('sha256').update(data).digest();
}

function doubleSha256(data) {
  return sha256(sha256(data));
}

function generateMerkleProof(btcTxIds, paymentBtcTxId) {
  const leaf = '0x' + paymentBtcTxId;
  const leaves = btcTxIds.map(tx => '0x' + tx);
  const tree = new MerkleTree(leaves, sha256, {
    isBitcoinTree: true,
    duplicateOdd: false,
    sort: false
  });

  const merkleRoot = tree.getHexRoot();
  const proof = tree.getHexProof(leaf);
  const positions = tree.getProof(leaf).map(p => p.position === 'right');
  const txIndex = btcTxIds.indexOf(paymentBtcTxId);

  logger.info('Merkle proof generated:');
  logger.data('  Root', merkleRoot);
  logger.data('  Tx Index', txIndex);
  logger.data('  Verified', tree.verify(tree.getProof(leaf), leaf, tree.getRoot()));

  return {
    merkleRoot,
    leaf,
    proof,
    positions,
    txIndex
  };
}

export async function generateProofParams(btcTxId, scriptAddress = null) {
  logger.info('Generating ZKP proof parameters...');
  logger.data('Transaction ID', btcTxId);

  // Get transaction details
  const txDetails = await getTransactionDetails(btcTxId);
  if (!txDetails) {
    throw new Error('Failed to get transaction details');
  }

  // Handle different block hash field names
  const blockHash = txDetails.blockhash || txDetails.status?.block_hash;

  if (!blockHash) {
    logger.error('Transaction details:', JSON.stringify(txDetails, null, 2));
    throw new Error('Transaction has not been confirmed in a block yet. Block hash is missing.');
  }

  logger.data('Block Hash', blockHash);

  // Get block information
  const { blockInfo, txIds } = await getBlock(blockHash);
  if (!blockInfo) {
    throw new Error('Failed to get block info');
  }

  logger.data('Block Height', blockInfo.height);
  logger.data('Transactions in block', txIds.length);

  const blockHeight = blockInfo.height;

  // Get raw transaction hex - handle different formats
  let txRawData;
  const txHex = txDetails.hex || '';
  if (!txHex) {
    // mempool.space might require separate endpoint for hex
    logger.info('Fetching raw transaction hex...');
    try {
      const hexResponse = await axios.get(`https://mempool.space/api/tx/${btcTxId}/hex`);
      txRawData = '0x' + hexResponse.data;
    } catch (e) {
      throw new Error(`Failed to get transaction hex data for ${btcTxId}`);
    }
  } else {
    txRawData = '0x' + txHex;
  }

  // Generate Merkle proof
  const { merkleRoot, proof, leaf, positions, txIndex } = generateMerkleProof(txIds, btcTxId);

  // Get UTXOs (parent transactions)
  const utxos = [];
  const txInputs = txDetails.vin || [];

  for (const vin of txInputs) {
    const parentTxId = vin.txid;
    const txData = await getTransactionDetails(parentTxId);
    if (!txData) {
      throw new Error(`Failed to get parent transaction ${parentTxId}`);
    }
    // Handle different hex field names
    const txHex = txData.hex || '';
    if (!txHex) {
      logger.warning(`No hex data for parent transaction ${parentTxId}, fetching raw tx...`);
      // For mempool.space, might need to fetch hex separately
      try {
        const hexResponse = await axios.get(`https://mempool.space/api/tx/${parentTxId}/hex`);
        utxos.push('0x' + hexResponse.data);
      } catch (e) {
        logger.error(`Could not fetch hex for ${parentTxId}`);
        throw new Error(`Failed to get hex data for parent transaction ${parentTxId}`);
      }
    } else {
      utxos.push('0x' + txHex);
    }
  }

  // Try to find script address index in outputs
  let scriptAddressOutputIndex = -1;
  if (scriptAddress) {
    scriptAddressOutputIndex = txDetails.vout.findIndex(vout => {
      // Handle different API formats
      if (vout.scriptPubKey?.addresses?.includes(scriptAddress)) return true;
      if (vout.scriptPubKey?.address === scriptAddress) return true;
      if (vout.scriptpubkey_address === scriptAddress) return true; // mempool.space format
      return false;
    });

    if (scriptAddressOutputIndex === -1) {
      logger.warning(`Script address ${scriptAddress} not found in transaction outputs`);
    } else {
      logger.data('Script address output index', scriptAddressOutputIndex);
    }
  }

  logger.success('Proof parameters generated successfully!');

  return {
    blockHeight,
    txRawData,
    utxos,
    proof,
    merkleRoot,
    leaf,
    positions,
    scriptAddressOutputIndex,
    txIndex
  };
}

export function generatePreImage() {
  // Generate a random 32-byte preimage
  const preImage = crypto.randomBytes(32).toString('hex');
  const preImageHash = sha256(Buffer.from(preImage, 'hex')).toString('hex');

  logger.info('PreImage generated:');
  logger.data('  PreImage', preImage);
  logger.data('  Hash', preImageHash);

  return {
    preImage,
    preImageHash
  };
}
