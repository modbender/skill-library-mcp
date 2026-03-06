import crypto from 'node:crypto';

const clamp = (n, min, max) => Math.max(min, Math.min(max, n));
const err = (b, c, m, d = {}) => ({ board_id: b, error: { code: c, message: m, details: d } });

function validate(input) {
  if (!input || typeof input !== 'object') return 'input must be object';
  if (!input.board_id || typeof input.board_id !== 'string') return 'board_id required';
  if (!input.decision || typeof input.decision !== 'object') return 'decision required';
  if (!input.vote_batch || typeof input.vote_batch !== 'object') return 'vote_batch required';
  if (!input.persona_set || typeof input.persona_set !== 'object') return 'persona_set required';
  if (!Array.isArray(input.vote_batch.votes)) return 'vote_batch.votes must be array';
  if (!Array.isArray(input.persona_set.personas)) return 'persona_set.personas must be array';
  return null;
}

function defaultRuleset() {
  return {
    id: 'persona-engine-default',
    version: '1',
    rewardAligned: 0.02,
    penalizeMisaligned: -0.03,
    highConfidencePenaltyBoost: -0.02,
    minRep: 0.05,
    maxRep: 0.95
  };
}

export async function handler(input) {
  const board_id = input?.board_id;
  try {
    const ve = validate(input);
    if (ve) return err(board_id || '', 'INVALID_INPUT', ve);

    const rules = { ...defaultRuleset(), ...(input.ruleset || {}) };
    const finalDecision = input.decision.final_decision;
    const personaById = new Map(input.persona_set.personas.map((p) => [p.persona_id, p]));

    const changes = [];

    for (const v of input.vote_batch.votes) {
      const persona = personaById.get(v.persona_id);
      if (!persona) continue;
      const before = Number(persona.reputation ?? v.reputation_before ?? 0.5);

      const aligned = (finalDecision === 'ALLOW' && v.vote === 'YES') ||
        (finalDecision === 'BLOCK' && v.vote === 'NO') ||
        (finalDecision === 'REQUIRE_REWRITE' && v.vote === 'REWRITE');

      let delta = aligned ? rules.rewardAligned : rules.penalizeMisaligned;
      if (!aligned && Number(v.confidence) >= 0.8) delta += rules.highConfidencePenaltyBoost;

      const after = clamp(before + delta, rules.minRep, rules.maxRep);
      persona.reputation = after;

      changes.push({
        persona_id: v.persona_id,
        reputation_before: before,
        delta,
        reputation_after: after,
        reasons: [aligned ? 'aligned_with_final_decision' : 'misaligned_with_final_decision']
      });
    }

    const timestamp = new Date().toISOString();

    return {
      board_id,
      reputation_delta: {
        reputation_delta_id: crypto.randomUUID(),
        board_id,
        decision_id: input.decision.decision_id || null,
        persona_set_id: input.persona_set.persona_set_id || null,
        ruleset: {
          id: String(rules.id),
          version: String(rules.version),
          hash: null
        },
        changes,
        created_at: timestamp
      },
      persona_set: {
        ...input.persona_set,
        updated_at: timestamp,
        personas: input.persona_set.personas
      }
    };
  } catch (e) {
    return err(board_id || '', 'PERSONA_ENGINE_FAILED', e.message || 'unknown');
  }
}

export async function invoke(input, opts = {}) { return handler(input, opts); }
