const fs = require('fs');
const path = require('path');

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function writeJsonAtomic(p, obj) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  const tmp = `${p}.tmp-${process.pid}-${Date.now()}`;
  fs.writeFileSync(tmp, JSON.stringify(obj, null, 2));
  fs.renameSync(tmp, p);
}

function normalizeToken(s) {
  return String(s || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
}

function registryPathFor(workspaceRoot) {
  return path.join(workspaceRoot, 'schedules', 'profiles', 'registry.json');
}

function ensureRegistry(workspaceRoot) {
  const p = registryPathFor(workspaceRoot);
  if (!fs.existsSync(p)) {
    return { version: 1, dataRoot: 'schedules/profiles', profiles: [], global: { wake_keywords: [] }, _path: p };
  }

  let data;
  try {
    data = readJson(p);
  } catch {
    return { version: 1, dataRoot: 'schedules/profiles', profiles: [], global: { wake_keywords: [] }, _path: p };
  }

  const out = data && typeof data === 'object' ? data : {};
  out.version = typeof out.version === 'number' ? out.version : 1;
  out.dataRoot = out.dataRoot ? String(out.dataRoot) : 'schedules/profiles';
  out.profiles = Array.isArray(out.profiles) ? out.profiles : [];
  out.global = out.global && typeof out.global === 'object' ? out.global : {};
  if (!Array.isArray(out.global.wake_keywords)) out.global.wake_keywords = [];
  out._path = p;
  return out;
}

function listWakeKeywords(workspaceRoot) {
  const reg = ensureRegistry(workspaceRoot);
  return (reg.global.wake_keywords || []).map(k => normalizeToken(k)).filter(Boolean);
}

function addWakeKeyword(workspaceRoot, keyword) {
  const kw = normalizeToken(keyword);
  if (!kw) return { ok: false, error: 'empty_keyword' };

  const reg = ensureRegistry(workspaceRoot);

  const existing = (reg.global.wake_keywords || []).map(k => normalizeToken(k)).filter(Boolean);
  if (existing.includes(kw)) return { ok: true, keyword: kw, already: true };

  reg.global.wake_keywords.push(kw);
  writeJsonAtomic(reg._path, reg);
  return { ok: true, keyword: kw, already: false };
}

module.exports = { listWakeKeywords, addWakeKeyword };
