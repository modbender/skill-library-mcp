import crypto from 'node:crypto';
import { rejectUnknown, getLatest, getPersonaSet, getDecisionByKey, writeArtifact, aggregateVotes, makeIdempotencyKey, detectHardBlockFlags, resolveStatePath } from 'consensus-guard-core';

const TOP = new Set(['board_id','proposed_action','constraints','persona_set_id','mode','external_votes']);
const ACTION = new Set(['action_type','target','summary','irreversible','external_side_effect','risk_level']);
const CONSTRAINTS = new Set(['require_human_confirm_for_irreversible','block_sensitive_exfiltration']);
const err=(b,c,m,d={})=>({board_id:b,error:{code:c,message:m,details:d}});

function validate(input){
  if(!input||typeof input!=='object'||Array.isArray(input)) return 'input must be object';
  let e=rejectUnknown(input,TOP,'input'); if(e) return e;
  if(typeof input.board_id!=='string' || !input.board_id.trim()) return 'board_id is required';
  if(!input.proposed_action||typeof input.proposed_action!=='object'||Array.isArray(input.proposed_action)) return 'proposed_action is required';
  e=rejectUnknown(input.proposed_action,ACTION,'proposed_action'); if(e) return e;
  if(input.constraints!==undefined){
    if(typeof input.constraints!=='object'||Array.isArray(input.constraints)) return 'constraints must be object';
    e=rejectUnknown(input.constraints,CONSTRAINTS,'constraints'); if(e) return e;
  }
  if(input.mode!==undefined && !['persona','external_agent'].includes(input.mode)) return 'mode must be persona|external_agent';
  if(input.external_votes!==undefined && !Array.isArray(input.external_votes)) return 'external_votes must be array';
  return null;
}

function makeVotes(personaSet, action, constraints={}){
  const txt = `${action.action_type||''}\n${action.summary||''}`;
  const flags = detectHardBlockFlags(txt);
  const highRisk = action.risk_level === 'high';
  const irreversible = !!action.irreversible;
  const blockExfil = constraints.block_sensitive_exfiltration && flags.includes('SENSITIVE_DATA');
  const mustConfirm = constraints.require_human_confirm_for_irreversible && irreversible;

  return personaSet.personas.map((p)=>{
    let vote = 'YES';
    const red = [];
    if (highRisk && irreversible) { vote = 'NO'; red.push('HIGH_RISK_IRREVERSIBLE'); }
    if (blockExfil) { vote = 'NO'; red.push('SENSITIVE_DATA'); }
    if (!red.length && mustConfirm) { vote = 'REWRITE'; red.push('HUMAN_CONFIRM_REQUIRED'); }
    return {
      persona_id: p.persona_id,
      name: p.name,
      reputation_before: p.reputation,
      vote,
      confidence: vote==='NO' ? 0.9 : vote==='REWRITE' ? 0.8 : 0.72,
      reasons: [vote==='YES' ? 'Action acceptable' : 'Action requires additional safeguards'],
      red_flags: red,
      suggested_edits: vote==='REWRITE' ? ['Add explicit human confirmation gate before execution'] : []
    };
  });
}

const mapDecision = (d)=> d==='APPROVE' ? 'ALLOW' : d==='REWRITE' ? 'REQUIRE_REWRITE' : 'BLOCK';

export async function handler(input, opts={}){
  const board_id = input?.board_id;
  const statePath = resolveStatePath(opts);
  try {
    const ve = validate(input); if (ve) return err(board_id||'', 'INVALID_INPUT', ve);

    const externalMode = input.mode === 'external_agent';
    const idem = makeIdempotencyKey({ board_id, proposed_action: input.proposed_action, constraints: input.constraints||{}, persona_set_id: input.persona_set_id||null });
    const prior = await getDecisionByKey(board_id, idem, statePath);
    if (prior?.response) return prior.response;

    let personaSet = externalMode ? null : (input.persona_set_id ? await getPersonaSet(board_id, input.persona_set_id, statePath) : await getLatest(board_id, 'persona_set', statePath));
    if (!personaSet && !externalMode) {
      personaSet = { persona_set_id: null, personas: [1,2,3,4,5].map((n)=>({ persona_id:`default-${n}`, name:`Default Persona ${n}`, reputation:0.5 })) };
    }

    const votes = externalMode ? input.external_votes : makeVotes(personaSet, input.proposed_action, input.constraints || {});
    const ag = aggregateVotes(votes, { method:'WEIGHTED_APPROVAL_VOTE', approve_threshold:0.7 });
    const final_decision = mapDecision(ag.final_decision);
    const required_actions = [];
    if (final_decision === 'BLOCK') required_actions.push('Do not execute action');
    if (final_decision === 'REQUIRE_REWRITE') required_actions.push('Add human confirmation step');

    const decision_id = crypto.randomUUID();
    const timestamp = new Date().toISOString();
    const rep = { personas: [], updates: [] };
    const personas = rep.personas; const updates = rep.updates;

    const response = {
      board_id,
      decision_id,
      timestamp,
      persona_set_id: personaSet?.persona_set_id || input.persona_set_id || null,
      votes,
      aggregation: {
        method: ag.method,
        weighted_yes: ag.weighted_yes,
        weighted_no: ag.weighted_no,
        weighted_rewrite: ag.weighted_rewrite,
        hard_block: ag.hard_block,
        rationale: ag.rationale
      },
      final_decision,
      required_actions,
      persona_updates: updates,
      board_writes: []
    };

    const d = await writeArtifact(board_id, 'decision', {
      idempotency_key: idem,
      decision_id,
      final_decision,
      votes,
      aggregation: ag,
      response
    }, statePath);
    response.board_writes = [
      { type:'decision', success:true, ref:d.ref },
      
    ];
    return response;
  } catch(e){
    return err(board_id||'', 'AGENT_ACTION_GUARD_FAILED', e.message||'unknown');
  }
}

export async function invoke(input, opts = {}) {
  return handler(input, opts);
}
