import crypto from 'node:crypto';
import { JsonStorage } from '@consensus-tools/consensus-tools/src/storage/JsonStorage.ts';
import { rejectUnknown, getLatest, getPersonaSet, writeArtifact, makeIdempotencyKey, resolveStatePath } from 'consensus-guard-core';

const TOP = new Set(['board_id','trigger','persona_set_id','lookback_decisions']);
const TRIGGER = new Set(['persona_id','min_reputation','reason']);
const err=(b,c,m,d={})=>({board_id:b,error:{code:c,message:m,details:d}});

function validate(input){
  if(!input||typeof input!=='object'||Array.isArray(input)) return 'input must be object';
  let e = rejectUnknown(input, TOP, 'input'); if(e) return e;
  if(typeof input.board_id!=='string' || !input.board_id.trim()) return 'board_id is required';
  if(input.trigger!==undefined){
    if(typeof input.trigger!=='object'||Array.isArray(input.trigger)) return 'trigger must be object';
    e = rejectUnknown(input.trigger, TRIGGER, 'trigger'); if(e) return e;
  }
  if(input.persona_set_id!==undefined && typeof input.persona_set_id!=='string') return 'persona_set_id must be string';
  if(input.lookback_decisions!==undefined && typeof input.lookback_decisions!=='number') return 'lookback_decisions must be number';
  return null;
}

async function listRecentDecisions(boardId, statePath, limit=50){
  const storage = new JsonStorage(statePath); await storage.init();
  const state = await storage.getState();
  const out = [];
  for (const s of [...(state.submissions||[])].reverse()) {
    const a = s.artifacts;
    if (!a || a.type !== 'decision') continue;
    const payload = a.payload || {};
    if (payload.board_id === boardId) out.push(payload);
    if (out.length >= limit) break;
  }
  return out;
}

function buildLearningSummary(personaId, decisions){
  const patterns = new Map();
  let considered = 0;
  for (const d of decisions) {
    const votes = d.votes || d.response?.votes || [];
    const final = d.final_decision || d.response?.final_decision;
    const v = votes.find((x)=>x.persona_id===personaId);
    if (!v || !final) continue;
    considered += 1;
    const opposite = (final==='APPROVE'&&v.vote!=='YES') || (final==='BLOCK'&&v.vote!=='NO') || (final==='REWRITE'&&v.vote!=='REWRITE');
    if (opposite && Number(v.confidence||0) > 0.85) patterns.set('high_confidence_mismatch', (patterns.get('high_confidence_mismatch')||0)+1);
    for (const rf of (v.red_flags||[])) patterns.set(`red_flag:${rf}`, (patterns.get(`red_flag:${rf}`)||0)+1);
  }
  return { source_decisions: considered, mistake_patterns: [...patterns.entries()].sort((a,b)=>b[1]-a[1]).map(([k,v])=>`${k}:${v}`) };
}

function seedPersonaSet(board_id){
  const personas = [
    { name: 'Reliability Sentinel', role: 'reliability', bias: 'failure-first', non_negotiables: ['Rollback path required'], failure_modes: ['overconfidence'] },
    { name: 'Security Gatekeeper', role: 'security', bias: 'least-privilege', non_negotiables: ['No wildcard privileges'], failure_modes: ['excessive trust'] },
    { name: 'Operations Realist', role: 'operations', bias: 'operability', non_negotiables: ['Observable rollout'], failure_modes: ['underestimated blast radius'] },
    { name: 'Risk Controller', role: 'risk', bias: 'downside-aware', non_negotiables: ['Explicit risk acknowledgement'], failure_modes: ['missing edge-case analysis'] },
    { name: 'Policy Auditor', role: 'policy', bias: 'contract-first', non_negotiables: ['Policy contract compliance'], failure_modes: ['ambiguous requirements'] }
  ].map((p)=>({
    persona_id: `persona_${crypto.randomUUID().slice(0,8)}`,
    reputation: 0.55,
    ...p
  }));
  return { board_id, persona_set_id: crypto.randomUUID(), created_at: new Date().toISOString(), personas };
}

function mutatePersona(oldPersona, learning){
  const top = learning.mistake_patterns.slice(0,3);
  return {
    ...oldPersona,
    persona_id: `persona_${crypto.randomUUID().slice(0,8)}`,
    name: `${oldPersona.name} v2`,
    bias: `Adjusted from ledger mistakes (${top.join(', ') || 'none'})`,
    non_negotiables: [...new Set([...(oldPersona.non_negotiables||[]), 'Validate high-confidence disagreement'])],
    failure_modes: [...new Set([...(oldPersona.failure_modes||[]), 'Overconfidence without evidence'])],
    reputation: 0.55
  };
}

export async function handler(input, opts={}){
  const board_id = input?.board_id;
  const statePath = resolveStatePath(opts);
  try {
    const ve = validate(input); if (ve) return err(board_id||'', 'INVALID_INPUT', ve);

    let personaSet = input.persona_set_id ? await getPersonaSet(board_id, input.persona_set_id, statePath) : await getLatest(board_id, 'persona_set', statePath);
    if (!personaSet) {
      personaSet = seedPersonaSet(board_id);
    }

    const trigger = input.trigger || {};
    const idem = makeIdempotencyKey({ board_id, persona_set_id: input.persona_set_id || 'latest', persona_id: trigger.persona_id || null, min_reputation: trigger.min_reputation ?? 0.12, reason: trigger.reason||'auto' });
    const latestRespawn = await getLatest(board_id, 'persona_respawn', statePath);
    if (latestRespawn?.idempotency_key === idem && latestRespawn?.response) return latestRespawn.response;

    const minRep = Number(trigger.min_reputation ?? 0.12);
    const target = trigger.persona_id
      ? personaSet.personas.find((p)=>p.persona_id===trigger.persona_id)
      : [...personaSet.personas].sort((a,b)=>a.reputation-b.reputation).find((p)=>p.reputation<=minRep);
    if (!target) return err(board_id, 'NO_DEAD_PERSONA', 'No persona met respawn trigger');

    const decisions = await listRecentDecisions(board_id, statePath, Number(input.lookback_decisions || 50));
    const learning = buildLearningSummary(target.persona_id, decisions);
    const newPersona = mutatePersona(target, learning);

    const updated = {
      ...personaSet,
      persona_set_id: crypto.randomUUID(),
      updated_at: new Date().toISOString(),
      lineage: { parent_persona_set_id: personaSet.persona_set_id },
      personas: personaSet.personas.map((p)=> p.persona_id===target.persona_id ? newPersona : p)
    };

    const respawn_id = crypto.randomUUID();
    const timestamp = new Date().toISOString();
    const response = {
      board_id,
      respawn_id,
      timestamp,
      replaced_persona_id: target.persona_id,
      new_persona: newPersona,
      learning_summary: learning,
      board_writes: []
    };

    const rw = await writeArtifact(board_id, 'persona_respawn', {
      idempotency_key: idem,
      respawn_id,
      replaced_persona_id: target.persona_id,
      learning_summary: learning,
      response
    }, statePath);
    const pw = await writeArtifact(board_id, 'persona_set', updated, statePath);
    response.board_writes = [
      { type:'persona_respawn', success:true, ref: rw.ref },
      { type:'persona_set', success:true, ref: pw.ref }
    ];
    return response;
  } catch(e){
    return err(board_id||'', 'PERSONA_RESPAWN_FAILED', e.message||'unknown');
  }
}

export async function invoke(input, opts = {}) {
  return handler(input, opts);
}
