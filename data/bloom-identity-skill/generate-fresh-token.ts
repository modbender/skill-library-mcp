/**
 * Generate a fresh auth token with correct JWT_SECRET
 */

import { privateKeyToAccount } from 'viem/accounts';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import * as dotenv from 'dotenv';

// Load .env explicitly
dotenv.config();

const TEST_PRIVATE_KEY = '0x' + crypto.randomBytes(32).toString('hex');

async function generateFreshToken() {
  console.log('\n🎯 Generating Fresh Auth Token\n');
  console.log('═══════════════════════════════════════\n');

  // Check JWT_SECRET
  const jwtSecret = process.env.JWT_SECRET;
  if (!jwtSecret) {
    throw new Error('JWT_SECRET not found in .env');
  }
  console.log('✅ JWT_SECRET loaded:', jwtSecret.substring(0, 10) + '...\n');

  // Create test wallet
  const account = privateKeyToAccount(TEST_PRIVATE_KEY as `0x${string}`);
  const address = account.address;
  console.log('✅ Test wallet created:', address, '\n');

  // Generate token data
  const nonce = crypto.randomUUID();
  const timestamp = Date.now();
  const expiresAt = timestamp + 24 * 60 * 60 * 1000;

  const message = [
    'Bloom Agent Authentication',
    `Address: ${address}`,
    `Nonce: ${nonce}`,
    `Timestamp: ${timestamp}`,
    `Expires: ${expiresAt}`,
    'Scope: read:identity,read:skills,read:wallet',
  ].join('\n');

  console.log('Signing message with wallet...');
  const signature = await account.signMessage({ message });
  console.log('✅ Signature:', signature.substring(0, 20) + '...\n');

  // Include identity metadata in the token
  const identityMetadata = {
    personalityType: 'The Visionary',
    tagline: 'See beyond the hype',
    description: 'You are a forward-thinking builder who sees beyond the hype and focuses on real-world impact.',
    mainCategories: ['Crypto', 'DeFi', 'Web3'],
    subCategories: ['Smart Contracts', 'Layer 2', 'Cross-chain'],
    confidence: 85,
  };

  const payload = {
    type: 'agent',
    version: '1.0',
    address,
    nonce,
    timestamp,
    expiresAt,
    scope: ['read:identity', 'read:skills', 'read:wallet'],
    signature,
    signedMessage: message,
    identity: identityMetadata,  // Add identity data to token
  };

  console.log('Signing JWT with secret:', jwtSecret.substring(0, 10) + '...');
  const token = jwt.sign(payload, jwtSecret, {
    algorithm: 'HS256',
    expiresIn: '24h',
    issuer: 'bloom-protocol',
    audience: 'bloom-dashboard',
  });

  console.log('✅ Token generated!\n');
  console.log('═══════════════════════════════════════\n');
  console.log('🌐 Dashboard URL:\n');
  const dashboardUrl = process.env.DASHBOARD_URL || 'http://localhost:3001';
  console.log(`${dashboardUrl}/dashboard?token=${token}\n`);
  console.log('═══════════════════════════════════════\n');

  // Verify the token can be decoded
  try {
    const decoded = jwt.verify(token, jwtSecret, {
      issuer: 'bloom-protocol',
      audience: 'bloom-dashboard',
      algorithms: ['HS256'],
    });
    console.log('✅ Token self-verification passed\n');
  } catch (error) {
    console.error('❌ Token self-verification failed:', error);
  }
}

generateFreshToken().catch(console.error);
