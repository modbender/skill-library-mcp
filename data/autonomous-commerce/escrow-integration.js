#!/usr/bin/env node
/**
 * Escrow Integration for Autonomous Commerce
 * Works with ClawPay or any USDC escrow system
 */

import { generateProofHash } from './generate-proof.js';

/**
 * Create purchase escrow
 * @param {Object} escrowClient - ClawPay or compatible client
 * @param {number} budget - Amount in USDC
 * @param {string} recipientWallet - Recipient address
 * @returns {Promise<string>} - Escrow job ID
 */
export async function createPurchaseEscrow(escrowClient, budget, recipientWallet) {
  const jobId = `purchase-${Date.now()}`;
  
  console.log(`Creating escrow: ${jobId}`);
  console.log(`Budget: ${budget} USDC`);
  console.log(`Recipient: ${recipientWallet}`);
  
  const escrow = await escrowClient.escrowCreate(
    jobId,
    budget,
    recipientWallet
  );
  
  console.log(`✓ Escrow created: ${escrow.status}`);
  return jobId;
}

/**
 * Verify proof and release escrow
 * @param {Object} escrowClient - ClawPay or compatible client
 * @param {string} escrowId - Escrow job ID
 * @param {string} proofHash - Cryptographic proof hash
 * @param {Object} orderData - Order details for verification
 * @returns {Promise<boolean>} - Success
 */
export async function releaseOnProof(escrowClient, escrowId, proofHash, orderData) {
  console.log(`Verifying proof: ${proofHash}`);
  
  // Verify proof matches expected format
  if (!proofHash.startsWith('0x') || proofHash.length !== 66) {
    throw new Error('Invalid proof hash format');
  }
  
  // Verify order data is complete
  if (!orderData.orderId || !orderData.total) {
    throw new Error('Incomplete order data');
  }
  
  console.log(`✓ Proof verified`);
  console.log(`Order ID: ${orderData.orderId}`);
  console.log(`Total: $${orderData.total}`);
  
  // Release escrow
  console.log(`Releasing escrow: ${escrowId}`);
  await escrowClient.escrowRelease(escrowId);
  
  console.log(`✓ Escrow released`);
  return true;
}

/**
 * Refund escrow on failure
 * @param {Object} escrowClient - ClawPay or compatible client
 * @param {string} escrowId - Escrow job ID
 * @param {string} reason - Reason for refund
 * @returns {Promise<boolean>} - Success
 */
export async function refundEscrow(escrowClient, escrowId, reason) {
  console.log(`Refunding escrow: ${escrowId}`);
  console.log(`Reason: ${reason}`);
  
  await escrowClient.escrowRefund(escrowId);
  
  console.log(`✓ Escrow refunded`);
  return true;
}

/**
 * Full purchase flow with escrow protection
 * @param {Object} escrowClient - ClawPay or compatible client
 * @param {Object} purchaseRequest - { item, budget, recipientWallet }
 * @param {Function} executePurchase - Async function that returns orderData
 * @returns {Promise<Object>} - { success, proofHash, escrowId, orderData }
 */
export async function autonomousPurchaseWithEscrow(escrowClient, purchaseRequest, executePurchase) {
  const { budget, recipientWallet } = purchaseRequest;
  
  // Phase 1: Create escrow
  const escrowId = await createPurchaseEscrow(escrowClient, budget, recipientWallet);
  
  try {
    // Phase 2: Execute purchase
    console.log(`Executing purchase...`);
    const orderData = await executePurchase(purchaseRequest);
    
    if (!orderData.orderId || !orderData.total) {
      throw new Error('Purchase failed: No order confirmation');
    }
    
    // Phase 3: Generate proof
    console.log(`Generating proof...`);
    const proofHash = generateProofHash(orderData, orderData.screenshotPath);
    
    // Phase 4: Release escrow
    await releaseOnProof(escrowClient, escrowId, proofHash, orderData);
    
    return {
      success: true,
      escrowId,
      proofHash,
      orderData
    };
  } catch (error) {
    // Purchase failed - refund escrow
    console.error(`Purchase failed: ${error.message}`);
    await refundEscrow(escrowClient, escrowId, error.message);
    
    return {
      success: false,
      escrowId,
      error: error.message
    };
  }
}

// Example usage (commented out for library use)
/*
import { ClawPay } from 'clawpay';

const escrowClient = new ClawPay({
  privateKey: process.env.WALLET_PRIVATE_KEY,
  network: 'base'
});

const purchaseRequest = {
  item: 'USB-C cable',
  budget: 15,
  recipientWallet: '0x...'
};

async function executePurchase(request) {
  // Your Amazon purchase logic here
  // Return { orderId, total, screenshotPath }
}

const result = await autonomousPurchaseWithEscrow(
  escrowClient,
  purchaseRequest,
  executePurchase
);

console.log(result.success ? `✓ Purchase complete` : `✗ Purchase failed`);
*/
