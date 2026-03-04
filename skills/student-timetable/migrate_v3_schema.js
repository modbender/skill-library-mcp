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

function backupDirName() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  const stamp = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
  return `student-timetable-migrate-v3-${stamp}`;
}

function copyFileIfExists(src, dst) {
  if (!exists(src)) return false;
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.copyFileSync(src, dst);
  return true;
}

function ensureArray(x) {
  return Array.isArray(x) ? x : [];
}

function normalizeId(s) {
  return String(s || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9\-]/g, '')
    .replace(/\-+/g, '-')
    .replace(/^\-+|\-+$/g, '') || 'id';
}

function emptyRules() {
  return { weekly_rules: [], dated_items: [], weekly_exceptions: [] };
}

function loadRegistry(workspaceRoot) {
  const p = path.join(workspaceRoot, 'schedules', 'profiles', 'registry.json');
  if (!exists(p)) return { profiles: [], _path: p };
  const reg = readJson(p);
  const profiles = ensureArray(reg && reg.profiles);
  return { profiles, _path: p };
}

function migrateProfileToScheduleV2(workspaceRoot, profileId, opts = {}) {
  const dryRun = !!opts.dryRun;
  const base = path.join(workspaceRoot, 'schedules', 'profiles', profileId);
  const weeklyPath = path.join(base, 'weekly.json');
  const specialPath = path.join(base, 'special_events.json');
  const scheduleV2Path = path.join(base, 'schedule.json');

  const report = { profile_id: profileId, dryRun, changed: false, backupsRoot: path.join(workspaceRoot, 'schedules', 'backups', backupDirName()), outputs: [scheduleV2Path], warnings: [] };

  if (exists(scheduleV2Path)) {
    report.warnings.push('schedule.json already exists; skip to keep idempotent.');
    return report;
  }

  const weekly = exists(weeklyPath) ? readJson(weeklyPath) : null;
  const specialStore = exists(specialPath) ? readJson(specialPath) : null;

  const rules = emptyRules();

  // Convert weekly.json v1 -> weekly_rules (only supports every_week default for now)
  if (weekly && weekly.weeks && weekly.weeks.default) {
    const def = weekly.weeks.default;
    for (const day of Object.keys(def)) {
      const items = ensureArray(def[day]);
      for (const it of items) {
        const title = it && it.title ? String(it.title) : '';
        const st = it && it.start_time ? String(it.start_time) : '';
        const en = it && it.end_time ? String(it.end_time) : '';
        const id = `wr-${normalizeId(`${title}-${day}-${st}`)}`;
        rules.weekly_rules.push({
          id,
          weekday: day,
          start_time: st,
          end_time: en,
          title,
          location: it && it.location ? String(it.location) : '',
          notes: it && it.notes ? String(it.notes) : '',
          tags: []
        });
      }
    }
  } else {
    report.warnings.push('No weekly.json default week found; weekly_rules empty.');
  }

  const specialEvents = ensureArray(specialStore && specialStore.events).map(ev => ({
    id: ev && ev.id ? String(ev.id) : '',
    date: ev && ev.date ? String(ev.date) : '',
    title: ev && ev.title ? String(ev.title) : 'Special event',
    start_time: ev && ev.start_time ? String(ev.start_time) : '',
    end_time: ev && ev.end_time ? String(ev.end_time) : '',
    location: ev && ev.location ? String(ev.location) : '',
    notes: ev && ev.notes ? String(ev.notes) : '',
    tags: ensureArray(ev && ev.tags).map(String),
    cancels_weekly: !!(ev && ev.cancels_weekly)
  }));

  const schedule = {
    version: 2,
    profile_id: profileId,
    timezone: (weekly && weekly.timezone) ? String(weekly.timezone) : 'Asia/Singapore',
    rules,
    special_events: specialEvents,
    updated_at: new Date().toISOString()
  };

  report.changed = true;

  if (dryRun) return report;

  copyFileIfExists(weeklyPath, path.join(report.backupsRoot, 'profiles', profileId, 'weekly.json'));
  copyFileIfExists(specialPath, path.join(report.backupsRoot, 'profiles', profileId, 'special_events.json'));

  writeJsonAtomic(scheduleV2Path, schedule);
  return report;
}

function migrateAllProfilesToScheduleV2(workspaceRoot, opts = {}) {
  const dryRun = !!opts.dryRun;
  const reg = loadRegistry(workspaceRoot);
  const report = { source: 'student-timetable-v3-schema', dryRun, per_profile: [], warnings: [] };

  for (const p of reg.profiles) {
    const id = p && p.profile_id ? String(p.profile_id) : '';
    if (!id) continue;
    report.per_profile.push(migrateProfileToScheduleV2(workspaceRoot, id, { dryRun }));
  }

  return report;
}

module.exports = { migrateAllProfilesToScheduleV2, migrateProfileToScheduleV2 };
