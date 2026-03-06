const { loadProfileScheduleFiles } = require('./schedule_store.js');
const { formatISODate, addDays, weekStartMonday, startOfDay } = require('./date_utils.js');
const { resolveDayV2, resolveWeekV2 } = require('./resolver_v2.js');

const DOW_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];

function weekdayKey(date) {
  const js = date.getDay();
  // JS: 0 Sun .. 6 Sat
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

function weekIndexForDate(startDateISO, date) {
  const anchor = new Date(`${startDateISO}T00:00:00`);
  const aMon = weekStartMonday(anchor);
  const dMon = weekStartMonday(date);
  const diffMs = dMon.getTime() - aMon.getTime();
  const diffDays = Math.round(diffMs / (24 * 60 * 60 * 1000));
  return Math.floor(diffDays / 7);
}

function normalizeWeeklyEvents(weekly, date) {
  if (!weekly) return [];
  const rec = weekly.recurrence || { type: 'every_week' };
  const type = rec.type || 'every_week';
  const key = weekdayKey(date);

  let dayItems = [];

  if (type === 'every_week') {
    const w = weekly.weeks && weekly.weeks.default ? weekly.weeks.default : null;
    dayItems = (w && Array.isArray(w[key])) ? w[key] : [];
  } else if (type === 'biweekly') {
    const startDate = rec.start_date;
    if (!startDate) return [];
    const idx = weekIndexForDate(startDate, date);
    const which = (idx % 2 === 0) ? 'week_a' : 'week_b';
    const w = weekly.weeks && weekly.weeks[which] ? weekly.weeks[which] : null;
    dayItems = (w && Array.isArray(w[key])) ? w[key] : [];
  } else {
    return [];
  }

  const out = [];
  for (const it of dayItems) {
    out.push({
      date: formatISODate(date),
      weekday: key,
      title: it && it.title ? String(it.title) : '',
      start_time: it && it.start_time ? String(it.start_time) : '',
      end_time: it && it.end_time ? String(it.end_time) : '',
      location: it && it.location ? String(it.location) : '',
      notes: it && it.notes ? String(it.notes) : '',
      source: 'weekly',
      raw: it
    });
  }
  return out;
}

function specialEventsOnDate(special, date) {
  if (!special) return [];
  const target = formatISODate(date);
  const events = Array.isArray(special.events) ? special.events : [];
  const out = [];
  for (const ev of events) {
    if (!ev || String(ev.date || '') !== target) continue;
    out.push({
      date: target,
      weekday: weekdayKey(date),
      id: ev.id ? String(ev.id) : '',
      title: ev.title ? String(ev.title) : 'Special event',
      start_time: ev.start_time ? String(ev.start_time) : '',
      end_time: ev.end_time ? String(ev.end_time) : '',
      location: ev.location ? String(ev.location) : '',
      notes: ev.notes ? String(ev.notes) : '',
      tags: Array.isArray(ev.tags) ? ev.tags.slice() : [],
      cancels_weekly: !!ev.cancels_weekly,
      source: 'special',
      raw: ev
    });
  }
  return out;
}

function applyCancelsWeekly(weeklyItems, specialItems) {
  const cancelers = specialItems.filter(e => e && e.cancels_weekly);
  if (!cancelers.length) return weeklyItems;

  // v1: if cancel event has no times, cancel all weekly items for that day.
  const cancelsAllDay = cancelers.some(c => !c.start_time || !c.end_time);
  if (cancelsAllDay) return [];

  return weeklyItems.filter(w => {
    const wS = parseHHMM(w.start_time);
    const wE = parseHHMM(w.end_time);
    for (const c of cancelers) {
      const cS = parseHHMM(c.start_time);
      const cE = parseHHMM(c.end_time);
      if (overlapsRange(wS, wE, cS, cE)) return false;
    }
    return true;
  });
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

function dayScheduleForProfile(workspaceRoot, profileId, date) {
  const { weekly, special, scheduleV2 } = loadProfileScheduleFiles(workspaceRoot, profileId);
  if (scheduleV2 && scheduleV2.version === 2) {
    return resolveDayV2(scheduleV2, date);
  }

  const weeklyItems = normalizeWeeklyEvents(weekly, date);
  const specialItems = specialEventsOnDate(special, date);
  const keptWeekly = applyCancelsWeekly(weeklyItems, specialItems);
  return sortByTime(keptWeekly.concat(specialItems));
}

function weekScheduleForProfile(workspaceRoot, profileId, anchorDate, which) {
  const { scheduleV2 } = loadProfileScheduleFiles(workspaceRoot, profileId);
  if (scheduleV2 && scheduleV2.version === 2) {
    return resolveWeekV2(scheduleV2, anchorDate, which);
  }

  const monday = weekStartMonday(anchorDate);
  const start = which === 'next' ? addDays(monday, 7) : monday;
  const days = [];
  for (let i = 0; i < 7; i++) {
    const d = addDays(start, i);
    days.push({ date: formatISODate(d), weekday: weekdayKey(d), items: dayScheduleForProfile(workspaceRoot, profileId, d) });
  }
  return { week_start: formatISODate(start), days };
}

function todayDate() {
  return startOfDay(new Date());
}

module.exports = {
  dayScheduleForProfile,
  weekScheduleForProfile,
  todayDate,
  weekdayKey
};
