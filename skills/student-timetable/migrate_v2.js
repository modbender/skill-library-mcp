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

function normalizeToken(s) {
  return String(s || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
}

function backupDirName() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  const stamp = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
  return `student-timetable-migrate-v2-${stamp}`;
}

function copyFileIfExists(src, dst) {
  if (!exists(src)) return false;
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.copyFileSync(src, dst);
  return true;
}

function ensureRegistryShape(reg) {
  const out = reg && typeof reg === 'object' ? reg : {};
  out.version = typeof out.version === 'number' ? out.version : 1;
  out.dataRoot = out.dataRoot ? String(out.dataRoot) : 'schedules/profiles';
  out.profiles = Array.isArray(out.profiles) ? out.profiles : [];
  out.global = out.global && typeof out.global === 'object' ? out.global : {};
  if (!Array.isArray(out.global.wake_keywords)) out.global.wake_keywords = [];
  // normalize + dedupe
  const dedup = [];
  for (const kw of out.global.wake_keywords) {
    const n = normalizeToken(kw);
    if (!n) continue;
    if (!dedup.includes(n)) dedup.push(n);
  }
  out.global.wake_keywords = dedup;
  return out;
}

function ensureProfileShape(p) {
  const out = p && typeof p === 'object' ? p : {};
  out.profile_id = out.profile_id ? String(out.profile_id) : '';
  out.type = out.type ? String(out.type) : 'child';
  out.display_name = out.display_name ? String(out.display_name) : out.profile_id;
  out.aliases = Array.isArray(out.aliases) ? out.aliases : [];
  out.base_info = out.base_info && typeof out.base_info === 'object' ? out.base_info : {};
  out.base_info.school = out.base_info.school ? String(out.base_info.school) : '';
  out.base_info.grade = out.base_info.grade ? String(out.base_info.grade) : '';
  out.base_info.class = out.base_info.class ? String(out.base_info.class) : '';
  return out;
}

function migrateV2(workspaceRoot, opts = {}) {
  const dryRun = !!opts.dryRun;
  const registryPath = path.join(workspaceRoot, 'schedules', 'profiles', 'registry.json');

  const report = {
    source: 'student-timetable-v2',
    dryRun,
    changed: false,
    backupsRoot: path.join(workspaceRoot, 'schedules', 'backups', backupDirName()),
    warnings: []
  };

  if (!exists(registryPath)) {
    report.warnings.push('registry.json not found; nothing to migrate.');
    return report;
  }

  let reg;
  try {
    reg = readJson(registryPath);
  } catch {
    report.warnings.push('registry.json unreadable; abort.');
    return report;
  }

  const before = JSON.stringify(reg);
  reg = ensureRegistryShape(reg);
  reg.profiles = (reg.profiles || []).map(ensureProfileShape);
  const after = JSON.stringify(reg);

  if (before !== after) {
    report.changed = true;
    if (!dryRun) {
      copyFileIfExists(registryPath, path.join(report.backupsRoot, 'profiles', 'registry.json'));
      writeJsonAtomic(registryPath, reg);
    }
  }

  return report;
}

module.exports = { migrateV2 };
