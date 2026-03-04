import { JsonStorage } from '@consensus-tools/consensus-tools/src/storage/JsonStorage.ts';
import { LedgerEngine } from '@consensus-tools/consensus-tools/src/ledger/ledger.ts';
import { JobEngine } from '@consensus-tools/consensus-tools/src/jobs/engine.ts';
import { defaultConfig } from '@consensus-tools/consensus-tools/src/config.ts';

const indexCache = new Map();

function mkEngine(statePath) {
  const storage = new JsonStorage(statePath);
  const cfg = structuredClone(defaultConfig);
  const ledger = new LedgerEngine(storage, cfg);
  const engine = new JobEngine(storage, ledger, cfg);
  return { storage, engine };
}

async function ensureIndex(boardId, statePath) {
  const key = `${statePath}::${boardId}`;
  if (indexCache.has(key)) return indexCache.get(key);
  const { storage, engine } = mkEngine(statePath);
  await storage.init();
  const jobs = await engine.listJobs({});
  const idx = { latest_by_type: {}, persona_by_id: {}, refs: {}, decisions_by_id: {}, idempotency: {} };
  for (const j of jobs) {
    if (j.boardId !== boardId || !String(j.title || '').startsWith('artifact:')) continue;
    const status = await engine.getStatus(j.id);
    const sub = [...(status.submissions || [])].reverse()[0];
    const art = sub?.artifacts;
    if (!art?.type || !art?.payload) continue;
    idx.latest_by_type[art.type] = art.payload;
    idx.refs[sub.id] = art.payload;
    if (art.type === 'persona_set' && art.payload.persona_set_id) idx.persona_by_id[art.payload.persona_set_id] = art.payload;
    if (art.type === 'decision' && art.payload.decision_id) idx.decisions_by_id[art.payload.decision_id] = art.payload;
    if (art.payload?.idempotency_key) idx.idempotency[art.payload.idempotency_key] = art.payload;
  }
  indexCache.set(key, idx);
  return idx;
}

export async function readBoardPolicy(boardId, statePath) {
  const idx = await ensureIndex(boardId, statePath);
  return idx.latest_by_type.board_policy || null;
}

export async function getLatestPersonaSet(boardId, statePath) {
  const idx = await ensureIndex(boardId, statePath);
  return idx.latest_by_type.persona_set || null;
}

export async function getPersonaSet(boardId, personaSetId, statePath) {
  const idx = await ensureIndex(boardId, statePath);
  return idx.persona_by_id[personaSetId] || null;
}

export async function getDecisionByIdempotency(boardId, idempotencyKey, statePath) {
  const idx = await ensureIndex(boardId, statePath);
  return idx.idempotency[idempotencyKey] || null;
}

export async function writeArtifact(boardId, { type, payload }, statePath) {
  const { storage, engine } = mkEngine(statePath);
  await storage.init();
  const job = await engine.postJob('orchestrator@local', {
    boardId,
    title: `artifact:${type}`,
    description: `Artifact write: ${type}`,
    mode: 'SUBMISSION',
    policyConfigJson: { type: 'FIRST_SUBMISSION_WINS' },
    reward: 0,
    rewardAmount: 0,
    stakeRequired: 0,
    stakeAmount: 0,
    expiresSeconds: 3600
  });
  const sub = await engine.submitJob('orchestrator@local', job.id, {
    summary: `${type} artifact`,
    artifacts: { type, payload, created_at: new Date().toISOString() },
    confidence: 1
  });
  await engine.resolveJob('orchestrator@local', job.id, { manualSubmissionId: sub.id, manualWinners: ['orchestrator@local'] });

  const idx = await ensureIndex(boardId, statePath);
  idx.latest_by_type[type] = payload;
  idx.refs[sub.id] = payload;
  if (type === 'persona_set' && payload.persona_set_id) idx.persona_by_id[payload.persona_set_id] = payload;
  if (type === 'decision' && payload.decision_id) idx.decisions_by_id[payload.decision_id] = payload;
  if (payload?.idempotency_key) idx.idempotency[payload.idempotency_key] = payload;

  return { success: true, ref: sub.id, job_id: job.id };
}
