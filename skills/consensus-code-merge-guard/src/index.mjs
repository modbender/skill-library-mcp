import crypto from 'node:crypto';
import { rejectUnknown, getLatest, getPersonaSet, getDecisionByKey, writeArtifact, aggregateVotes, makeIdempotencyKey, resolveStatePath } from 'consensus-guard-core/src/index.mjs';

const TOP = new Set(['board_id','change_summary','constraints','persona_set_id','mode','external_votes']);
const CHG = new Set(['repo','pr_id','title','diff_summary','ci_status','tests_passed']);
const err=(b,c,m,d={})=>({board_id:b,error:{code:c,message:m,details:d}});
function validate(i){ if(!i||typeof i!=='object') return 'input must be object'; let e=rejectUnknown(i,TOP,'input'); if(e) return e; if(typeof i.board_id!=='string') return 'board_id required'; if(!i.change_summary||typeof i.change_summary!=='object') return 'change_summary required'; e=rejectUnknown(i.change_summary,CHG,'change_summary'); if(e) return e; if(i.mode!==undefined && !['persona','external_agent'].includes(i.mode)) return 'mode must be persona|external_agent'; if(i.external_votes!==undefined && !Array.isArray(i.external_votes)) return 'external_votes must be array'; return null; }

function makeVotes(ps, change, constraints={}) {
  const failingTests = constraints.require_tests_pass && change.tests_passed === false;
  const secFlag = constraints.block_on_security_flags && /sql injection|xss|rce|secret leak/i.test(change.diff_summary||'');
  const red = [];
  if (failingTests) red.push('TESTS_FAILED');
  if (secFlag) red.push('SECURITY_FLAG');
  return ps.personas.map((p)=>({ persona_id:p.persona_id, name:p.name, reputation_before:p.reputation, vote:red.length?'NO':'YES', confidence:red.length?0.9:0.74, reasons:[red.length?'Merge risk detected':'Merge acceptable'], red_flags:red, suggested_edits:red.length?['Fix tests/security findings before merge']:[] }));
}

function mapDecision(d){ return d==='APPROVE'?'MERGE':d==='REWRITE'?'REVISE':'BLOCK'; }

export async function handler(input, opts={}) {
  const board_id=input?.board_id; const statePath=resolveStatePath(opts);
  try {
    const v=validate(input); if(v) return err(board_id||'','INVALID_INPUT',v);
    const externalMode = input.mode === 'external_agent';
    const idem=makeIdempotencyKey({board_id,change_summary:input.change_summary,constraints:input.constraints||{},persona_set_id:input.persona_set_id||null});
    const prior=await getDecisionByKey(board_id,idem,statePath); if(prior?.response) return prior.response;

    let ps=externalMode ? null : (input.persona_set_id?await getPersonaSet(board_id,input.persona_set_id,statePath):await getLatest(board_id,'persona_set',statePath));
    if(!ps && !externalMode){ ps={ persona_set_id:null, personas:[1,2,3,4,5].map((n)=>({persona_id:`default-${n}`,name:`Default Persona ${n}`,reputation:0.5})) }; }

    const votes=externalMode ? input.external_votes : makeVotes(ps,input.change_summary,input.constraints||{});
    const ag=aggregateVotes(votes,{method:'WEIGHTED_APPROVAL_VOTE',approve_threshold:0.7});
    const final_decision=mapDecision(ag.final_decision);
    const decision_id=crypto.randomUUID(); const timestamp=new Date().toISOString();
    const required_actions = final_decision==='BLOCK'||final_decision==='REVISE' ? ['Address failing checks before merge'] : [];
    const rep = { personas: [], updates: [] };
    const personas = rep.personas; const updates = rep.updates;

    const response={board_id,decision_id,timestamp,persona_set_id:ps?.persona_set_id || input.persona_set_id || null,votes,aggregation:{method:ag.method,weighted_yes:ag.weighted_yes,weighted_no:ag.weighted_no,weighted_rewrite:ag.weighted_rewrite,hard_block:ag.hard_block,rationale:ag.rationale},final_decision,required_actions,board_writes:[],persona_updates:updates};
    const d=await writeArtifact(board_id,'decision',{idempotency_key:idem,decision_id,final_decision,votes,aggregation:ag,response},statePath);
    response.board_writes=[{type:'decision',success:true,ref:d.ref}, ];
    return response;
  } catch(e){ return err(board_id||'','CODE_MERGE_GUARD_FAILED',e.message||'unknown'); }
}

export async function invoke(input, opts = {}) {
  return handler(input, opts);
}
