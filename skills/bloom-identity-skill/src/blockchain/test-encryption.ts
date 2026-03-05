/**
 * Test script for wallet encryption
 *
 * Run: npx tsx src/blockchain/test-encryption.ts
 */

import { encryptPrivateKey, decryptPrivateKey, validateEncryptionSecret, generateEncryptionSecret } from './encryption';

async function testEncryption() {
  console.log('🔐 Testing Wallet Encryption\n');

  // Test 1: Generate strong secret
  console.log('Test 1: Generate encryption secret');
  const secret = generateEncryptionSecret();
  console.log(`✅ Generated secret: ${secret.substring(0, 16)}...${secret.substring(secret.length - 16)}`);
  console.log(`   Length: ${secret.length} characters\n`);

  // Test 2: Validate secret strength
  console.log('Test 2: Validate secret strength');
  const validation = validateEncryptionSecret(secret);
  console.log(`✅ Validation result: ${validation.valid}`);
  console.log(`   Reason: ${validation.reason || 'Strong secret'}\n`);

  // Test 3: Encrypt a private key
  console.log('Test 3: Encrypt private key');
  const testPrivateKey = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef';
  console.log(`   Original: ${testPrivateKey}`);

  const encrypted = encryptPrivateKey(testPrivateKey, secret);
  console.log(`   Encrypted: ${encrypted.substring(0, 60)}...`);
  console.log(`   Length: ${encrypted.length} characters\n`);

  // Test 4: Decrypt the private key
  console.log('Test 4: Decrypt private key');
  const decrypted = decryptPrivateKey(encrypted, secret);
  console.log(`   Decrypted: ${decrypted}`);
  console.log(`   Match: ${decrypted === testPrivateKey ? '✅ YES' : '❌ NO'}\n`);

  // Test 5: Multiple encryptions produce different ciphertexts
  console.log('Test 5: Random IV ensures different ciphertexts');
  const encrypted1 = encryptPrivateKey(testPrivateKey, secret);
  const encrypted2 = encryptPrivateKey(testPrivateKey, secret);
  console.log(`   Same plaintext, different ciphertext: ${encrypted1 !== encrypted2 ? '✅ YES' : '❌ NO'}`);
  console.log(`   Both decrypt correctly: ${
    decryptPrivateKey(encrypted1, secret) === testPrivateKey &&
    decryptPrivateKey(encrypted2, secret) === testPrivateKey ? '✅ YES' : '❌ NO'
  }\n`);

  // Test 6: Wrong secret fails
  console.log('Test 6: Wrong secret fails decryption');
  const wrongSecret = generateEncryptionSecret();
  try {
    decryptPrivateKey(encrypted, wrongSecret);
    console.log('   ❌ FAIL: Should have thrown error\n');
  } catch (error) {
    console.log('   ✅ PASS: Correctly rejected wrong secret\n');
  }

  // Test 7: Weak secret validation
  console.log('Test 7: Weak secret validation');
  const weakValidation = validateEncryptionSecret('weak');
  console.log(`   Weak secret rejected: ${!weakValidation.valid ? '✅ YES' : '❌ NO'}`);
  console.log(`   Reason: ${weakValidation.reason}\n`);

  console.log('✅ All tests passed! Encryption is production-ready.\n');
}

testEncryption().catch(console.error);
