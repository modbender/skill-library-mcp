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

function exists(p) {
  try {
    fs.accessSync(p);
    return true;
  } catch {
    return false;
  }
}

function normalizeId(s) {
  return String(s || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9\-]/g, '')
    .replace(/\-+/g, '-')
    .replace(/^\-+|\-+$/g, '') || 'event';
}

function ensureStore(store) {
  const out = store && typeof store === 'object' ? store : {};
  if (typeof out.version !== 'number') out.version = 1;
  if (!Array.isArray(out.events)) out.events = [];
  return out;
}

function ensureTBD(s) {
  const v = String(s || '').trim();
  return v || '';
}

function upsertSpecialEvent(workspaceRoot, profileId, event) {
  const base = path.join(workspaceRoot, 'schedules', 'profiles', profileId);
  const specialPath = path.join(base, 'special_events.json');

  const store = exists(specialPath) ? ensureStore(readJson(specialPath)) : ensureStore({ version: 1, profile_id: profileId, events: [] });

  const date = String(event && event.date ? event.date : '').trim();
  if (!date) return { ok: false, error: 'missing_date' };

  const title = String(event && event.title ? event.title : 'Special event');

  const id = event && event.id
    ? String(event.id)
    : `ev-${normalizeId(`${title}-${date}`)}`;

  const next = {
    id,
    date,
    title,
    start_time: ensureTBD(event && event.start_time),
    end_time: ensureTBD(event && event.end_time),
    location: ensureTBD(event && event.location),
    notes: ensureTBD(event && event.notes),
    tags: Array.isArray(event && event.tags) ? event.tags.slice() : [],
    cancels_weekly: !!(event && event.cancels_weekly)
  };

  const idx = store.events.findIndex(e => e && String(e.id) === id);
  if (idx >= 0) store.events[idx] = next;
  else store.events.push(next);

  writeJsonAtomic(specialPath, store);
  return { ok: true, id, path: specialPath };
}

module.exports = { upsertSpecialEvent };
