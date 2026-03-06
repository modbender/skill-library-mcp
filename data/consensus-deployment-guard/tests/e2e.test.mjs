import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { handler } from '../src/index.mjs';

const vectors = JSON.parse(fs.readFileSync(new URL('./test-vectors.json', import.meta.url), 'utf8'));
const mkState = () => path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'dep-')), 'state.json');

for (const c of vectors.cases) {
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

    for (const f of c.expected_flags || []) {
      assert.equal(flags.includes(f), true, `missing flag: ${f}`);
    }
  });
}

test('idempotent retry returns same decision_id', async () => {
  const input = vectors.cases.find((c) => c.id === 'DG-010').input;
  const s = mkState();
  const a = await handler(input, { statePath: s });
  const b = await handler(input, { statePath: s });
  assert.equal(a.decision_id, b.decision_id);
});

test('external_agent mode writes only decision artifact', async () => {
  const input = vectors.cases.find((c) => c.id === 'DG-012').input;
  const out = await handler(input, { statePath: mkState() });
  assert.equal(Boolean(out.error), false);
  assert.equal(out.board_writes.length, 1);
  assert.equal(out.board_writes[0].type, 'decision');
});
