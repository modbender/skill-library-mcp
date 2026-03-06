#!/usr/bin/env node
/**
 * FadNote CLI - Create secure self-destructing notes
 * Usage: fadnote [text] or pipe content via stdin
 */

import crypto from 'crypto';
import https from 'https';

const FADNOTE_URL = process.env.FADNOTE_URL || 'https://fadnote.com';
const MAX_SIZE = 1024 * 1024; // 1MB

async function readInput() {
  if (process.argv.length > 2) {
    return process.argv.slice(2).join(' ');
  }
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', chunk => data += chunk);
    process.stdin.on('end', () => resolve(data.trim()));
    process.stdin.on('error', reject);
  });
}

function encrypt(content) {
  const key = crypto.randomBytes(32).toString('base64url');
  const salt = crypto.randomBytes(16);
  const iv = crypto.randomBytes(12);
  const derived = crypto.pbkdf2Sync(Buffer.from(key), salt, 100000, 32, 'sha256');
  const cipher = crypto.createCipheriv('aes-256-gcm', derived, iv);
  const encrypted = Buffer.concat([cipher.update(content, 'utf8'), cipher.final()]);
  const payload = {
    ciphertext: Buffer.concat([encrypted, cipher.getAuthTag()]).toString('base64'),
    iv: iv.toString('base64'),
    salt: salt.toString('base64')
  };
  return { blob: Buffer.from(JSON.stringify(payload)), key };
}

async function post(blob) {
  const url = new URL(FADNOTE_URL);
  const options = {
    hostname: url.hostname,
    port: url.port || 443,
    path: '/n',
    method: 'POST',
    headers: {
      'Content-Type': 'application/octet-stream',
      'X-Note-TTL': '86400',
      'Content-Length': blob.length
    }
  };
  return new Promise((resolve, reject) => {
    const req = https.request(options, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 201) resolve(JSON.parse(data));
        else reject(new Error(`HTTP ${res.statusCode}: ${data}`));
      });
    });
    req.on('error', err => reject(new Error(`Request failed: ${err.message}`)));
    req.write(blob);
    req.end();
  });
}

async function main() {
  try {
    const content = await readInput();
    if (!content) throw new Error('Content is empty');
    if (Buffer.byteLength(content, 'utf8') > MAX_SIZE) throw new Error('Content exceeds 1MB limit');

    const { blob, key } = encrypt(content);
    const result = await post(blob);

    console.log(`${FADNOTE_URL}/n/${result.id}#${key}`);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
