import crypto from 'node:crypto';
import fs from 'node:fs';
import Ajv2020 from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';
import {
  rejectUnknown,
  getLatest,
  getPersonaSet,
  getDecisionByKey,
  writeArtifact,
  aggregateVotes,
    makeIdempotencyKey,
  resolveStatePath
} from 'consensus-guard-core';

const TOP = new Set(['board_id', 'proposed_deployment', 'constraints', 'persona_set_id', 'mode', 'external_votes']);
const VOTE = new Set(['persona_id', 'name', 'reputation_before', 'vote', 'confidence', 'reasons', 'red_flags', 'suggested_edits']);
const err = (b, c, m, d = {}) => ({ board_id: b, error: { code: c, message: m, details: d } });
const DECISION_MAP = (d) => (d === 'APPROVE' ? 'ALLOW' : d === 'REWRITE' ? 'REQUIRE_REWRITE' : 'BLOCK');

const schemaPath = new URL('../spec/input.schema.json', import.meta.url);
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
const validateSchema = ajv.compile(schema);

function validateVote(v) {
  if (!v || typeof v !== 'object' || Array.isArray(v)) return 'external_votes item must be object';
  const e = rejectUnknown(v, VOTE, 'external_votes[]');
  if (e) return e;
  if (!v.persona_id || !v.name) return 'external_votes[].persona_id/name required';
  if (typeof v.reputation_before !== 'number' || v.reputation_before < 0.05 || v.reputation_before > 0.95) return 'external_votes[].reputation_before must be 0.05..0.95';
  if (!['YES', 'NO', 'REWRITE'].includes(v.vote)) return 'external_votes[].vote must be YES|NO|REWRITE';
  if (typeof v.confidence !== 'number' || v.confidence < 0 || v.confidence > 1) return 'external_votes[].confidence must be 0..1';
  if (!Array.isArray(v.reasons) || !Array.isArray(v.red_flags) || !Array.isArray(v.suggested_edits)) return 'external_votes[].reasons/red_flags/suggested_edits must be arrays';
  return null;
}

function validate(input) {
  if (!validateSchema(input)) {
    const first = validateSchema.errors?.[0];
    return `schema: ${first?.instancePath || '/'} ${first?.message || 'invalid input'}`.trim();
  }
  const e = rejectUnknown(input, TOP, 'input');
  if (e) return e;
  if (input.external_votes !== undefined) {
    if (!Array.isArray(input.external_votes)) return 'external_votes must be array';
    for (const vote of input.external_votes) {
      const ve = validateVote(vote);
      if (ve) return ve;
    }
  }
  if (input.mode === 'external_agent' && (!Array.isArray(input.external_votes) || input.external_votes.length === 0)) return 'external_votes is required when mode=external_agent';
  return null;
}

function normalizeConstraints(c = {}) {
  return {
    require_rollback_artifact: c.require_rollback_artifact !== false,
    require_passing_tests: c.require_passing_tests !== false,
    require_canary_for_prod: c.require_canary_for_prod !== false,
    block_if_error_budget_breached: c.block_if_error_budget_breached !== false,
    max_initial_rollout_percent: Number.isInteger(c.max_initial_rollout_percent) ? c.max_initial_rollout_percent : 25,
    require_human_confirm_for_prod: c.require_human_confirm_for_prod !== false
  };
}

function detectPolicy(dep, c) {
  const hard = [];
  const rewrite = [];

  if (c.require_passing_tests && dep.checks.tests_passed !== true) hard.push('TESTS_FAILED');
  if (dep.checks.ci_status === 'failed') hard.push('CI_FAILED');
  if (c.require_rollback_artifact && dep.checks.rollback_artifact_present !== true) hard.push('MISSING_ROLLBACK_ARTIFACT');
  if (dep.checks.schema_compatibility === 'incompatible') hard.push('SCHEMA_INCOMPATIBLE');
  if (c.block_if_error_budget_breached && dep.checks.error_budget_ok !== true) hard.push('ERROR_BUDGET_BREACHED');

  if (!hard.length && dep.environment === 'prod' && c.require_canary_for_prod && dep.rollout.strategy === 'all-at-once') rewrite.push('PROD_REQUIRES_CANARY');
  if (!hard.length && dep.rollout.initial_percent > c.max_initial_rollout_percent) rewrite.push('INITIAL_ROLLOUT_TOO_HIGH');
  if (!hard.length && dep.environment === 'prod' && c.require_human_confirm_for_prod) rewrite.push('PROD_REQUIRES_HUMAN_CONFIRM');
  if (!hard.length && dep.checks.ci_status === 'pending') rewrite.push('CI_PENDING');
  if (!hard.length && dep.checks.schema_compatibility === 'unknown') rewrite.push('SCHEMA_COMPAT_UNKNOWN');

  return { hard_flags: [...new Set(hard)], rewrite_flags: [...new Set(rewrite)] };
}

function makeVotes(personaSet, flags) {
  const vote = flags.hard_flags.length ? 'NO' : flags.rewrite_flags.length ? 'REWRITE' : 'YES';
  return personaSet.personas.map((p) => ({
    persona_id: p.persona_id,
    name: p.name,
    reputation_before: p.reputation,
    vote,
    confidence: vote === 'NO' ? 0.92 : vote === 'REWRITE' ? 0.82 : 0.74,
    reasons: [vote === 'YES' ? 'Deployment gates are satisfied.' : 'Deployment requires stronger release safeguards.'],
    red_flags: vote === 'NO' ? flags.hard_flags : [],
    suggested_edits: vote === 'REWRITE' ? ['Tighten rollout strategy and confirm production gates before retry.'] : []
  }));
}

export async function handler(input, opts = {}) {
  const board_id = input?.board_id;
  const statePath = resolveStatePath(opts);

  try {
    const ve = validate(input);
    if (ve) return err(board_id || '', 'INVALID_INPUT', ve);

    const constraints = normalizeConstraints(input.constraints || {});
    const flags = detectPolicy(input.proposed_deployment, constraints);
    const externalMode = input.mode === 'external_agent';

    const idem = makeIdempotencyKey({ board_id, proposed_deployment: input.proposed_deployment, constraints, persona_set_id: input.persona_set_id || null, mode: input.mode || 'persona' });
    const prior = await getDecisionByKey(board_id, idem, statePath);
    if (prior?.response) return prior.response;

    let personaSet = externalMode ? null : (input.persona_set_id ? await getPersonaSet(board_id, input.persona_set_id, statePath) : await getLatest(board_id, 'persona_set', statePath));
    if (!personaSet && !externalMode) {
      personaSet = { persona_set_id: null, personas: [1,2,3,4,5].map((n)=>({ persona_id:`default-${n}`, name:`Default Persona ${n}`, reputation:0.5 })) };
    }

    const votes = externalMode ? input.external_votes : makeVotes(personaSet, flags);
    const ag = aggregateVotes(votes, { method: 'WEIGHTED_APPROVAL_VOTE', approve_threshold: 0.7 });

    let final_decision = DECISION_MAP(ag.final_decision);
    if (flags.hard_flags.length) final_decision = 'BLOCK';
    else if (flags.rewrite_flags.length && final_decision === 'ALLOW') final_decision = 'REQUIRE_REWRITE';

    const required_actions = [];
    if (final_decision === 'BLOCK') required_actions.push('Do not execute deployment');
    if (final_decision === 'REQUIRE_REWRITE') required_actions.push('Revise release plan and resubmit with safeguards');

    const decision_id = crypto.randomUUID();
    const timestamp = new Date().toISOString();
    const normalizedDecision = final_decision === 'ALLOW' ? 'APPROVE' : final_decision === 'REQUIRE_REWRITE' ? 'REWRITE' : 'BLOCK';
    const rep = { personas: [], updates: [] };

    const response = {
      board_id,
      decision_id,
      timestamp,
      persona_set_id: personaSet?.persona_set_id || input.persona_set_id || null,
      policy_flags: flags,
      votes,
      aggregation: {
        method: ag.method,
        weighted_yes: ag.weighted_yes,
        weighted_no: ag.weighted_no,
        weighted_rewrite: ag.weighted_rewrite,
        hard_block: ag.hard_block || flags.hard_flags.length > 0,
        rationale: ag.rationale
      },
      final_decision,
      required_actions,
      persona_updates: rep.updates,
      board_writes: []
    };

    const d = await writeArtifact(board_id, 'decision', { idempotency_key: idem, decision_id, final_decision, policy_flags: flags, votes, aggregation: ag, response }, statePath);

    response.board_writes = [{ type: 'decision', success: true, ref: d.ref }, ];
    return response;
  } catch (e) {
    return err(board_id || '', 'DEPLOYMENT_GUARD_FAILED', e.message || 'unknown');
  }
}

export async function invoke(input, opts = {}) { return handler(input, opts); }
