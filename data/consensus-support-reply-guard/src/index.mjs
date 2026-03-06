import crypto from 'node:crypto';
import { rejectUnknown, getLatest, getPersonaSet, getDecisionByKey, writeArtifact, detectHardBlockFlags, aggregateVotes, makeIdempotencyKey, resolveStatePath } from 'consensus-guard-core';

const TOP = new Set(['board_id','reply_draft','constraints','persona_set_id','mode','external_votes']);
const DRAFT = new Set(['ticket_id','customer_tier','subject','body']);
const err=(b,c,m,d={})=>({board_id:b,error:{code:c,message:m,details:d}});
function validate(i){ if(!i||typeof i!=='object') return 'input must be object'; let e=rejectUnknown(i,TOP,'input'); if(e) return e; if(typeof i.board_id!=='string') return 'board_id required'; if(!i.reply_draft||typeof i.reply_draft!=='object') return 'reply_draft required'; e=rejectUnknown(i.reply_draft,DRAFT,'reply_draft'); if(e) return e; if(i.mode!==undefined && !['persona','external_agent'].includes(i.mode)) return 'mode must be persona|external_agent'; if(i.external_votes!==undefined && !Array.isArray(i.external_votes)) return 'external_votes must be array'; return null; }

function makeVotes(ps,draft,constraints={}){
  const flags = detectHardBlockFlags(`${draft.subject||''}\n${draft.body||''}`).filter(f=>
    (f==='LEGAL_CLAIM'&&constraints.no_legal_claims) || (f==='SENSITIVE_DATA'&&constraints.no_sensitive_data) || ['THREAT_OR_HARASSMENT','CONFIDENTIALITY_BREACH'].includes(f)
  );
  return ps.personas.map(p=>({ persona_id:p.persona_id,name:p.name,reputation_before:p.reputation,vote:flags.length?'NO':'YES',confidence:flags.length?0.9:0.75,reasons:[flags.length?'Risky support language':'Safe reply'],red_flags:flags,suggested_edits:flags.length?['Remove legal/sensitive assertions']:[] }));
}

export async function handler(input, opts={}) {
  const board_id=input?.board_id; const statePath=resolveStatePath(opts);
  try {
    const v=validate(input); if(v) return err(board_id||'','INVALID_INPUT',v);
    const externalMode = input.mode === 'external_agent';
    let ps=externalMode ? null : (input.persona_set_id?await getPersonaSet(board_id,input.persona_set_id,statePath):await getLatest(board_id,'persona_set',statePath));
    if(!ps && !externalMode){ ps={ persona_set_id:null, personas:[1,2,3,4,5].map((n)=>({persona_id:`default-${n}`,name:`Default Persona ${n}`,reputation:0.5})) }; }
    const idem=makeIdempotencyKey({board_id,reply_draft:input.reply_draft,constraints:input.constraints||{},persona_set_id:ps?.persona_set_id || input.persona_set_id || null});
    const prior=await getDecisionByKey(board_id,idem,statePath); if(prior?.response) return prior.response;
    const votes=externalMode ? input.external_votes : makeVotes(ps,input.reply_draft,input.constraints||{}); const ag=aggregateVotes(votes,{method:'WEIGHTED_APPROVAL_VOTE',approve_threshold:0.7});
    const decision_id=crypto.randomUUID(); const timestamp=new Date().toISOString(); const final_decision=ag.final_decision;
    const rewrite_patch = final_decision==='REWRITE'?{subject:input.reply_draft.subject, body:(input.reply_draft.body||'').replace(/guarantee|legal certainty/gi,'we will review and follow policy')}:{};
    const rep = { personas: [], updates: [] };
    const personas = rep.personas; const updates = rep.updates;
    const response={board_id,decision_id,timestamp,persona_set_id:ps?.persona_set_id || input.persona_set_id || null,votes,aggregation:{method:ag.method,weighted_yes:ag.weighted_yes,weighted_no:ag.weighted_no,weighted_rewrite:ag.weighted_rewrite,hard_block:ag.hard_block,rationale:ag.rationale},final_decision,rewrite_patch,persona_updates:updates,board_writes:[]};
    const d=await writeArtifact(board_id,'decision',{idempotency_key:idem,decision_id,final_decision,votes,aggregation:ag,response},statePath);
    response.board_writes=[{type:'decision',success:true,ref:d.ref}, ];
    return response;
  } catch(e){ return err(board_id||'','SUPPORT_REPLY_GUARD_FAILED',e.message||'unknown'); }
}

export async function invoke(input, opts = {}) {
  return handler(input, opts);
}
