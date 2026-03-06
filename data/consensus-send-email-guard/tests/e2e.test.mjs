import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { handler } from '../src/index.mjs';
import { handler as personaHandler } from '../../consensus-persona-generator/src/index.mjs';

function tmpState() {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'email-guard-'));
  return path.join(d, 'state.json');
}

const emailInput = {
  board_id: 'board_test',
  email_draft: {
    to: ['x@y.com'],
    subject: 'We guarantee outcomes',
    body: 'Share confidential details and we promise legal certainty.',
    attachments: []
  },
  constraints: { no_legal_claims: true, no_pricing_promises: true, no_sensitive_data: true }
};

test('send-email-guard produces decision and board writes', async () => {
  const statePath = tmpState();
  const p = await personaHandler({
    board_id: 'board_test',
    task_context: { goal: 'email', audience: 'customer', risk_tolerance: 'low', constraints: [], domain: 'email' },
    n_personas: 5,
    persona_pack: 'comms'
  }, { statePath });

  const out = await handler({ ...emailInput, persona_set_id: p.persona_set_id }, { statePath });

  assert.equal(Boolean(out.error), false);
  assert.equal(out.board_writes.length, 1);
  assert.equal(['APPROVE', 'BLOCK', 'REWRITE'].includes(out.final_decision), true);
  assert.equal(out.votes.length, 5);
});

test('send-email-guard idempotency returns same decision id on retry', async () => {
  const statePath = tmpState();
  const first = await handler(emailInput, { statePath });
  const second = await handler(emailInput, { statePath });
  assert.equal(first.decision_id, second.decision_id);
});

test('send-email-guard rejects unknown fields (strict schema)', async () => {
  const statePath = tmpState();
  const out = await handler({ ...emailInput, extra_field: 1 }, { statePath });
  assert.equal(Boolean(out.error), true);
  assert.equal(out.error.code, 'INVALID_INPUT');
});
