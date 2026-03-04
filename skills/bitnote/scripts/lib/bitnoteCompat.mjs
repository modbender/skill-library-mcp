import { ethers } from 'ethers';
import { pbkdf2Sync, createDecipheriv, webcrypto } from 'node:crypto';
import { deflateRawSync } from 'node:zlib';

export const MOD_ADDR = '0x225AFdEb639E4cB7A128e348898A02e4730F2F2A';
export const NOTES_ADDR = '0x3B0f15DAB71e3C609EcbB4c99e3AD7EA6532c8c9';

export function hexToBuf(hex) {
  const h = hex.startsWith('0x') ? hex.slice(2) : hex;
  return Buffer.from(h, 'hex');
}

export function decryptMpBlob(hex, passphrase) {
  const b = hexToBuf(hex);
  const iv = b.subarray(0, 12);
  const encTag = b.subarray(12);
  const ciphertext = encTag.subarray(0, encTag.length - 16);
  const tag = encTag.subarray(encTag.length - 16);
  const key = pbkdf2Sync(Buffer.from(passphrase, 'utf8'), iv, 1_000_000, 32, 'sha512');
  const dec = createDecipheriv('aes-256-gcm', key, iv);
  dec.setAuthTag(tag);
  return Buffer.concat([dec.update(ciphertext), dec.final()]);
}

export function buildIdHexFromRequestId(requestId) {
  // 6-byte deterministic id (12 hex chars) to match BitNote timestamp-like width
  return ethers.keccak256(ethers.toUtf8Bytes('bitnote:req:' + requestId)).slice(2, 14);
}

export function makeBitnotePayload(title, body, ecdhPubHex, ecdhPrivPkcs8, idHex) {
  const subtle = webcrypto.subtle;
  return (async () => {
    const plaintext = `${title}${String.fromCodePoint(216)}${body}`;
    const compressed = deflateRawSync(Buffer.from(plaintext, 'utf8'));

    const importedPriv = await subtle.importKey('pkcs8', ecdhPrivPkcs8, { name: 'ECDH', namedCurve: 'P-521' }, true, ['deriveKey']);
    const importedPub = await subtle.importKey('raw', hexToBuf(ecdhPubHex), { name: 'ECDH', namedCurve: 'P-521' }, true, []);
    const derivedKey = await subtle.deriveKey({ name: 'ECDH', public: importedPub }, importedPriv, { name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt']);

    const iv = webcrypto.getRandomValues(new Uint8Array(12));
    const encrypted = new Uint8Array(await subtle.encrypt({ name: 'AES-GCM', iv }, derivedKey, compressed));
    return '0x' + Buffer.concat([Buffer.from(iv), Buffer.from(idHex, 'hex'), Buffer.from(encrypted)]).toString('hex');
  })();
}

export function extractIdHexFromBlob(noteHex) {
  // payload: 12-byte salt/iv + 6-byte id + encrypted
  return noteHex.slice(2 + 24, 2 + 24 + 12).toLowerCase();
}
