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

const TOP = new Set(['board_id', 'proposed_escalation', 'constraints', 'persona_set_id', 'mode', 'external_votes']);
const CONSTRAINTS = new Set([
  'require_ticket',
  'require_justification',
  'require_expiry_for_temporary',
  'max_temporary_duration_minutes',
  'block_wildcard_permissions',
  'production_requires_human_confirm',
  'forbid_break_glass_without_incident'
]);
const ESC = new Set([
  'request_id',
  'environment',
  'requested_at',
  'ticket_ref',
  'incident_ref',
  'justification',
  'subject',
  'resource',
  'change'
]);
const SUBJECT = new Set(['type', 'id', 'team', 'manager_id']);
const RESOURCE = new Set(['system', 'resource_id', 'tenant_id']);
const CHANGE = new Set(['kind', 'current_permissions', 'requested_permissions', 'temporary', 'expires_at', 'duration_minutes', 'break_glass']);
const VOTE = new Set(['persona_id', 'name', 'reputation_before', 'vote', 'confidence', 'reasons', 'red_flags', 'suggested_edits']);

const err = (b, c, m, d = {}) => ({ board_id: b, error: { code: c, message: m, details: d } });
const DECISION_MAP = (d) => (d === 'APPROVE' ? 'ALLOW' : d === 'REWRITE' ? 'REQUIRE_REWRITE' : 'BLOCK');

const schemaPath = new URL('../spec/input.schema.json', import.meta.url);
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
const validateSchema = ajv.compile(schema);

function isIsoDate(v) {
  if (typeof v !== 'string') return false;
  const t = Date.parse(v);
  return Number.isFinite(t) && /\d{4}-\d{2}-\d{2}T/.test(v);
}

function isNonEmptyString(v, min = 1) {
  return typeof v === 'string' && v.trim().length >= min;
}

function validateVote(v) {
  if (!v || typeof v !== 'object' || Array.isArray(v)) return 'external_votes item must be object';
  let e = rejectUnknown(v, VOTE, 'external_votes[]');
  if (e) return e;
  if (!isNonEmptyString(v.persona_id)) return 'external_votes[].persona_id is required';
  if (!isNonEmptyString(v.name)) return 'external_votes[].name is required';
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

  let e = rejectUnknown(input, TOP, 'input');
  if (e) return e;

  if (input.constraints !== undefined) {
    if (typeof input.constraints !== 'object' || Array.isArray(input.constraints)) return 'constraints must be object';
    e = rejectUnknown(input.constraints, CONSTRAINTS, 'constraints');
    if (e) return e;
  }

  if (input.external_votes !== undefined) {
    if (!Array.isArray(input.external_votes)) return 'external_votes must be array';
    for (const vote of input.external_votes) {
      e = validateVote(vote);
      if (e) return e;
    }
  }

  if (input.mode === 'external_agent' && (!Array.isArray(input.external_votes) || input.external_votes.length === 0)) {
    return 'external_votes is required when mode=external_agent';
  }

  const esc = input.proposed_escalation;
  e = rejectUnknown(esc, ESC, 'proposed_escalation');
  if (e) return e;
  if (!isNonEmptyString(esc.request_id)) return 'proposed_escalation.request_id is required';
  if (!['dev', 'staging', 'prod'].includes(esc.environment)) return 'proposed_escalation.environment must be dev|staging|prod';
  if (!isIsoDate(esc.requested_at)) return 'proposed_escalation.requested_at must be ISO datetime';
  if (!isNonEmptyString(esc.justification, 8)) return 'proposed_escalation.justification must be at least 8 chars';

  if (!esc.subject || typeof esc.subject !== 'object' || Array.isArray(esc.subject)) return 'proposed_escalation.subject is required';
  e = rejectUnknown(esc.subject, SUBJECT, 'proposed_escalation.subject');
  if (e) return e;
  if (!['user', 'service_account', 'role'].includes(esc.subject.type)) return 'proposed_escalation.subject.type must be user|service_account|role';
  if (!isNonEmptyString(esc.subject.id)) return 'proposed_escalation.subject.id is required';

  if (!esc.resource || typeof esc.resource !== 'object' || Array.isArray(esc.resource)) return 'proposed_escalation.resource is required';
  e = rejectUnknown(esc.resource, RESOURCE, 'proposed_escalation.resource');
  if (e) return e;
  if (!isNonEmptyString(esc.resource.system)) return 'proposed_escalation.resource.system is required';
  if (!isNonEmptyString(esc.resource.resource_id)) return 'proposed_escalation.resource.resource_id is required';

  if (!esc.change || typeof esc.change !== 'object' || Array.isArray(esc.change)) return 'proposed_escalation.change is required';
  e = rejectUnknown(esc.change, CHANGE, 'proposed_escalation.change');
  if (e) return e;

  if (!['grant', 'expand_scope', 'assume_role'].includes(esc.change.kind)) return 'proposed_escalation.change.kind must be grant|expand_scope|assume_role';
  if (!Array.isArray(esc.change.requested_permissions) || esc.change.requested_permissions.length < 1) return 'proposed_escalation.change.requested_permissions must have at least one item';
  if (typeof esc.change.temporary !== 'boolean') return 'proposed_escalation.change.temporary must be boolean';
  if (esc.change.expires_at !== undefined && !isIsoDate(esc.change.expires_at)) return 'proposed_escalation.change.expires_at must be ISO datetime';
  if (esc.change.duration_minutes !== undefined && !(Number.isInteger(esc.change.duration_minutes) && esc.change.duration_minutes > 0)) return 'proposed_escalation.change.duration_minutes must be a positive integer';

  return null;
}

function normalizeConstraints(c = {}) {
  return {
    require_ticket: c.require_ticket !== false,
    require_justification: c.require_justification !== false,
    require_expiry_for_temporary: c.require_expiry_for_temporary !== false,
    max_temporary_duration_minutes: Number.isInteger(c.max_temporary_duration_minutes) ? c.max_temporary_duration_minutes : 240,
    block_wildcard_permissions: c.block_wildcard_permissions !== false,
    production_requires_human_confirm: c.production_requires_human_confirm !== false,
    forbid_break_glass_without_incident: c.forbid_break_glass_without_incident !== false
  };
}

function detectPolicy(escalation, constraints) {
  const hard = [];
  const rewrite = [];
  const req = escalation.change.requested_permissions || [];
  const cur = escalation.change.current_permissions || [];

  const hasWildcard = req.some((p) => typeof p === 'string' && (p.trim() === '*' || p.includes(':*') || p.includes('.*')));
  if (constraints.block_wildcard_permissions && hasWildcard) hard.push('WILDCARD_PERMISSION');

  if (constraints.require_ticket && !isNonEmptyString(escalation.ticket_ref)) hard.push('MISSING_TICKET');
  if (constraints.require_justification && !isNonEmptyString(escalation.justification, 8)) hard.push('MISSING_JUSTIFICATION');

  if (constraints.require_expiry_for_temporary && escalation.change.temporary && !escalation.change.expires_at && !escalation.change.duration_minutes) {
    hard.push('TEMP_NO_EXPIRY');
  }

  if (constraints.forbid_break_glass_without_incident && escalation.change.break_glass === true && !isNonEmptyString(escalation.incident_ref)) {
    hard.push('BREAK_GLASS_NO_INCIDENT');
  }

  const hasCreate = [...cur, ...req].some((p) => /payments:create/.test(String(p)));
  const hasApprove = [...cur, ...req].some((p) => /payments:approve/.test(String(p)));
  if (hasCreate && hasApprove) hard.push('SOD_CONFLICT');

  const currentHasOwner = cur.some((p) => /owner/.test(String(p)));
  const requestedHasOwner = req.some((p) => /owner/.test(String(p)));
  if (!currentHasOwner && requestedHasOwner) hard.push('FORBIDDEN_ROLE_JUMP');

  const weakJustification = /^(need it asap|please approve|urgent access|need access)$/i.test((escalation.justification || '').trim());
  if (!hard.length && weakJustification) rewrite.push('JUSTIFICATION_TOO_WEAK');

  if (!hard.length && escalation.change.temporary && Number(escalation.change.duration_minutes || 0) > constraints.max_temporary_duration_minutes) {
    rewrite.push('TEMP_DURATION_TOO_LONG');
  }

  if (!hard.length && escalation.environment === 'prod' && constraints.production_requires_human_confirm) {
    rewrite.push('PROD_REQUIRES_HUMAN_CONFIRM');
  }

  return { hard_flags: [...new Set(hard)], rewrite_flags: [...new Set(rewrite)] };
}

function voteFromFlags(policyFlags) {
  if (policyFlags.hard_flags.length) return 'NO';
  if (policyFlags.rewrite_flags.length) return 'REWRITE';
  return 'YES';
}

function makePersonaVotes(personaSet, policyFlags) {
  const vote = voteFromFlags(policyFlags);
  const flags = vote === 'NO' ? policyFlags.hard_flags : policyFlags.rewrite_flags;
  return personaSet.personas.map((p) => ({
    persona_id: p.persona_id,
    name: p.name,
    reputation_before: p.reputation,
    vote,
    confidence: vote === 'NO' ? 0.92 : vote === 'REWRITE' ? 0.82 : 0.73,
    reasons: [vote === 'YES' ? 'Escalation is constrained, time-boxed, and justified.' : 'Escalation requires stronger safeguards before execution.'],
    red_flags: vote === 'NO' ? flags : [],
    suggested_edits: vote === 'REWRITE' ? ['Add required metadata and tighten least-privilege scope before retry.'] : []
  }));
}

export async function handler(input, opts = {}) {
  const board_id = input?.board_id;
  const statePath = resolveStatePath(opts);

  try {
    const ve = validate(input);
    if (ve) return err(board_id || '', 'INVALID_INPUT', ve);

    const constraints = normalizeConstraints(input.constraints || {});
    const policyFlags = detectPolicy(input.proposed_escalation, constraints);
    const externalMode = input.mode === 'external_agent';

    const idem = makeIdempotencyKey({
      board_id,
      proposed_escalation: input.proposed_escalation,
      constraints,
      persona_set_id: input.persona_set_id || null,
      mode: input.mode || 'persona'
    });

    const prior = await getDecisionByKey(board_id, idem, statePath);
    if (prior?.response) return prior.response;

    let personaSet = externalMode
      ? null
      : (input.persona_set_id
        ? await getPersonaSet(board_id, input.persona_set_id, statePath)
        : await getLatest(board_id, 'persona_set', statePath));

    if (!personaSet && !externalMode) {
      personaSet = { persona_set_id: null, personas: [1,2,3,4,5].map((n)=>({ persona_id:`default-${n}`, name:`Default Persona ${n}`, reputation:0.5 })) };
    }

    const votes = externalMode ? input.external_votes : makePersonaVotes(personaSet, policyFlags);
    const ag = aggregateVotes(votes, { method: 'WEIGHTED_APPROVAL_VOTE', approve_threshold: 0.7 });

    let final_decision = DECISION_MAP(ag.final_decision);
    if (policyFlags.hard_flags.length) final_decision = 'BLOCK';
    else if (policyFlags.rewrite_flags.length && final_decision === 'ALLOW') final_decision = 'REQUIRE_REWRITE';

    const required_actions = [];
    if (final_decision === 'BLOCK') required_actions.push('Do not apply permission escalation');
    if (final_decision === 'REQUIRE_REWRITE') required_actions.push('Amend escalation request and resubmit with safeguards');

    const decision_id = crypto.randomUUID();
    const timestamp = new Date().toISOString();

    const normalizedDecision = final_decision === 'ALLOW' ? 'APPROVE' : final_decision === 'REQUIRE_REWRITE' ? 'REWRITE' : 'BLOCK';
    const rep = { personas: [], updates: [] };

    const response = {
      board_id,
      decision_id,
      timestamp,
      persona_set_id: personaSet?.persona_set_id || input.persona_set_id || null,
      policy_flags: {
        hard_flags: policyFlags.hard_flags,
        rewrite_flags: policyFlags.rewrite_flags
      },
      votes,
      aggregation: {
        method: ag.method,
        weighted_yes: ag.weighted_yes,
        weighted_no: ag.weighted_no,
        weighted_rewrite: ag.weighted_rewrite,
        hard_block: ag.hard_block || policyFlags.hard_flags.length > 0,
        rationale: ag.rationale
      },
      final_decision,
      required_actions,
      persona_updates: rep.updates,
      board_writes: []
    };

    const d = await writeArtifact(board_id, 'decision', {
      idempotency_key: idem,
      decision_id,
      final_decision,
      policy_flags: response.policy_flags,
      votes,
      aggregation: ag,
      response
    }, statePath);

    response.board_writes = [
      { type: 'decision', success: true, ref: d.ref },
      
    ];

    return response;
  } catch (e) {
    return err(board_id || '', 'PERMISSION_ESCALATION_GUARD_FAILED', e.message || 'unknown');
  }
}

export async function invoke(input, opts = {}) {
  return handler(input, opts);
}
