#!/usr/bin/env node
/**
 * HeySummon Crypto CLI — Olm-inspired E2E encryption
 * 
 * Uses X25519 (Diffie-Hellman) + Ed25519 (signing) + AES-256-GCM
 * 
 * Commands:
 *   keygen [dir]            — Generate keypairs (Ed25519 + X25519)
 *   encrypt <plaintext> <recipientX25519PubPath> <ownSignPrivPath> <ownEncPrivPath> [messageId]
 *   decrypt <payloadJson> <senderX25519PubPath> <senderSignPubPath> <ownEncPrivPath>
 */

import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

const [, , action, ...args] = process.argv;

// === KEYGEN ===
if (action === 'keygen') {
  const dir = args[0] || path.join(process.env.HOME, '.heysummon');
  
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  console.error(`🔑 Generating keypairs in ${dir}...`);

  // Ed25519 (signing)
  const ed = crypto.generateKeyPairSync('ed25519', {
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  fs.writeFileSync(path.join(dir, 'sign_public.pem'), ed.publicKey);
  fs.writeFileSync(path.join(dir, 'sign_private.pem'), ed.privateKey);

  // X25519 (encryption via DH)
  const x = crypto.generateKeyPairSync('x25519', {
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  fs.writeFileSync(path.join(dir, 'encrypt_public.pem'), x.publicKey);
  fs.writeFileSync(path.join(dir, 'encrypt_private.pem'), x.privateKey);

  console.error('✅ Keypairs generated:');
  console.error(`   ${dir}/sign_public.pem`);
  console.error(`   ${dir}/sign_private.pem`);
  console.error(`   ${dir}/encrypt_public.pem`);
  console.error(`   ${dir}/encrypt_private.pem`);
  console.error('');

  // Output public keys as JSON (for API calls)
  console.log(JSON.stringify({
    signPublicKey: ed.publicKey,
    encryptPublicKey: x.publicKey
  }));

  process.exit(0);
}

// === ENCRYPT ===
if (action === 'encrypt') {
  const [plaintext, recipientX25519PubPath, ownSignPrivPath, ownEncPrivPath, messageId] = args;

  if (!plaintext || !recipientX25519PubPath || !ownSignPrivPath || !ownEncPrivPath) {
    console.error('Usage: crypto.mjs encrypt <plaintext> <recipientX25519PubPath> <ownSignPrivPath> <ownEncPrivPath> [messageId]');
    process.exit(1);
  }

  try {
    // Load keys
    const recipientPub = crypto.createPublicKey(fs.readFileSync(recipientX25519PubPath));
    const ownEncPriv = crypto.createPrivateKey(fs.readFileSync(ownEncPrivPath));
    const signPriv = crypto.createPrivateKey(fs.readFileSync(ownSignPrivPath));

    // Diffie-Hellman shared secret
    const sharedSecret = crypto.diffieHellman({
      privateKey: ownEncPriv,
      publicKey: recipientPub
    });

    // Generate or use provided messageId
    const msgId = messageId || crypto.randomUUID();

    // HKDF: derive per-message key (salt = messageId)
    const messageKey = crypto.hkdfSync(
      'sha256',
      sharedSecret,
      msgId,           // salt
      'heysummon-msg',   // info
      32               // key length (AES-256)
    );

    // AES-256-GCM encrypt
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(messageKey), iv);
    const encrypted = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
    const authTag = cipher.getAuthTag();

    // Ed25519 sign the ciphertext (sign what you send)
    const signature = crypto.sign(null, encrypted, signPriv);

    // Output as JSON
    console.log(JSON.stringify({
      ciphertext: encrypted.toString('base64'),
      iv: iv.toString('base64'),
      authTag: authTag.toString('base64'),
      signature: signature.toString('base64'),
      messageId: msgId
    }));

    process.exit(0);
  } catch (err) {
    console.error('❌ Encryption failed:', err.message);
    process.exit(1);
  }
}

// === DECRYPT ===
if (action === 'decrypt') {
  const [payloadJson, senderX25519PubPath, senderSignPubPath, ownEncPrivPath] = args;

  if (!payloadJson || !senderX25519PubPath || !senderSignPubPath || !ownEncPrivPath) {
    console.error('Usage: crypto.mjs decrypt <payloadJson> <senderX25519PubPath> <senderSignPubPath> <ownEncPrivPath>');
    process.exit(1);
  }

  try {
    // Parse payload
    const payload = JSON.parse(payloadJson);
    const { ciphertext, iv, authTag, signature, messageId } = payload;

    if (!ciphertext || !iv || !authTag || !signature || !messageId) {
      throw new Error('Invalid payload: missing required fields (ciphertext, iv, authTag, signature, messageId)');
    }

    // Load keys
    const senderPub = crypto.createPublicKey(fs.readFileSync(senderX25519PubPath));
    const senderSignPub = crypto.createPublicKey(fs.readFileSync(senderSignPubPath));
    const ownPriv = crypto.createPrivateKey(fs.readFileSync(ownEncPrivPath));

    // Verify signature first (Ed25519)
    const ciphertextBuf = Buffer.from(ciphertext, 'base64');
    const valid = crypto.verify(
      null, 
      ciphertextBuf, 
      senderSignPub, 
      Buffer.from(signature, 'base64')
    );

    if (!valid) {
      console.error('❌ SIGNATURE VERIFICATION FAILED');
      process.exit(1);
    }

    // Diffie-Hellman shared secret
    const sharedSecret = crypto.diffieHellman({ 
      privateKey: ownPriv, 
      publicKey: senderPub 
    });

    // HKDF: derive same key
    const messageKey = crypto.hkdfSync(
      'sha256',
      sharedSecret,
      messageId,       // salt
      'heysummon-msg',   // info
      32               // key length
    );

    // AES-256-GCM decrypt
    const decipher = crypto.createDecipheriv(
      'aes-256-gcm', 
      Buffer.from(messageKey), 
      Buffer.from(iv, 'base64')
    );
    decipher.setAuthTag(Buffer.from(authTag, 'base64'));
    
    const plaintext = Buffer.concat([
      decipher.update(ciphertextBuf), 
      decipher.final()
    ]).toString('utf8');

    // Output plaintext
    console.log(plaintext);
    process.exit(0);
  } catch (err) {
    console.error('❌ Decryption failed:', err.message);
    process.exit(1);
  }
}

// Invalid action
console.error('Usage:');
console.error('  crypto.mjs keygen [dir]');
console.error('  crypto.mjs encrypt <plaintext> <recipientX25519PubPath> <ownSignPrivPath> <ownEncPrivPath> [messageId]');
console.error('  crypto.mjs decrypt <payloadJson> <senderX25519PubPath> <senderSignPubPath> <ownEncPrivPath>');
process.exit(1);
