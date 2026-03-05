import { JsonStorage } from '@consensus-tools/consensus-tools/src/storage/JsonStorage.ts';
import { LedgerEngine } from '@consensus-tools/consensus-tools/src/ledger/ledger.ts';
import { JobEngine } from '@consensus-tools/consensus-tools/src/jobs/engine.ts';
import { defaultConfig } from '@consensus-tools/consensus-tools/src/config.ts';

const cache = new Map();
const key = (boardId, statePath) => `${statePath}::${boardId}`;

function mk(statePath) {
  const storage = new JsonStorage(statePath);
  const cfg = structuredClone(defaultConfig);
  const ledger = new LedgerEngine(storage, cfg);
  const engine = new JobEngine(storage, ledger, cfg);
  return { storage, engine };
}

export async function hydrateIndex(boardId, statePath) {
  const k = key(boardId, statePath);
  if (cache.has(k)) return cache.get(k);
  const { storage, engine } = mk(statePath);
  await storage.init();
  const idx = { latest_by_type:{}, persona_by_id:{}, idempotency:{} };
  const jobs = await engine.listJobs({});
  for (const j of jobs) {
    if (j.boardId !== boardId || !String(j.title||'').startsWith('artifact:')) continue;
    const st = await engine.getStatus(j.id);
    const sub = [...(st.submissions||[])].reverse()[0];
    const art = sub?.artifacts;
    if (!art?.type || !art?.payload) continue;
    idx.latest_by_type[art.type] = art.payload;
    if (art.type==='persona_set' && art.payload.persona_set_id) idx.persona_by_id[art.payload.persona_set_id]=art.payload;
    if (art.type==='decision' && art.payload.idempotency_key) idx.idempotency[art.payload.idempotency_key] = art.payload;
  }
  cache.set(k, idx);
  return idx;
}

export async function getLatest(boardId, type, statePath) { const i = await hydrateIndex(boardId,statePath); return i.latest_by_type[type] || null; }
export async function getPersonaSet(boardId, personaSetId, statePath){ const i = await hydrateIndex(boardId,statePath); return i.persona_by_id[personaSetId] || null; }
export async function getDecisionByKey(boardId, idem, statePath){ const i = await hydrateIndex(boardId,statePath); return i.idempotency[idem] || null; }

// consensus-interact contract wrappers (single boundary for skill tool calls)
export async function readBoardPolicy(boardId, statePath) {
  return getLatest(boardId, 'board_policy', statePath);
}

export async function getLatestPersonaSet(boardId, statePath) {
  return getLatest(boardId, 'persona_set', statePath);
}

export async function getDecisionByIdempotency(boardId, idempotencyKey, statePath) {
  return getDecisionByKey(boardId, idempotencyKey, statePath);
}

export async function writeDecision(boardId, payload, statePath) {
  return writeArtifact(boardId, 'decision', payload, statePath);
}

export async function writeArtifact(boardId, type, payload, statePath) {
  const { storage, engine } = mk(statePath); await storage.init();
  const job = await engine.postJob('orchestrator@local', { boardId, title:`artifact:${type}`, description:`Artifact write: ${type}`, mode:'SUBMISSION', policyConfigJson:{type:'FIRST_SUBMISSION_WINS'}, reward:0,rewardAmount:0,stakeRequired:0,stakeAmount:0,expiresSeconds:3600 });
  const sub = await engine.submitJob('orchestrator@local', job.id, { summary:`${type} artifact`, artifacts:{ type, payload, created_at:new Date().toISOString() }, confidence:1 });
  await engine.resolveJob('orchestrator@local', job.id, { manualSubmissionId:sub.id, manualWinners:['orchestrator@local'] });
  const i = await hydrateIndex(boardId,statePath);
  i.latest_by_type[type]=payload;
  if (type==='persona_set' && payload.persona_set_id) i.persona_by_id[payload.persona_set_id]=payload;
  if (type==='decision' && payload.idempotency_key) i.idempotency[payload.idempotency_key]=payload;
  return { success:true, ref: sub.id };
}
