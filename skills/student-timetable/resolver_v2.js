const { formatISODate, addDays, weekStartMonday, startOfDay } = require('./date_utils.js');

const DOW_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];

function weekdayKey(date) {
  const js = date.getDay();
  if (js === 0) return 'sun';
  if (js === 1) return 'mon';
  if (js === 2) return 'tue';
  if (js === 3) return 'wed';
  if (js === 4) return 'thu';
  if (js === 5) return 'fri';
  return 'sat';
}

function parseHHMM(s) {
  const m = String(s || '').match(/^(\d{1,2}):(\d{2})$/);
  if (!m) return null;
  const hh = parseInt(m[1], 10);
  const mm = parseInt(m[2], 10);
  if (hh < 0 || hh > 23 || mm < 0 || mm > 59) return null;
  return hh * 60 + mm;
}

function overlapsRange(aStart, aEnd, bStart, bEnd) {
  if (aStart == null || aEnd == null || bStart == null || bEnd == null) return false;
  return Math.max(aStart, bStart) < Math.min(aEnd, bEnd);
}

function inDateRange(dateISO, fromISO, toISO) {
  if (!fromISO && !toISO) return true;
  if (fromISO && dateISO < fromISO) return false;
  if (toISO && dateISO > toISO) return false;
  return true;
}

function normalizeTags(tags) {
  if (!Array.isArray(tags)) return [];
  const out = [];
  for (const t of tags) {
    const s = String(t || '').trim().toLowerCase();
    if (!s) continue;
    if (!out.includes(s)) out.push(s);
  }
  return out;
}

function ruleMatchesTimeWindow(rule, win) {
  if (!win) return false;
  const s = String(win.start_time || '').trim();
  const e = String(win.end_time || '').trim();
  if (s && String(rule.start_time || '').trim() !== s) return false;
  if (e && String(rule.end_time || '').trim() !== e) return false;

  const requiredTags = normalizeTags(win.tags);
  if (!requiredTags.length) return true;

  const rt = normalizeTags(rule.tags);
  return requiredTags.every(t => rt.includes(t));
}

function applyWeeklyExceptions(dateISO, items, weeklyExceptions) {
  const ex = Array.isArray(weeklyExceptions) ? weeklyExceptions : [];
  const todays = ex.filter(e => e && String(e.date || '') === dateISO);
  if (!todays.length) return items;

  let out = items.slice();

  for (const e of todays) {
    const kind = String(e.kind || '').toLowerCase();
    if (kind !== 'cancel') continue;

    const targets = e.targets || {};
    const ruleIds = Array.isArray(targets.rule_ids) ? targets.rule_ids.map(String) : [];
    const wins = Array.isArray(targets.time_windows) ? targets.time_windows : [];

    out = out.filter(it => {
      if (it.source !== 'weekly_rule') return true;
      if (ruleIds.length && it.rule_id && ruleIds.includes(String(it.rule_id))) return false;
      for (const w of wins) {
        if (ruleMatchesTimeWindow(it.raw_rule || {}, w)) return false;
      }
      return true;
    });
  }

  return out;
}

function sortByTime(items) {
  return items.slice().sort((a, b) => {
    const am = parseHHMM(a.start_time);
    const bm = parseHHMM(b.start_time);
    if (am == null && bm == null) return String(a.title).localeCompare(String(b.title));
    if (am == null) return 1;
    if (bm == null) return -1;
    if (am !== bm) return am - bm;
    return String(a.title).localeCompare(String(b.title));
  });
}

function resolveDayV2(schedule, date) {
  const dateISO = formatISODate(date);
  const wk = weekdayKey(date);

  const rules = schedule && schedule.rules ? schedule.rules : {};
  const weeklyRules = Array.isArray(rules.weekly_rules) ? rules.weekly_rules : [];
  const datedItems = Array.isArray(rules.dated_items) ? rules.dated_items : [];
  const weeklyExceptions = Array.isArray(rules.weekly_exceptions) ? rules.weekly_exceptions : [];
  const specialEvents = Array.isArray(schedule && schedule.special_events) ? schedule.special_events : [];

  const fromWeekly = weeklyRules
    .filter(r => r && String(r.weekday || '') === wk)
    .filter(r => inDateRange(dateISO, r.effective_from, r.effective_to))
    .map(r => ({
      date: dateISO,
      weekday: wk,
      rule_id: r.id ? String(r.id) : '',
      title: r.title ? String(r.title) : '',
      start_time: r.start_time ? String(r.start_time) : '',
      end_time: r.end_time ? String(r.end_time) : '',
      location: r.location ? String(r.location) : '',
      notes: r.notes ? String(r.notes) : '',
      tags: normalizeTags(r.tags),
      source: 'weekly_rule',
      raw_rule: r
    }));

  const fromDated = datedItems
    .filter(d => d && String(d.date || '') === dateISO)
    .map(d => ({
      date: dateISO,
      weekday: wk,
      id: d.id ? String(d.id) : '',
      title: d.title ? String(d.title) : '',
      start_time: d.start_time ? String(d.start_time) : '',
      end_time: d.end_time ? String(d.end_time) : '',
      location: d.location ? String(d.location) : '',
      notes: d.notes ? String(d.notes) : '',
      tags: normalizeTags(d.tags),
      source: 'dated_item',
      raw: d
    }));

  const fromSpecial = specialEvents
    .filter(e => e && String(e.date || '') === dateISO)
    .map(e => ({
      date: dateISO,
      weekday: wk,
      id: e.id ? String(e.id) : '',
      title: e.title ? String(e.title) : 'Special event',
      start_time: e.start_time ? String(e.start_time) : '',
      end_time: e.end_time ? String(e.end_time) : '',
      location: e.location ? String(e.location) : '',
      notes: e.notes ? String(e.notes) : '',
      tags: normalizeTags(e.tags),
      cancels_weekly: !!e.cancels_weekly,
      source: 'special',
      raw: e
    }));

  let combined = fromWeekly.concat(fromDated);
  combined = applyWeeklyExceptions(dateISO, combined, weeklyExceptions);

  // Legacy cancels_weekly behavior for special events.
  const cancelers = fromSpecial.filter(e => e && e.cancels_weekly);
  if (cancelers.length) {
    const cancelsAllDay = cancelers.some(c => !c.start_time || !c.end_time);
    if (cancelsAllDay) {
      combined = combined.filter(it => it.source !== 'weekly_rule');
    } else {
      combined = combined.filter(it => {
        if (it.source !== 'weekly_rule') return true;
        const itS = parseHHMM(it.start_time);
        const itE = parseHHMM(it.end_time);
        for (const c of cancelers) {
          const cS = parseHHMM(c.start_time);
          const cE = parseHHMM(c.end_time);
          if (overlapsRange(itS, itE, cS, cE)) return false;
        }
        return true;
      });
    }
  }

  return sortByTime(combined.concat(fromSpecial));
}

function resolveWeekV2(schedule, anchorDate, which) {
  const monday = weekStartMonday(anchorDate);
  const start = which === 'next' ? addDays(monday, 7) : monday;
  const days = [];
  for (let i = 0; i < 7; i++) {
    const d = addDays(start, i);
    days.push({
      date: formatISODate(d),
      weekday: weekdayKey(d),
      items: resolveDayV2(schedule, d)
    });
  }
  return { week_start: formatISODate(start), days };
}

function todayDate() {
  return startOfDay(new Date());
}

module.exports = { resolveDayV2, resolveWeekV2, todayDate, weekdayKey };
