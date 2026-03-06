import crypto from 'node:crypto';

export function sha256(bufOrString) {
  return crypto.createHash('sha256').update(bufOrString).digest();
}

export function leadingZeroBits(buf) {
  let bits = 0;
  for (const b of buf) {
    if (b === 0) {
      bits += 8;
      continue;
    }
    // clz32 counts leading zeros in 32-bit; for 8-bit shift.
    bits += Math.clz32(b) - 24;
    break;
  }
  return bits;
}

export function meetsDifficulty({ nonce, solution, difficulty }) {
  const hash = sha256(`${nonce}:${solution}`);
  return leadingZeroBits(hash) >= difficulty;
}

export async function solvePow({
  nonce,
  difficulty,
  start = 0,
  maxMs = 30_000,
  logEveryMs = 2_000,
  signal,
}) {
  if (!nonce) throw new Error('solvePow: nonce is required');
  if (!Number.isFinite(difficulty) || difficulty < 0) {
    throw new Error('solvePow: difficulty must be a non-negative number');
  }

  const t0 = Date.now();
  let lastLog = t0;
  let i = start;

  while (true) {
    if (signal?.aborted) {
      const err = new Error('PoW solving aborted');
      err.name = 'AbortError';
      throw err;
    }

    const solution = String(i);
    const hash = sha256(`${nonce}:${solution}`);
    if (leadingZeroBits(hash) >= difficulty) {
      return {
        nonce,
        difficulty,
        solution,
        hashHex: hash.toString('hex'),
        tries: i - start + 1,
        elapsedMs: Date.now() - t0,
      };
    }

    i++;

    const now = Date.now();
    if (now - t0 > maxMs) {
      const err = new Error(`PoW solving timed out after ${maxMs}ms (tried ~${i - start} solutions)`);
      err.code = 'POW_TIMEOUT';
      throw err;
    }

    if (now - lastLog >= logEveryMs) {
      const tries = i - start;
      const elapsedSec = (now - t0) / 1000;
      const rate = Math.floor(tries / Math.max(elapsedSec, 0.001));
      // Keep logs minimal; stderr so stdout stays machine-usable.
      console.error(`[moltlog] PoW solving… tries=${tries} elapsed=${elapsedSec.toFixed(1)}s rate~${rate}/s difficulty=${difficulty}`);
      lastLog = now;
    }
  }
}
