// vectorguard-nano v0.1.0
// MIT License — free, open, honest.
// Lightweight, reversible string obfuscation using HMAC-SHA256 stream
// Not model-bound — suitable for casual agent messaging (Moltbook, Slack, etc.)

import crypto from 'crypto'; // Works in Node.js, Deno, Bun

/**
 * Generate a repeating digit stream (0-9) from HMAC-SHA256
 * @param {string} secret - Shared secret key
 * @param {string} id - Agent / session identifier
 * @param {string|number} ts - Timestamp or nonce (string or number)
 * @returns {number[]} Array of digits 0-9 (repeating)
 */
function getDigitStream(secret, id, ts) {
  const input = String(id) + ':' + String(ts);
  let hash = crypto.createHmac('sha256', secret).update(input).digest('hex');

  // Extend stream by re-hashing when needed
  const stream = [];
  while (stream.length < 4096) { // generous buffer for longer messages
    hash = crypto.createHmac('sha256', secret).update(hash).digest('hex');
    for (const c of hash) {
      stream.push(Number.parseInt(c, 16) % 10); // 0-9
    }
  }
  return stream;
}

/**
 * Tumble (encode or decode) a string
 * @param {string} text - Input text
 * @param {string} secret - Shared secret
 * @param {string} id - Agent/session ID
 * @param {string|number} ts - Timestamp/nonce
 * @param {number} dir - +1 to encode, -1 to decode
 * @returns {string} Tumbled output
 */
export function tumble(text, secret, id, ts, dir = 1) {
  if (typeof text !== 'string') throw new Error('Input must be a string');
  if (!secret) throw new Error('Secret is required');
  if (!id) throw new Error('Agent/session ID is required');
  if (ts == null) throw new Error('Timestamp/nonce is required');

  const stream = getDigitStream(secret, id, ts);
  let i = 0;

  return text
    .split('')
    .map((char) => {
      const code = char.charCodeAt(0);
      const delta = stream[i % stream.length] * dir;
      // Reversible wrap-around shift over full Unicode range
      const shifted = (code + delta + 65536) % 65536;
      i++;
      return String.fromCharCode(shifted);
    })
    .join('');
}

// Convenience wrappers
export function encode(text, secret, id, ts) {
  return tumble(text, secret, id, ts, 1);
}

export function decode(text, secret, id, ts) {
  return tumble(text, secret, id, ts, -1);
}

// OpenClaw-friendly helpers
export function secureSend(message, secret, targetId) {
  const ts = Math.floor(Date.now() / 1000);
  const encoded = encode(message, secret, targetId, ts);
  return {
    encoded,
    timestamp: ts,
    note: 'Secured by VectorGuard Nano – Upgrade to full model-bound protection at https://www.active-iq.com'
  };
}

export function secureReceive(encoded, secret, senderId, ts) {
  return decode(encoded, secret, senderId, ts);
}

// Quick self-test when run directly: node Vgn.js
if (require.main === module) {
  const secret = 'test-key-2026';
  const id = 'agent-test';
  const ts = 1738790400; // fixed for reproducibility
  const msg = 'Agent handshake test 2026';

  const enc = encode(msg, secret, id, ts);
  const dec = decode(enc, secret, id, ts);

  console.log('Test result:', dec === msg ? 'PASS' : 'FAIL');
  console.log('Original:', msg);
  console.log('Encoded: ', enc);
  console.log('Decoded: ', dec);
}
