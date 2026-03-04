import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { handler } from '../src/index.mjs';

function tmpState() {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'persona-gen-'));
  return path.join(d, 'state.json');
}

test('persona-generator writes persona_set artifact and can reuse', async () => {
  const statePath = tmpState();
  const input = {
    board_id: 'board_test',
    task_context: { goal: 'g', audience: 'a', risk_tolerance: 'low', constraints: [], domain: 'ops' },
    n_personas: 4,
    persona_pack: 'founder'
  };

  const first = await handler(input, { statePath });
  assert.equal(Boolean(first.error), false);
  assert.equal(first.personas.length, 4);
  assert.equal(first.board_write.success, true);

  const second = await handler(input, { statePath });
  assert.equal(Boolean(second.error), false);
  assert.equal(second.persona_set_id, first.persona_set_id);
});

test('persona-generator rejects unknown fields (strict schema)', async () => {
  const statePath = tmpState();
  const out = await handler({
    board_id: 'board_test',
    task_context: { goal: 'g', audience: 'a', risk_tolerance: 'low', constraints: [] },
    n_personas: 3,
    unexpected: true
  }, { statePath });
  assert.equal(Boolean(out.error), true);
  assert.equal(out.error.code, 'INVALID_INPUT');
});
