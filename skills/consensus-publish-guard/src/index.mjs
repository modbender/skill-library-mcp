import crypto from 'node:crypto';
import { rejectUnknown, getLatest, getPersonaSet, getDecisionByKey, writeArtifact, detectHardBlockFlags, aggregateVotes, makeIdempotencyKey, resolveStatePath } from 'consensus-guard-core/src/index.mjs';

const TOP = new Set(['board_id','content_draft','constraints','persona_set_id','mode','external_votes']);
const DRAFT = new Set(['channel','title','body','tags']);

function err(board_id, code, message, details={}) { return { board_id, error:{ code, message, details } }; }
function validate(input){
  if (!input || typeof input !== 'object') return 'input must be object';
  let e=rejectUnknown(input,TOP,'input'); if(e) return e;
  if (typeof input.board_id!=='string') return 'board_id required';
  if (!input.content_draft||typeof input.content_draft!=='object') return 'content_draft required';
  e=rejectUnknown(input.content_draft,DRAFT,'content_draft'); if(e) return e;
  if (!Array.isArray(input.content_draft.tags||[])) return 'content_draft.tags must be array';
  if (input.mode!==undefined && !['persona','external_agent'].includes(input.mode)) return 'mode must be persona|external_agent';
  if (input.external_votes!==undefined && !Array.isArray(input.external_votes)) return 'external_votes must be array';
  return null;
}

function votesFromContent(personaSet, draft, constraints={}){
  const text = `${draft.title||''}\n${draft.body||''}`;
  const flags = detectHardBlockFlags(text).filter(f =>
    (f==='LEGAL_CLAIM' && constraints.no_legal_claims) ||
    (f==='SENSITIVE_DATA' && constraints.no_sensitive_data) ||
    (f==='DISALLOWED_GUARANTEE' && constraints.no_definitive_promises) ||
    ['THREAT_OR_HARASSMENT','CONFIDENTIALITY_BREACH','WRONGDOING_INSTRUCTION','MEDICAL_CLAIM'].includes(f)
  );
  return personaSet.personas.map(p=>({ persona_id:p.persona_id,name:p.name,reputation_before:p.reputation,vote: flags.length?'NO':'YES',confidence: flags.length?0.9:0.72,reasons:[flags.length?'Policy risk':'No blockers'],red_flags:flags,suggested_edits: flags.length?['Remove claims and sensitive details']:[] }));
}

export async function handler(input, opts={}) {
  const board_id = input?.board_id;
  const statePath = resolveStatePath(opts);
  try {
    const v = validate(input); if (v) return err(board_id||'', 'INVALID_INPUT', v);
    const idem = makeIdempotencyKey({ board_id, content_draft: input.content_draft, constraints: input.constraints||{}, persona_set_id: input.persona_set_id || null });
    const prior = await getDecisionByKey(board_id, idem, statePath);
    if (prior?.response) return prior.response;

    const externalMode = input.mode === 'external_agent';
    let personaSet = externalMode ? null : (input.persona_set_id ? await getPersonaSet(board_id,input.persona_set_id,statePath) : await getLatest(board_id,'persona_set',statePath));
    if (!personaSet && !externalMode) {
      personaSet = { persona_set_id: null, personas: [1,2,3,4,5].map((n)=>({ persona_id:`default-${n}`, name:`Default Persona ${n}`, reputation:0.5 })) };
    }

    const votes = externalMode ? input.external_votes : votesFromContent(personaSet, input.content_draft, input.constraints||{});
    const aggregation = aggregateVotes(votes, { method:'WEIGHTED_APPROVAL_VOTE', approve_threshold:0.7 });
    const final_decision = aggregation.final_decision;
    const rewrite_patch = final_decision==='REWRITE' ? { title:(input.content_draft.title||'').replace(/guarantee/gi,'plan'), body:(input.content_draft.body||'').replace(/guarantee/gi,'aim') } : {};
    const decision_id = crypto.randomUUID();
    const timestamp = new Date().toISOString();
    const rep = { personas: [], updates: [] };
    const personas = rep.personas; const updates = rep.updates;

    const response = { board_id, decision_id, timestamp, persona_set_id: personaSet?.persona_set_id || input.persona_set_id || null, votes, aggregation: { method:aggregation.method, weighted_yes:aggregation.weighted_yes, weighted_no:aggregation.weighted_no, weighted_rewrite:aggregation.weighted_rewrite, hard_block:aggregation.hard_block, rationale:aggregation.rationale }, final_decision, rewrite_patch, persona_updates: updates, board_writes: [] };
    const dWrite = await writeArtifact(board_id,'decision',{ idempotency_key: idem, decision_id, final_decision, votes, aggregation, response },statePath);
    response.board_writes = [{ type:'decision', success:true, ref:dWrite.ref }, ];
    return response;
  } catch (e) { return err(board_id||'', 'PUBLISH_GUARD_FAILED', e.message||'unknown'); }
}

export async function invoke(input, opts = {}) {
  return handler(input, opts);
}
