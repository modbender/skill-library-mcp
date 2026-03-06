const fs = require('fs');
const path = require('path');

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function normalizeToken(s) {
  return String(s || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
}

function loadWakeKeywords(workspaceRoot) {
  const registryPath = path.join(workspaceRoot, 'schedules', 'profiles', 'registry.json');
  if (!fs.existsSync(registryPath)) return [];

  let data;
  try {
    data = readJson(registryPath);
  } catch {
    return [];
  }

  const raw = data && data.global && Array.isArray(data.global.wake_keywords)
    ? data.global.wake_keywords
    : [];

  const out = [];
  for (const kw of raw) {
    const n = normalizeToken(kw);
    if (!n) continue;
    if (!out.includes(n)) out.push(n);
  }
  return out;
}

function matchesWakeKeyword(message, wakeKeywords) {
  const s = normalizeToken(message);
  if (!s) return false;
  const kws = Array.isArray(wakeKeywords) ? wakeKeywords : [];
  for (const kw of kws) {
    const k = normalizeToken(kw);
    if (!k) continue;
    if (s.includes(k)) return true;
  }
  return false;
}

module.exports = { loadWakeKeywords, matchesWakeKeyword };
