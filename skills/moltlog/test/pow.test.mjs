import test from 'node:test';
import assert from 'node:assert/strict';

import { leadingZeroBits, meetsDifficulty, solvePow } from '../src/pow.mjs';

test('leadingZeroBits basic', () => {
  assert.equal(leadingZeroBits(Buffer.from([0x00])), 8);
  assert.equal(leadingZeroBits(Buffer.from([0x00, 0x00])), 16);
  assert.equal(leadingZeroBits(Buffer.from([0x80])), 0);
  assert.equal(leadingZeroBits(Buffer.from([0x40])), 1);
  assert.equal(leadingZeroBits(Buffer.from([0x20])), 2);
});

test('solvePow finds a solution for small difficulty', async () => {
  const nonce = 'unit-test-nonce';
  const difficulty = 10; // expected fast
  const solved = await solvePow({ nonce, difficulty, maxMs: 5_000, logEveryMs: 60_000 });
  assert.ok(solved.solution);
  assert.ok(solved.hashHex);
  assert.ok(meetsDifficulty({ nonce, solution: solved.solution, difficulty }));
});
