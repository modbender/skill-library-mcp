const fs = require('node:fs');
const path = require('node:path');

const DAYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];

function parseTimeToMinutes(value) {
  if (typeof value !== 'string') return null;
  const m = value.trim().match(/^(\d{1,2}):(\d{2})$/);
  if (!m) return null;
  const hh = Number(m[1]);
  const mm = Number(m[2]);
  if (!Number.isInteger(hh) || !Number.isInteger(mm)) return null;
  if (hh < 0 || hh > 23 || mm < 0 || mm > 59) return null;
  return hh * 60 + mm;
}

function normalizeDays(input) {
  if (!input) return null;
  const list = Array.isArray(input) ? input : String(input).split(',');
  const normalized = list
    .map(d => String(d || '').trim().slice(0, 3).toLowerCase())
    .filter(Boolean);
  if (normalized.length === 0) return null;
  for (const d of normalized) {
    if (!DAYS.includes(d)) return null;
  }
  return Array.from(new Set(normalized));
}

function resolveConfigPath(configPath) {
  if (configPath) return configPath;
  if (process.env.ROUTER_SCHEDULE_PATH) return process.env.ROUTER_SCHEDULE_PATH;
  return path.join(path.resolve(__dirname, '..'), 'router.schedule.json');
}

function validateSchedule(parsed) {
  if (!parsed || typeof parsed !== 'object') {
    throw new Error('router.schedule.json must be a JSON object');
  }
  if (parsed.timezone !== undefined && typeof parsed.timezone !== 'string') {
    throw new Error('router.schedule.json timezone must be a string');
  }
  if (!Array.isArray(parsed.rules)) {
    throw new Error('router.schedule.json missing rules[]');
  }

  const ids = new Set();
  for (const rule of parsed.rules) {
    if (!rule || typeof rule !== 'object') {
      throw new Error('rule must be an object');
    }
    if (!rule.id || typeof rule.id !== 'string') {
      throw new Error('rule.id must be a non-empty string');
    }
    if (ids.has(rule.id)) {
      throw new Error(`duplicate rule id: ${rule.id}`);
    }
    ids.add(rule.id);
    if (!rule.model || typeof rule.model !== 'string') {
      throw new Error(`rule ${rule.id} missing model`);
    }
    if (rule.enabled !== undefined && typeof rule.enabled !== 'boolean') {
      throw new Error(`rule ${rule.id} enabled must be boolean`);
    }
    const days = normalizeDays(rule.days);
    if (!days) {
      throw new Error(`rule ${rule.id} invalid days`);
    }
    const start = parseTimeToMinutes(rule.start);
    const end = parseTimeToMinutes(rule.end);
    if (start === null || end === null) {
      throw new Error(`rule ${rule.id} invalid start/end time`);
    }
    if (rule.priority !== undefined && !Number.isInteger(rule.priority)) {
      throw new Error(`rule ${rule.id} priority must be integer`);
    }
  }

  return parsed;
}

function loadSchedule(configPath) {
  const resolved = resolveConfigPath(configPath);
  if (!fs.existsSync(resolved)) {
    return { rules: [], timezone: 'local' };
  }
  const raw = fs.readFileSync(resolved, 'utf8');
  const parsed = JSON.parse(raw);
  return validateSchedule(parsed);
}

function getDayMinutesInTimezone(date, timezone) {
  const tz = timezone && timezone !== 'local' ? timezone : undefined;
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: tz,
    weekday: 'short',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(date);

  const weekday = (parts.find(p => p.type === 'weekday') || {}).value || '';
  const hour = Number((parts.find(p => p.type === 'hour') || {}).value || '0');
  const minute = Number((parts.find(p => p.type === 'minute') || {}).value || '0');

  const day = weekday ? weekday.slice(0, 3).toLowerCase() : DAYS[date.getDay()];
  const minutes = hour * 60 + minute;
  return { day, minutes };
}

function isRuleActive(rule, at, timezone = 'local') {
  const date = at instanceof Date ? at : new Date(at);
  if (Number.isNaN(date.getTime())) return false;
  const { day, minutes } = getDayMinutesInTimezone(date, timezone);
  const days = normalizeDays(rule.days) || [];
  if (!days.includes(day)) return false;
  if (rule.enabled === false) return false;
  const start = parseTimeToMinutes(rule.start);
  const end = parseTimeToMinutes(rule.end);
  if (start === null || end === null) return false;
  if (start === end) return false;
  if (start < end) {
    return minutes >= start && minutes < end;
  }
  // Overnight span (e.g. 22:00 -> 06:00)
  return minutes >= start || minutes < end;
}

function resolveActiveRule(schedule, at = new Date()) {
  const rules = Array.isArray(schedule.rules) ? schedule.rules : [];
  const timezone = (schedule && schedule.timezone) || 'local';
  const candidates = rules.filter(rule => isRuleActive(rule, at, timezone));
  if (candidates.length === 0) return null;
  candidates.sort((a, b) => (b.priority || 0) - (a.priority || 0));
  const top = candidates[0];
  const topPriority = top.priority || 0;
  const conflicts = candidates.filter(r => (r.priority || 0) === topPriority);
  if (conflicts.length > 1) {
    const ids = conflicts.map(r => r.id).join(', ');
    throw new Error(`schedule conflict: ${ids}`);
  }
  return top;
}

function detectConflicts(schedule) {
  const rules = Array.isArray(schedule.rules) ? schedule.rules : [];
  const conflicts = [];
  for (let i = 0; i < rules.length; i += 1) {
    for (let j = i + 1; j < rules.length; j += 1) {
      const a = rules[i];
      const b = rules[j];
      if ((a.priority || 0) !== (b.priority || 0)) continue;
      const daysA = normalizeDays(a.days) || [];
      const daysB = normalizeDays(b.days) || [];
      const overlapDay = daysA.some(d => daysB.includes(d));
      if (!overlapDay) continue;
      if (rangesOverlap(a, b)) {
        conflicts.push({ a: a.id, b: b.id });
      }
    }
  }
  return conflicts;
}

function rangesOverlap(a, b) {
  const aStart = parseTimeToMinutes(a.start);
  const aEnd = parseTimeToMinutes(a.end);
  const bStart = parseTimeToMinutes(b.start);
  const bEnd = parseTimeToMinutes(b.end);
  if (aStart === null || aEnd === null || bStart === null || bEnd === null) return false;
  const toIntervals = (start, end) => {
    if (start < end) return [[start, end]];
    return [[start, 1440], [0, end]];
  };
  const aIntervals = toIntervals(aStart, aEnd);
  const bIntervals = toIntervals(bStart, bEnd);
  for (const [as, ae] of aIntervals) {
    for (const [bs, be] of bIntervals) {
      if (Math.max(as, bs) < Math.min(ae, be)) return true;
    }
  }
  return false;
}

function addRule(schedule, rule) {
  const next = { timezone: schedule.timezone || 'local', rules: [...(schedule.rules || [])] };
  next.rules.push(rule);
  validateSchedule(next);
  return next;
}

function removeRule(schedule, id) {
  const next = { timezone: schedule.timezone || 'local', rules: [...(schedule.rules || [])] };
  next.rules = next.rules.filter(r => r.id !== id);
  return next;
}

function saveSchedule(schedule, configPath) {
  const resolved = resolveConfigPath(configPath);
  fs.writeFileSync(resolved, JSON.stringify(schedule, null, 2) + '\n', 'utf8');
  return resolved;
}

function buildCronPreview(schedule) {
  const rules = Array.isArray(schedule.rules) ? schedule.rules : [];
  const lines = [];
  for (const rule of rules) {
    const start = parseTimeToMinutes(rule.start);
    const end = parseTimeToMinutes(rule.end);
    if (start === null || end === null) continue;
    const startH = Math.floor(start / 60);
    const startM = start % 60;
    const endH = Math.floor(end / 60);
    const endM = end % 60;
    lines.push(`# ${rule.id} -> ${rule.model}`);
    lines.push(`${startM} ${startH} * * ${rule.days.map(d => DAYS.indexOf(d)).join(',')} node src/cli.js schedule apply --id ${rule.id}`);
    lines.push(`${endM} ${endH} * * ${rule.days.map(d => DAYS.indexOf(d)).join(',')} node src/cli.js schedule end --id ${rule.id}`);
  }
  return lines.join('\n');
}

module.exports = {
  loadSchedule,
  validateSchedule,
  resolveActiveRule,
  detectConflicts,
  addRule,
  removeRule,
  saveSchedule,
  buildCronPreview,
  parseTimeToMinutes,
  normalizeDays,
};
