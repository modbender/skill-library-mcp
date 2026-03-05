#!/usr/bin/env node
/**
 * Lattice Protocol Test Suite
 * 
 * Tests for identity, signing, and basic protocol operations
 */

import { strict as assert } from 'assert';
import * as ed25519 from '@noble/ed25519';
import fs from 'fs';
import path from 'path';
import os from 'os';

const TEST_DIR = path.join(os.tmpdir(), 'lattice-test-' + Date.now());
const TEST_KEYS_FILE = path.join(TEST_DIR, 'keys.json');

// Mock keys for testing
const mockKeys = {
  did: 'did:key:z6Mktest123',
  username: 'testagent',
  privateKey: 'aabbccdd00112233aabbccdd00112233aabbccdd00112233aabbccdd00112233',
  createdAt: new Date().toISOString()
};

console.log('🧪 Lattice Protocol Test Suite\n');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  ✅ ${name}`);
    passed++;
  } catch (err) {
    console.log(`  ❌ ${name}`);
    console.log(`     ${err.message}`);
    failed++;
  }
}

// Test 1: Ed25519 key generation
test('Ed25519 key generation', async () => {
  const privateKey = ed25519.utils.randomPrivateKey();
  const publicKey = await ed25519.getPublicKeyAsync(privateKey);
  
  assert.equal(privateKey.length, 32, 'Private key should be 32 bytes');
  assert.equal(publicKey.length, 32, 'Public key should be 32 bytes');
});

// Test 2: Ed25519 signing
test('Ed25519 signing and verification', async () => {
  const privateKey = ed25519.utils.randomPrivateKey();
  const publicKey = await ed25519.getPublicKeyAsync(privateKey);
  const message = new TextEncoder().encode('test message');
  
  const signature = await ed25519.signAsync(message, privateKey);
  const isValid = await ed25519.verifyAsync(signature, message, publicKey);
  
  assert.equal(isValid, true, 'Signature should be valid');
});

// Test 3: Signature format
test('Signature format matches protocol spec', async () => {
  const privateKey = Buffer.from(mockKeys.privateKey, 'hex');
  const timestamp = Date.now();
  const method = 'POST';
  const path = '/api/v1/posts';
  const body = JSON.stringify({ content: 'test' });
  
  const message = `${method}:${path}:${timestamp}:${body}`;
  const signature = await ed25519.signAsync(
    new TextEncoder().encode(message),
    privateKey
  );
  
  const signatureB64 = Buffer.from(signature).toString('base64');
  
  // Verify format
  assert.ok(signatureB64.length > 0, 'Signature should not be empty');
  assert.ok(Buffer.from(signatureB64, 'base64').length === 64, 'Signature should be 64 bytes');
});

// Test 4: Configuration directory creation
test('Configuration directory handling', () => {
  fs.mkdirSync(TEST_DIR, { recursive: true });
  assert.ok(fs.existsSync(TEST_DIR), 'Test directory should exist');
  
  // Cleanup
  fs.rmSync(TEST_DIR, { recursive: true, force: true });
  assert.ok(!fs.existsSync(TEST_DIR), 'Test directory should be cleaned up');
});

// Test 5: Keys file permissions (simulated)
test('Keys file format validation', () => {
  const keys = {
    did: 'did:key:z6Mkexample',
    privateKey: 'deadbeef00112233deadbeef00112233deadbeef00112233deadbeef00112233',
    createdAt: new Date().toISOString()
  };
  
  // Verify DID format
  assert.ok(keys.did.startsWith('did:key:'), 'DID should use did:key method');
  
  // Verify private key format
  assert.equal(keys.privateKey.length, 64, 'Private key hex should be 64 chars');
  assert.ok(/^[a-f0-9]+$/.test(keys.privateKey), 'Private key should be hex');
});

// Test 6: Message serialization for signing
test('Request message serialization', () => {
  const testCases = [
    {
      method: 'POST',
      path: '/api/v1/posts',
      timestamp: 1234567890,
      body: '{"content":"hello"}',
      expected: 'POST:/api/v1/posts:1234567890:{"content":"hello"}'
    },
    {
      method: 'GET',
      path: '/api/v1/feed',
      timestamp: 1234567890,
      body: '',
      expected: 'GET:/api/v1/feed:1234567890:'
    }
  ];
  
  for (const tc of testCases) {
    const message = `${tc.method}:${tc.path}:${tc.timestamp}:${tc.body}`;
    assert.equal(message, tc.expected, `Message format should match for ${tc.method}`);
  }
});

// Test 7: Hashtag extraction logic (from lattice-post)
test('Hashtag extraction', () => {
  const content = 'Exploring #MachineLearning and #AI agents! #exciting';
  const hashtags = content.match(/#\w+/g) || [];
  
  assert.ok(hashtags.includes('#MachineLearning'), 'Should extract #MachineLearning');
  assert.ok(hashtags.includes('#AI'), 'Should extract #AI');
  assert.ok(hashtags.includes('#exciting'), 'Should extract #exciting');
  assert.equal(hashtags.length, 3, 'Should extract exactly 3 hashtags');
});

// Test 8: DID validation
test('DID format validation', () => {
  const validDids = [
    'did:key:z6MkhaXg...',
    'did:key:z6MkpJ...'
  ];
  
  const invalidDids = [
    'did:web:example.com',
    'not-a-did',
    '',
    'did:key:'
  ];
  
  for (const did of validDids) {
    assert.ok(did.startsWith('did:key:'), `${did} should be valid did:key`);
  }
  
  for (const did of invalidDids) {
    const isValid = did.startsWith('did:key:') && did.length > 'did:key:'.length;
    assert.ok(!isValid, `${did} should be invalid`);
  }
});

// Summary
console.log('\n' + '='.repeat(40));
console.log(`Results: ${passed} passed, ${failed} failed`);
console.log('='.repeat(40));

process.exit(failed > 0 ? 1 : 0);
