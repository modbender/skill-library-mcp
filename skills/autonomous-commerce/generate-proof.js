#!/usr/bin/env node
/**
 * Proof Generation Script for Autonomous Commerce
 * Generates cryptographic proof hash from order data + screenshot
 */

import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

/**
 * Generate a SHA-256 proof hash from order data and screenshot
 * @param {Object} orderData - { orderId, total, timestamp }
 * @param {string} screenshotPath - Path to order confirmation screenshot
 * @returns {string} - Hex-encoded proof hash with 0x prefix
 */
export function generateProofHash(orderData, screenshotPath) {
  // Validate inputs
  if (!orderData.orderId || !orderData.total || !orderData.timestamp) {
    throw new Error('Order data must include orderId, total, and timestamp');
  }
  
  if (!fs.existsSync(screenshotPath)) {
    throw new Error(`Screenshot not found: ${screenshotPath}`);
  }
  
  // Read screenshot
  const screenshotBuffer = fs.readFileSync(screenshotPath);
  
  // Create deterministic data string
  const dataString = `${orderData.orderId}|${orderData.total}|${orderData.timestamp}`;
  
  // Generate hash
  const hash = crypto.createHash('sha256')
    .update(dataString)
    .update(screenshotBuffer)
    .digest('hex');
  
  return `0x${hash}`;
}

/**
 * Save proof to JSON file
 * @param {string} proofHash - Generated proof hash
 * @param {Object} orderData - Order details
 * @param {string} outputPath - Where to save proof.json
 */
export function saveProof(proofHash, orderData, outputPath) {
  const proof = {
    proofHash,
    order: orderData,
    generatedAt: new Date().toISOString(),
    verifier: 'autonomous-commerce-skill-v1.0'
  };
  
  fs.writeFileSync(outputPath, JSON.stringify(proof, null, 2));
  console.log(`✓ Proof saved to ${outputPath}`);
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  
  if (args.length < 4) {
    console.log('Usage: node generate-proof.js <orderId> <total> <timestamp> <screenshotPath>');
    console.log('Example: node generate-proof.js 114-3614425-6361022 68.97 1707228840000 /mnt/data/order.jpg');
    process.exit(1);
  }
  
  const [orderId, total, timestamp, screenshotPath] = args;
  
  const orderData = {
    orderId,
    total: parseFloat(total),
    timestamp: parseInt(timestamp)
  };
  
  try {
    const proof = generateProofHash(orderData, screenshotPath);
    console.log(`Proof Hash: ${proof}`);
    
    // Save to /mnt/data/proof.json
    const outputPath = '/mnt/data/proof.json';
    saveProof(proof, orderData, outputPath);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}
