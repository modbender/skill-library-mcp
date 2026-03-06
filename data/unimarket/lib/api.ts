import { secp256k1 } from '@noble/curves/secp256k1.js';
import { sha256 } from '@noble/hashes/sha2.js';
import { bytesToHex, hexToBytes } from '@noble/hashes/utils.js';
import { config } from './config.js';

interface SignedHeaders extends Record<string, string> {
  'x-signature': string;
  'x-public-key': string;
  'x-timestamp': string;
  'content-type': string;
}

export function signRequest(body: unknown, privateKeyHex: string): { body: string; headers: SignedHeaders } {
  const timestamp = Date.now();
  const payload = JSON.stringify({ body, timestamp });
  const messageHash = sha256(new TextEncoder().encode(payload));
  const privateKeyBytes = hexToBytes(privateKeyHex);
  const signature = secp256k1.sign(messageHash, privateKeyBytes);
  const publicKey = bytesToHex(secp256k1.getPublicKey(privateKeyBytes, true));

  return {
    body: JSON.stringify(body),
    headers: {
      'x-signature': bytesToHex(signature),
      'x-public-key': publicKey,
      'x-timestamp': String(timestamp),
      'content-type': 'application/json',
    },
  };
}

export async function apiPost(path: string, body: unknown, privateKeyHex: string): Promise<any> {
  const signed = signRequest(body, privateKeyHex);
  const res = await fetch(`${config.serverUrl}${path}`, {
    method: 'POST',
    headers: signed.headers,
    body: signed.body,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error ?? `HTTP ${res.status}`);
  }
  return data;
}

export async function apiGet(path: string, privateKeyHex: string): Promise<any> {
  const signed = signRequest({}, privateKeyHex);
  const res = await fetch(`${config.serverUrl}${path}`, {
    method: 'GET',
    headers: signed.headers,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error ?? `HTTP ${res.status}`);
  }
  return data;
}

export async function apiDelete(path: string, privateKeyHex: string): Promise<any> {
  const signed = signRequest({}, privateKeyHex);
  const res = await fetch(`${config.serverUrl}${path}`, {
    method: 'DELETE',
    headers: signed.headers,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error ?? `HTTP ${res.status}`);
  }
  return data;
}

// Public endpoints (no auth)
export async function apiPublicPost(path: string, body: unknown): Promise<any> {
  const res = await fetch(`${config.serverUrl}${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`);
  return data;
}

export async function apiPublicGet(path: string): Promise<any> {
  const res = await fetch(`${config.serverUrl}${path}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`);
  return data;
}
