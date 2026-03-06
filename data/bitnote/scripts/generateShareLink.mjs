import { ethers } from 'ethers';
import fs from 'node:fs';
import { pbkdf2Sync, createDecipheriv, webcrypto } from 'node:crypto';
import modAbi from '../abi-mod.json' with { type: 'json' };
import { MOD_ADDR } from './lib/bitnoteCompat.mjs';

function arg(name, fallback = null) {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx >= 0 && process.argv[idx + 1]) return process.argv[idx + 1];
  return process.env[name.toUpperCase()] ?? fallback;
}

const profileName = arg('profile');
let profile = {};
if (profileName) {
  const p = `./profiles/${profileName}.json`;
  if (fs.existsSync(p)) profile = JSON.parse(fs.readFileSync(p, 'utf8'));
}

const senderUsername = arg('username', profile.username);
const senderPassphrase = arg('passphrase', process.env.BITNOTE_PASSPHRASE);
const recipientUsername = arg('recipient');
const noteBody = arg('body');
const noteTitle = arg('title', 'Shared BitNote');
const includeTitle = arg('include-title', '1') === '1';
const rpc = arg('rpc', profile.rpc || 'https://api.avax.network/ext/bc/C/rpc');
const appBase = arg('app-base', 'https://app.bitnote.xyz');

if (!senderUsername || !senderPassphrase || !recipientUsername || !noteBody) {
  console.error('MISSING_REQUIRED_ARGS username/passphrase/recipient/body');
  process.exit(2);
}

function hexToArrayBuffer(hex, bufferType = null) {
  const h = hex.startsWith('0x') ? hex.slice(2) : hex;
  const ret = [];
  for (let i = 0; i < h.length / 2; i++) ret.push(parseInt(h.substr(i * 2, 2), 16));
  return bufferType ? new bufferType(ret) : ret;
}

function bufferToHex(buffer) {
  return [...new Uint8Array(buffer)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

function hexToUrlBase64(hex) {
  let result = '';
  for (let i = 0; i < hex.length; i += 2) result += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
  result = Buffer.from(result, 'binary').toString('base64');
  return result.replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/, '');
}

function decryptMpBlob(hex, passphrase) {
  const b = Buffer.from((hex.startsWith('0x') ? hex.slice(2) : hex), 'hex');
  const iv = b.subarray(0, 12);
  const encTag = b.subarray(12);
  const ciphertext = encTag.subarray(0, encTag.length - 16);
  const tag = encTag.subarray(encTag.length - 16);
  const key = pbkdf2Sync(Buffer.from(passphrase, 'utf8'), iv, 1_000_000, 32, 'sha512');
  const dec = createDecipheriv('aes-256-gcm', key, iv);
  dec.setAuthTag(tag);
  return Buffer.concat([dec.update(ciphertext), dec.final()]);
}

function createAadFromShared(sharedPathAndQueryPrefix) {
  const user1 = sharedPathAndQueryPrefix.match(/\/.*?\//)[0].replace('/', '');
  const user2 = sharedPathAndQueryPrefix.match(/\?su=.*?&/)[0].replace('su=', '').replace('&', '');
  return new TextEncoder().encode(user1 + '_' + user2).buffer;
}

async function compressDeflateRaw(text) {
  if (typeof CompressionStream !== 'undefined') {
    const cs = new CompressionStream('deflate-raw');
    const writer = cs.writable.getWriter();
    writer.write(new TextEncoder().encode(text));
    writer.close();
    const chunks = [];
    const reader = cs.readable.getReader();
    while (true) {
      const result = await reader.read();
      if (result.done) break;
      chunks.push(result.value);
    }
    return (new Uint8Array(chunks.reduce((acc, val) => acc.concat(Array.from(val)), []))).buffer;
  }

  // Fallback for older runtimes (should rarely trigger on modern Node)
  const { deflateRawSync } = await import('node:zlib');
  return deflateRawSync(Buffer.from(text, 'utf8')).buffer;
}

async function ecdhEncryptLikeBitNote(messageText, recipientPubHex, senderPrivPkcs8, aad) {
  const subtle = webcrypto.subtle;
  const msgBuff = await compressDeflateRaw(messageText);

  const importedPriv = await subtle.importKey('pkcs8', senderPrivPkcs8, { name: 'ECDH', namedCurve: 'P-521' }, false, ['deriveKey']);
  const importedPub = await subtle.importKey('raw', hexToArrayBuffer(recipientPubHex, Uint8Array).buffer, { name: 'ECDH', namedCurve: 'P-521' }, true, []);
  const derivedKey = await subtle.deriveKey({ name: 'ECDH', public: importedPub }, importedPriv, { name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt']);

  const iv = webcrypto.getRandomValues(new Uint8Array(12));
  const encryptedBuff = await subtle.encrypt({ name: 'AES-GCM', iv, additionalData: aad }, derivedKey, msgBuff);
  return bufferToHex(iv.buffer) + bufferToHex(encryptedBuff);
}

const provider = new ethers.JsonRpcProvider(rpc);
const mod = new ethers.Contract(MOD_ADDR, modAbi, provider);

const senderAddr = await mod.getAddressLink(ethers.keccak256(ethers.toUtf8Bytes(senderUsername)));
if (senderAddr === ethers.ZeroAddress) {
  console.error('SENDER_USERNAME_NOT_FOUND');
  process.exit(3);
}

const recipientAddr = await mod.getAddressLink(ethers.keccak256(ethers.toUtf8Bytes(recipientUsername)));
if (recipientAddr === ethers.ZeroAddress) {
  console.error('RECIPIENT_USERNAME_NOT_FOUND');
  process.exit(4);
}

const [senderEncEcdhPriv, recipientPubHex] = await Promise.all([
  mod.getPrivString(senderAddr),
  mod.getPubString(recipientAddr),
]);

const senderPrivPkcs8 = decryptMpBlob(senderEncEcdhPriv.toString(), senderPassphrase);
const prefix = `/${encodeURI(recipientUsername)}/?su=${senderUsername}&`;
const aad = createAadFromShared(prefix);

const smHex = await ecdhEncryptLikeBitNote(noteBody, recipientPubHex.toString(), senderPrivPkcs8, aad);
const sm = hexToUrlBase64(smHex);

let shareLink = `${appBase.replace(/\/$/, '')}/${encodeURIComponent(recipientUsername)}/?su=${encodeURIComponent(senderUsername)}&sm=${sm}`;
if (includeTitle) {
  const stHex = await ecdhEncryptLikeBitNote(noteTitle, recipientPubHex.toString(), senderPrivPkcs8, aad);
  const st = hexToUrlBase64(stHex);
  shareLink += `&st=${st}`;
}

console.log('SENDER_USERNAME', senderUsername);
console.log('SENDER_ADDRESS', senderAddr);
console.log('RECIPIENT_USERNAME', recipientUsername);
console.log('RECIPIENT_ADDRESS', recipientAddr);
console.log('SHARE_LINK', shareLink);
