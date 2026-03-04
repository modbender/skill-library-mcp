import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import zvec from '@zvec/zvec';

const BASE_DIR = path.resolve(process.env.RAG_BASE_DIR || path.join(os.homedir(), '.openclaw/data/zvec-rag-service'));
const HOST = process.env.RAG_HOST || '127.0.0.1';
const PORT = Number(process.env.RAG_PORT || 8787);
const ALLOW_NON_LOOPBACK_HOST = process.env.ALLOW_NON_LOOPBACK_HOST === 'true';
const OLLAMA_URL = process.env.OLLAMA_URL || 'http://127.0.0.1:11434';
const MODEL = process.env.OLLAMA_EMBED_MODEL || 'mxbai-embed-large';
const ALLOW_REMOTE_OLLAMA = process.env.ALLOW_REMOTE_OLLAMA === 'true';

const DB_PATH = path.join(BASE_DIR, 'db');
const META_PATH = path.join(BASE_DIR, 'meta.json');

fs.mkdirSync(BASE_DIR, { recursive: true });

function isLoopbackUrl(urlText) {
  try {
    const u = new URL(urlText);
    return ['127.0.0.1', 'localhost', '::1'].includes(u.hostname);
  } catch {
    return false;
  }
}

if (!isLoopbackUrl(OLLAMA_URL) && !ALLOW_REMOTE_OLLAMA) {
  throw new Error('Remote OLLAMA_URL is blocked by default. Use loopback URL or set ALLOW_REMOTE_OLLAMA=true intentionally.');
}

if (!['127.0.0.1', 'localhost', '::1'].includes(HOST) && !ALLOW_NON_LOOPBACK_HOST) {
  throw new Error('Non-loopback RAG_HOST is blocked by default. Use loopback host or set ALLOW_NON_LOOPBACK_HOST=true intentionally.');
}

let collection = null;
let dimension = null;

function json(res, code, obj) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(obj));
}

async function readJsonBody(req) {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString('utf8') || '{}';
  return JSON.parse(raw);
}

async function embed(text) {
  const res = await fetch(`${OLLAMA_URL}/api/embeddings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: MODEL, prompt: text }),
  });
  if (!res.ok) throw new Error(`Embeddings failed: ${res.status} ${await res.text()}`);
  const data = await res.json();
  if (!Array.isArray(data.embedding) || data.embedding.length === 0) throw new Error('No embedding returned');
  return data.embedding;
}

function listTextFiles(dir) {
  if (!fs.existsSync(dir)) return [];
  const out = [];
  const stack = [path.resolve(dir)];
  while (stack.length) {
    const cur = stack.pop();
    for (const ent of fs.readdirSync(cur, { withFileTypes: true })) {
      const p = path.join(cur, ent.name);
      if (ent.isDirectory()) stack.push(p);
      else if (/\.(txt|md)$/i.test(ent.name)) out.push(p);
    }
  }
  return out;
}

function chunkText(text, size = 900, overlap = 120) {
  const clean = String(text || '').replace(/\s+/g, ' ').trim();
  if (!clean) return [];
  const chunks = [];
  let i = 0;
  while (i < clean.length) {
    const end = Math.min(clean.length, i + size);
    chunks.push(clean.slice(i, end));
    if (end === clean.length) break;
    i = Math.max(0, end - overlap);
  }
  return chunks;
}

function resetDir(dir) {
  if (fs.existsSync(dir)) fs.rmSync(dir, { recursive: true, force: true });
}

function openExistingIfAny() {
  if (fs.existsSync(DB_PATH)) {
    collection = zvec.ZVecOpen(DB_PATH);
    dimension = collection.schema.vector('embedding').dimension;
  }
}

function ensureCollection(dim, reset = false) {
  if (collection && !reset && dimension === dim) return;
  if (collection) {
    collection.closeSync();
    collection = null;
  }
  if (reset) resetDir(DB_PATH);

  const schema = new zvec.ZVecCollectionSchema({
    name: 'docs',
    vectors: { name: 'embedding', dataType: zvec.ZVecDataType.VECTOR_FP32, dimension: dim },
    fields: [
      { name: 'source', dataType: zvec.ZVecDataType.STRING },
      { name: 'chunkIndex', dataType: zvec.ZVecDataType.INT32 },
      { name: 'text', dataType: zvec.ZVecDataType.STRING },
    ],
  });

  collection = zvec.ZVecCreateAndOpen(DB_PATH, schema);
  dimension = dim;
}

async function ingestFromDir(dir, reset = true) {
  const files = listTextFiles(dir);
  if (!files.length) return { files: 0, chunks: 0 };

  const rows = [];
  for (const f of files) {
    const text = fs.readFileSync(f, 'utf8');
    const chunks = chunkText(text);
    chunks.forEach((c, idx) => rows.push({
      id: `${path.basename(f)}#${idx + 1}`,
      source: path.resolve(f),
      chunkIndex: idx + 1,
      text: c,
    }));
  }
  if (!rows.length) return { files: files.length, chunks: 0 };

  const firstVec = await embed(rows[0].text);
  ensureCollection(firstVec.length, reset);

  const docs = [{
    id: rows[0].id,
    vectors: { embedding: firstVec },
    fields: { source: rows[0].source, chunkIndex: rows[0].chunkIndex, text: rows[0].text },
  }];

  for (let i = 1; i < rows.length; i++) {
    const vec = await embed(rows[i].text);
    docs.push({
      id: rows[i].id,
      vectors: { embedding: vec },
      fields: { source: rows[i].source, chunkIndex: rows[i].chunkIndex, text: rows[i].text },
    });
  }

  collection.insertSync(docs);
  fs.writeFileSync(META_PATH, JSON.stringify({ updatedAt: new Date().toISOString(), model: MODEL, dim: dimension, files: files.length, chunks: rows.length, sourceDir: path.resolve(dir) }, null, 2));
  return { files: files.length, chunks: rows.length };
}

async function search(query, topk = 5) {
  if (!collection) throw new Error('No index loaded. Call /ingest first.');
  const qv = await embed(query);
  const results = collection.querySync({ fieldName: 'embedding', vector: qv, topk, outputFields: ['source', 'chunkIndex', 'text'] });
  return results.map(r => ({ id: r.id, score: r.score, source: r.fields?.source, chunkIndex: r.fields?.chunkIndex, text: r.fields?.text }));
}

openExistingIfAny();

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'GET' && req.url === '/health') {
      return json(res, 200, { ok: true, host: HOST, port: PORT, model: MODEL, hasIndex: Boolean(collection), baseDir: BASE_DIR });
    }

    if (req.method === 'POST' && req.url === '/ingest') {
      const body = await readJsonBody(req);
      const dir = body.dir || './docs';
      const reset = body.reset !== false;
      const out = await ingestFromDir(dir, reset);
      return json(res, 200, { ok: true, ...out, model: MODEL, dbPath: DB_PATH });
    }

    if (req.method === 'POST' && req.url === '/search') {
      const body = await readJsonBody(req);
      if (!body.query) return json(res, 400, { ok: false, error: 'query is required' });
      const topk = Number(body.topk || 5);
      const results = await search(body.query, topk);
      return json(res, 200, { ok: true, model: MODEL, topk, results });
    }

    return json(res, 404, { ok: false, error: 'Not found' });
  } catch (err) {
    return json(res, 500, { ok: false, error: err.message || String(err) });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`zvec-rag-service listening on http://${HOST}:${PORT} (model=${MODEL})`);
});
