import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { handler } from '../src/index.mjs';

const vec = JSON.parse(fs.readFileSync(new URL('./test-vectors.json', import.meta.url), 'utf8'));
const mkState = () => path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'perm-')), 'state.json');

for (const c of vec.cases) {
  test(`${c.id} ${c.name}`, async () => {
    const out = await handler(c.input, { statePath: mkState() });

    if (c.expected_error_code) {
      assert.equal(Boolean(out.error), true);
      assert.equal(out.error.code, c.expected_error_code);
      return;
    }

    assert.equal(Boolean(out.error), false);
    assert.equal(out.final_decision, c.expected_decision);

    const flags = [
      ...(out.policy_flags?.hard_flags || []),
      ...(out.policy_flags?.rewrite_flags || [])
    ];

    for (const expectedFlag of c.expected_flags || []) {
      assert.equal(flags.includes(expectedFlag), true, `missing flag: ${expectedFlag}`);
    }
  });
}

test('idempotent retry returns same decision_id', async () => {
  const statePath = mkState();
  const input = vec.cases.find((c) => c.id === 'PE-011').input;
  const a = await handler(input, { statePath });
  const b = await handler(input, { statePath });
  assert.equal(a.decision_id, b.decision_id);
});

test('external_agent mode writes only decision artifact', async () => {
  const input = vec.cases.find((c) => c.id === 'PE-012').input;
  const out = await handler(input, { statePath: mkState() });
  assert.equal(Boolean(out.error), false);
  assert.equal(out.board_writes.length, 1);
  assert.equal(out.board_writes[0].type, 'decision');
});
