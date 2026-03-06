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
    .replace(/^\-+|\-+$/g, '') || 'profile';
}

function nowIso() {
  return new Date().toISOString();
}

function ensureUniqueId(existingIds, desired) {
  let base = desired;
  let out = base;
  let i = 2;
  while (existingIds.has(out)) {
    out = `${base}-${i}`;
    i++;
  }
  existingIds.add(out);
  return out;
}

function backupDirName() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  const stamp = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
  return `student-timetable-migrate-${stamp}`;
}

function copyFileIfExists(src, dst) {
  if (!exists(src)) return false;
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.copyFileSync(src, dst);
  return true;
}

function loadKidRegistry(workspaceRoot) {
  const p = path.join(workspaceRoot, 'schedules', 'kids', 'registry.json');
  if (!exists(p)) return { kids: [], _path: p };
  const data = readJson(p);
  if (Array.isArray(data)) return { kids: data, _path: p };
  return { kids: Array.isArray(data.kids) ? data.kids : [], _path: p };
}

function detectLegacyZianJson(workspaceRoot) {
  const schedulesDir = path.join(workspaceRoot, 'schedules');
  if (!exists(schedulesDir)) return [];
  const entries = fs.readdirSync(schedulesDir);
  const candidates = [];
  for (const name of entries) {
    if (!/^zian_.*\.json$/i.test(name)) continue;
    const p = path.join(schedulesDir, name);
    if (!exists(p)) continue;
    try {
      const data = readJson(p);
      if (data && (data.weekly_timetable || data.special_events || data.term_calendar || data.events || data.terms)) {
        candidates.push({ path: p, data });
      }
    } catch {
      // ignore
    }
  }
  return candidates;
}

function convertOldWeeklyToNew(oldWeekly, profileId) {
  const weeklyTimetable = (oldWeekly && (oldWeekly.weekly_timetable || oldWeekly.weekly)) || {};
  // old keys like Monday
  const mapDay = {
    Monday: 'mon', Tuesday: 'tue', Wednesday: 'wed', Thursday: 'thu', Friday: 'fri', Saturday: 'sat', Sunday: 'sun'
  };
  const week = { mon: [], tue: [], wed: [], thu: [], fri: [], sat: [], sun: [] };

  for (const [k, items] of Object.entries(weeklyTimetable)) {
    const dk = mapDay[k] || String(k || '').toLowerCase().slice(0, 3);
    if (!week[dk] || !Array.isArray(items)) continue;
    for (const it of items) {
      const title = it && (it.title || it.subject || it.activity || it.name) ? String(it.title || it.subject || it.activity || it.name) : '';
      let start = '';
      let end = '';
      if (it && it.time) {
        const m = String(it.time).match(/(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})/);
        if (m) {
          start = m[1];
          end = m[2];
        }
      }
      week[dk].push({
        title,
        start_time: start,
        end_time: end,
        location: it && it.location ? String(it.location) : '',
        notes: it && it.notes ? String(it.notes) : ''
      });
    }
  }

  return {
    version: 1,
    profile_id: profileId,
    recurrence: { type: 'every_week' },
    timezone: 'Asia/Singapore',
    weeks: { default: week }
  };
}

function convertOldSpecialToNew(oldSpecial, profileId) {
  const events = Array.isArray(oldSpecial && oldSpecial.events) ? oldSpecial.events : [];
  const out = [];
  for (const ev of events) {
    const date = ev && ev.date ? String(ev.date) : (ev && ev.event_details && ev.event_details.date ? String(ev.event_details.date) : '');
    if (!date) continue;
    let start = '';
    let end = '';
    const time = ev.time || (ev.event_details && ev.event_details.time) || '';
    if (time) {
      const m = String(time).match(/(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})/);
      if (m) {
        start = m[1];
        end = m[2];
      }
    }
    out.push({
      id: ev.id ? String(ev.id) : `legacy-${normalizeId((ev.name || ev.title || 'event') + '-' + date)}`,
      date,
      title: ev.title ? String(ev.title) : (ev.name ? String(ev.name) : 'Special event'),
      start_time: ev.start_time ? String(ev.start_time) : start,
      end_time: ev.end_time ? String(ev.end_time) : end,
      location: ev.location ? String(ev.location) : '',
      notes: ev.notes ? String(ev.notes) : (ev.description ? String(ev.description) : ''),
      tags: Array.isArray(ev.tags) ? ev.tags.slice() : [],
      cancels_weekly: !!ev.cancels_weekly
    });
  }

  return { version: 1, profile_id: profileId, events: out };
}

function convertOldTermToNew(oldTerm, profileId) {
  return {
    version: 1,
    profile_id: profileId,
    timezone: 'Asia/Singapore',
    terms: Array.isArray(oldTerm && oldTerm.terms) ? oldTerm.terms : [],
    no_school_days: Array.isArray(oldTerm && oldTerm.holidays) ? oldTerm.holidays.map(h => ({ date: h.date || h, name: h.name || '' })) : []
  };
}

function loadNewRegistry(workspaceRoot) {
  const p = path.join(workspaceRoot, 'schedules', 'profiles', 'registry.json');
  if (!exists(p)) return { version: 1, dataRoot: 'schedules/profiles', profiles: [], _path: p };
  const data = readJson(p);
  return {
    version: typeof data.version === 'number' ? data.version : 1,
    dataRoot: data.dataRoot ? String(data.dataRoot) : 'schedules/profiles',
    profiles: Array.isArray(data.profiles) ? data.profiles : [],
    _path: p
  };
}

function migrateKidSchedule(workspaceRoot, opts = {}) {
  const dryRun = !!opts.dryRun;
  const backupsRoot = path.join(workspaceRoot, 'schedules', 'backups', backupDirName());

  const oldReg = loadKidRegistry(workspaceRoot);
  const newReg = loadNewRegistry(workspaceRoot);

  const existingIds = new Set((newReg.profiles || []).map(p => String(p.profile_id || '')).filter(Boolean));
  const report = { source: 'kid-schedule', dryRun, migrated: [], skipped: [], warnings: [], backupsRoot };

  for (const kid of oldReg.kids || []) {
    const oldId = kid && kid.id ? String(kid.id) : '';
    if (!oldId) continue;

    let profileId = normalizeId(oldId);

    // Special-case: historical kid-schedule data sometimes used zian-2/zian-3 etc.
    // Consolidate all of those into the canonical Zian child profile_id.
    if (profileId === 'zian-2' || profileId === 'zian-3' || profileId === 'zian-specialevents') {
      profileId = 'zian';
    }

    const already = (newReg.profiles || []).some(p => String(p.profile_id || '') === profileId);
    if (already) {
      report.skipped.push({ oldId, reason: 'already_migrated', profileId });
      continue;
    }

    profileId = ensureUniqueId(existingIds, profileId);

    const createdAt = nowIso();
    const prof = {
      profile_id: profileId,
      type: 'child',
      display_name: kid.display_name ? String(kid.display_name) : oldId,
      aliases: Array.isArray(kid.aliases) ? kid.aliases.slice() : [],
      created_at: createdAt,
      updated_at: createdAt
    };

    const oldBase = path.join(workspaceRoot, 'schedules', 'kids', oldId);
    const oldWeeklyPath = path.join(oldBase, 'weekly.json');
    const oldSpecialPath = path.join(oldBase, 'special_events.json');
    const oldTermPath = path.join(oldBase, 'term_calendar.json');

    const newBase = path.join(workspaceRoot, 'schedules', 'profiles', profileId);
    const newWeeklyPath = path.join(newBase, 'weekly.json');
    const newSpecialPath = path.join(newBase, 'special_events.json');
    const newTermPath = path.join(newBase, 'term_calendar.json');

    if (dryRun) {
      report.migrated.push({ oldId, profileId, outputs: [newWeeklyPath, newSpecialPath, newTermPath] });
      continue;
    }

    // backup any destination files that exist
    const bWeekly = path.join(backupsRoot, 'profiles', profileId, 'weekly.json');
    const bSpecial = path.join(backupsRoot, 'profiles', profileId, 'special_events.json');
    const bTerm = path.join(backupsRoot, 'profiles', profileId, 'term_calendar.json');
    copyFileIfExists(newWeeklyPath, bWeekly);
    copyFileIfExists(newSpecialPath, bSpecial);
    copyFileIfExists(newTermPath, bTerm);

    const oldWeekly = exists(oldWeeklyPath) ? readJson(oldWeeklyPath) : null;
    const oldSpecial = exists(oldSpecialPath) ? readJson(oldSpecialPath) : null;
    const oldTerm = exists(oldTermPath) ? readJson(oldTermPath) : null;

    const newWeekly = convertOldWeeklyToNew(oldWeekly, profileId);
    const newSpecial = convertOldSpecialToNew(oldSpecial, profileId);
    const newTerm = convertOldTermToNew(oldTerm, profileId);

    // only write if missing (idempotent + non-destructive)
    if (!exists(newWeeklyPath)) writeJsonAtomic(newWeeklyPath, newWeekly);
    if (!exists(newSpecialPath)) writeJsonAtomic(newSpecialPath, newSpecial);
    if (!exists(newTermPath)) writeJsonAtomic(newTermPath, newTerm);

    newReg.profiles.push(prof);

    report.migrated.push({ oldId, profileId, outputs: [newWeeklyPath, newSpecialPath, newTermPath] });
  }

  if (!dryRun) {
    // backup registry if it exists
    const bReg = path.join(backupsRoot, 'profiles', 'registry.json');
    copyFileIfExists(newReg._path, bReg);

    // write registry
    const regOut = {
      version: 1,
      dataRoot: 'schedules/profiles',
      profiles: newReg.profiles
    };
    writeJsonAtomic(newReg._path, regOut);
  }

  return report;
}

function migrateLegacyZian(workspaceRoot, opts = {}) {
  const dryRun = !!opts.dryRun;
  const backupsRoot = path.join(workspaceRoot, 'schedules', 'backups', backupDirName());

  const newReg = loadNewRegistry(workspaceRoot);
  const existingIds = new Set((newReg.profiles || []).map(p => String(p.profile_id || '')).filter(Boolean));

  const candidates = detectLegacyZianJson(workspaceRoot);
  const report = { source: 'legacy-zian-json', dryRun, migrated: [], skipped: [], warnings: [], backupsRoot };

  if (!candidates.length) return report;

  // For v1: migrate all legacy zian JSON into a single canonical child profile.
  // profile_id represents the person (Zian), not the data source.
  const profileId = 'zian';

  if ((newReg.profiles || []).some(p => String(p.profile_id || '') === profileId)) {
    report.skipped.push({ profileId, reason: 'profile_exists' });
    return report;
  }

  const createdAt = nowIso();
  const prof = {
    profile_id: profileId,
    type: 'child',
    display_name: 'Zian',
    aliases: ['zian'],
    created_at: createdAt,
    updated_at: createdAt
  };

  const newBase = path.join(workspaceRoot, 'schedules', 'profiles', profileId);
  const newWeeklyPath = path.join(newBase, 'weekly.json');
  const newSpecialPath = path.join(newBase, 'special_events.json');
  const newTermPath = path.join(newBase, 'term_calendar.json');

  if (dryRun) {
    report.migrated.push({ profileId, inputs: candidates.map(c => c.path), outputs: [newWeeklyPath, newSpecialPath, newTermPath] });
    return report;
  }

  // backup any destination files that exist
  copyFileIfExists(newWeeklyPath, path.join(backupsRoot, 'profiles', profileId, 'weekly.json'));
  copyFileIfExists(newSpecialPath, path.join(backupsRoot, 'profiles', profileId, 'special_events.json'));
  copyFileIfExists(newTermPath, path.join(backupsRoot, 'profiles', profileId, 'term_calendar.json'));

  // best-effort merge: pick first candidate with those keys
  let oldWeekly = null;
  let oldSpecial = null;
  let oldTerm = null;
  for (const c of candidates) {
    const d = c.data;
    if (!oldWeekly && d && d.weekly_timetable) oldWeekly = d;
    if (!oldSpecial && d && (d.special_events || d.events)) oldSpecial = d.special_events ? d.special_events : d;
    if (!oldTerm && d && (d.term_calendar || d.terms)) oldTerm = d.term_calendar ? d.term_calendar : d;
  }

  // If destination exists, we still proceed safely:
  // - create backups
  // - overwrite destination so legacy zian content can be migrated even under "missing-only" behavior
  writeJsonAtomic(newWeeklyPath, convertOldWeeklyToNew(oldWeekly, profileId));
  writeJsonAtomic(newSpecialPath, convertOldSpecialToNew(oldSpecial, profileId));
  writeJsonAtomic(newTermPath, convertOldTermToNew(oldTerm, profileId));

  newReg.profiles.push(prof);

  // backup registry if it exists
  copyFileIfExists(newReg._path, path.join(backupsRoot, 'profiles', 'registry.json'));
  writeJsonAtomic(newReg._path, { version: 1, dataRoot: 'schedules/profiles', profiles: newReg.profiles });

  report.migrated.push({ profileId, inputs: candidates.map(c => c.path), outputs: [newWeeklyPath, newSpecialPath, newTermPath] });
  report.warnings.push('Legacy zian migration writes to canonical profile_id "zian" (child).');
  return report;
}

module.exports = { migrateKidSchedule, migrateLegacyZian };
