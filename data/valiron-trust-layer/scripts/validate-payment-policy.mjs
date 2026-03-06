#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const fileArg = process.argv[2];
if (!fileArg) {
  console.error('Usage: node scripts/validate-payment-policy.mjs <policy.json>');
  process.exit(1);
}

function resolvePolicyPath(input) {
  if (typeof input !== 'string' || input.trim() === '') throw new Error('empty path');
  if (input.includes('\0')) throw new Error('path contains NUL byte');
  if (path.isAbsolute(input)) throw new Error('absolute paths are not allowed');

  const baseDir = process.cwd();
  const resolved = path.resolve(baseDir, input);
  const relative = path.relative(baseDir, resolved);

  if (relative.startsWith('..') || path.isAbsolute(relative)) {
    throw new Error('path traversal outside working directory is not allowed');
  }
  if (path.extname(resolved).toLowerCase() !== '.json') {
    throw new Error('policy file must be a .json file');
  }

  return resolved;
}

let file;
try {
  file = resolvePolicyPath(fileArg);
} catch (e) {
  console.error(`Invalid policy path: ${e.message}`);
  process.exit(1);
}

const required = [
  'route',
  'authorization',
  'allowedRails',
  'maxAmountPerPayment',
  'maxAmountPerHour',
  'maxAmountPerDay',
  'requireHumanApprovalOver',
  'fallbackMode',
];

const validRoutes = new Set(['prod', 'prod_throttled', 'sandbox', 'sandbox_only']);
const validAuth = new Set(['allow', 'allow_with_limits', 'restricted', 'deny']);
const validRails = new Set(['prod', 'sandbox']);
const validFallback = new Set(['fail-open-guarded', 'fail-closed']);

let data;
try {
  const stat = fs.statSync(file);
  if (!stat.isFile()) throw new Error('policy path must point to a regular file');
  if (stat.size > 1_000_000) throw new Error('policy file too large (max 1MB)');
  data = JSON.parse(fs.readFileSync(file, 'utf8'));
} catch (e) {
  console.error('Invalid policy file or JSON:', e.message);
  process.exit(1);
}

const entries = Array.isArray(data) ? data : [data];
let ok = true;

for (const [i, row] of entries.entries()) {
  for (const key of required) {
    if (!(key in row)) {
      console.error(`Entry ${i}: missing field ${key}`);
      ok = false;
    }
  }

  if (!validRoutes.has(row.route)) {
    console.error(`Entry ${i}: invalid route ${row.route}`);
    ok = false;
  }
  if (!validAuth.has(row.authorization)) {
    console.error(`Entry ${i}: invalid authorization ${row.authorization}`);
    ok = false;
  }

  if (!Array.isArray(row.allowedRails) || row.allowedRails.length === 0 || row.allowedRails.some((r) => !validRails.has(r))) {
    console.error(`Entry ${i}: allowedRails must be non-empty and contain only prod|sandbox`);
    ok = false;
  }

  for (const n of ['maxAmountPerPayment', 'maxAmountPerHour', 'maxAmountPerDay', 'requireHumanApprovalOver']) {
    if (typeof row[n] !== 'number' || row[n] < 0) {
      console.error(`Entry ${i}: ${n} must be a non-negative number`);
      ok = false;
    }
  }

  if (row.route === 'sandbox_only' && row.allowedRails.includes('prod')) {
    console.error(`Entry ${i}: sandbox_only cannot allow prod rail`);
    ok = false;
  }

  if (!validFallback.has(row.fallbackMode)) {
    console.error(`Entry ${i}: invalid fallbackMode ${row.fallbackMode}`);
    ok = false;
  }
}

if (!ok) process.exit(2);
console.log('Payment policy validation OK');
