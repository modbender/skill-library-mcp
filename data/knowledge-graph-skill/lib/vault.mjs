// vault.mjs — Encrypted secret store
// Key file sits inside skill folder for portability

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { randomBytes, createCipheriv, createDecipheriv, pbkdf2Sync } from 'crypto';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = join(__dirname, '..');
const VAULT_PATH = join(SKILL_DIR, 'data', 'vault.enc.json');
const KEY_PATH = join(SKILL_DIR, 'data', '.vault-key');

const ALG = 'aes-256-gcm';
const SALT_LEN = 16;
const IV_LEN = 12;
const TAG_LEN = 16;
const KDF_ITER = 100000;

function getOrCreateKey() {
  if (existsSync(KEY_PATH)) return readFileSync(KEY_PATH, 'utf8').trim();
  const key = randomBytes(32).toString('hex');
  writeFileSync(KEY_PATH, key + '\n', { mode: 0o600 });
  return key;
}

function deriveKey(passphrase, salt) {
  return pbkdf2Sync(passphrase, salt, KDF_ITER, 32, 'sha256');
}

function encrypt(text) {
  const pass = getOrCreateKey();
  const salt = randomBytes(SALT_LEN);
  const key = deriveKey(pass, salt);
  const iv = randomBytes(IV_LEN);
  const cipher = createCipheriv(ALG, key, iv);
  const enc = Buffer.concat([cipher.update(text, 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();
  // salt(16) + iv(12) + tag(16) + ciphertext
  return Buffer.concat([salt, iv, tag, enc]).toString('base64');
}

function decrypt(b64) {
  const pass = getOrCreateKey();
  const buf = Buffer.from(b64, 'base64');
  const salt = buf.subarray(0, SALT_LEN);
  const iv = buf.subarray(SALT_LEN, SALT_LEN + IV_LEN);
  const tag = buf.subarray(SALT_LEN + IV_LEN, SALT_LEN + IV_LEN + TAG_LEN);
  const enc = buf.subarray(SALT_LEN + IV_LEN + TAG_LEN);
  const key = deriveKey(pass, salt);
  const decipher = createDecipheriv(ALG, key, iv);
  decipher.setAuthTag(tag);
  return decipher.update(enc, null, 'utf8') + decipher.final('utf8');
}

function loadVault() {
  if (!existsSync(VAULT_PATH)) return {};
  const raw = JSON.parse(readFileSync(VAULT_PATH, 'utf8'));
  const out = {};
  for (const [k, v] of Object.entries(raw)) {
    try { out[k] = { ...v, value: decrypt(v.value) }; } catch { out[k] = v; }
  }
  return out;
}

function saveVault(entries) {
  const out = {};
  for (const [k, v] of Object.entries(entries)) {
    out[k] = { ...v, value: encrypt(v.value) };
  }
  writeFileSync(VAULT_PATH, JSON.stringify(out, null, 2) + '\n', { mode: 0o600 });
}

export function vaultSet(key, value, note = '') {
  const vault = loadVault();
  vault[key] = { value, note, rotated: new Date().toISOString().slice(0, 10) };
  saveVault(vault);
  return { ok: true, key };
}

export function vaultGet(key) {
  const vault = loadVault();
  if (!vault[key]) return null;
  return vault[key].value;
}

export function vaultList() {
  const vault = loadVault();
  return Object.entries(vault).map(([k, v]) => ({
    key: k, note: v.note || '', rotated: v.rotated || '?'
  }));
}

export function vaultDel(key) {
  const vault = loadVault();
  if (!vault[key]) return { ok: false, msg: 'not found' };
  delete vault[key];
  saveVault(vault);
  return { ok: true };
}
