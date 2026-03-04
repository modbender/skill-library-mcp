import test from 'node:test';
import assert from 'node:assert/strict';
import { aggregateVotes, updateReputations } from '../src/policy.mjs';

test('aggregateVotes approve path', () => {
  const a = aggregateVotes([
    { vote: 'YES', reputation_before: 0.8, red_flags: [] },
    { vote: 'YES', reputation_before: 0.7, red_flags: [] },
    { vote: 'NO', reputation_before: 0.1, red_flags: [] }
  ], { approve_threshold: 0.7, method: 'WEIGHTED_APPROVAL_VOTE' });
  assert.equal(a.final_decision, 'APPROVE');
});

test('aggregateVotes hard-block', () => {
  const a = aggregateVotes([
    { vote: 'YES', reputation_before: 0.8, red_flags: [] },
    { vote: 'REWRITE', reputation_before: 0.7, red_flags: ['sensitive_data'] }
  ], { approve_threshold: 0.7, method: 'WEIGHTED_APPROVAL_VOTE' });
  assert.equal(a.hard_block, true);
  assert.equal(a.final_decision, 'BLOCK');
});

test('reputation updates and clamps', () => {
  const personas = [{ persona_id: 'p1', reputation: 0.95 }, { persona_id: 'p2', reputation: 0.06 }];
  const votes = [
    { persona_id: 'p1', vote: 'NO', confidence: 0.9 },
    { persona_id: 'p2', vote: 'APPROVE', confidence: 0.5 }
  ];
  const { updates } = updateReputations(personas, [{ persona_id: 'p1', vote: 'NO', confidence: 0.9 }], 'BLOCK');
  assert.equal(updates[0].reputation_after <= 0.95, true);
});
