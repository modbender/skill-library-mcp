const { resolveWorkspaceRoot } = require('./workspace_root.js');
const { loadProfilesRegistry, resolveProfile, clarifyProfileMessage } = require('./profiles_registry.js');
const { dayScheduleForProfile, weekScheduleForProfile, todayDate } = require('./student_timetable_service.js');
const { addDays } = require('./date_utils.js');
const { loadWakeKeywords, matchesWakeKeyword } = require('./wake_keywords.js');

function parseIntent(input) {
  const s = String(input || '').toLowerCase();
  if (s.includes('tomorrow') || s.includes('明天')) return 'tomorrow';
  if (s.includes('today') || s.includes('今天')) return 'today';
  if (s.includes('next week') || s.includes('下周')) return 'next_week';
  if (s.includes('this week') || s.includes('本周') || s.includes('这周')) return 'this_week';
  return 'today';
}

function extractProfileIdent(input) {
  const m = String(input || '').match(/--profile\s+([^\s]+)/i);
  if (m) return m[1];
  return null;
}

function renderDay(items) {
  if (!items.length) {
    return '(no items)';
  }
  return items.map(it => {
    const time = it.start_time ? `${it.start_time}-${it.end_time || ''}`.replace(/-$/, '') : 'TBD';
    const notes = it.notes ? ` | ${it.notes}` : '';
    return `${time} | ${it.title}${notes}`;
  }).join('\n');
}

async function run(input) {
  const workspaceRoot = resolveWorkspaceRoot();
  const wakeKeywords = loadWakeKeywords(workspaceRoot);
  const wakeMatched = matchesWakeKeyword(input, wakeKeywords);

  const registry = loadProfilesRegistry(workspaceRoot);

  const ident = extractProfileIdent(input);
  const resolved = resolveProfile(registry, ident, { allowDefaultToSelf: true });
  if (!resolved.ok) {
    resolved.input = ident;
    return { ok: false, message: clarifyProfileMessage(resolved) };
  }

  const profile = resolved.profile;
  const intent = parseIntent(input);

  if (wakeMatched && intent === 'today') {
    // Wake keyword matched but no specific intent; default to today's schedule.
  }
  const today = todayDate();

  if (intent === 'today') {
    const items = dayScheduleForProfile(workspaceRoot, profile.profile_id, today);
    const wakeNote = wakeMatched ? ` (wake matched)` : '';
    return { ok: true, message: `${profile.display_name || profile.profile_id}${wakeNote} today\n${renderDay(items)}` };
  }

  if (intent === 'tomorrow') {
    const d = addDays(today, 1);
    const items = dayScheduleForProfile(workspaceRoot, profile.profile_id, d);
    return { ok: true, message: `${profile.display_name || profile.profile_id} tomorrow\n${renderDay(items)}` };
  }

  if (intent === 'this_week' || intent === 'next_week') {
    const which = intent === 'next_week' ? 'next' : 'this';
    const wk = weekScheduleForProfile(workspaceRoot, profile.profile_id, today, which);
    const lines = [];
    lines.push(`${profile.display_name || profile.profile_id} ${intent} (week of ${wk.week_start})`);
    for (const day of wk.days) {
      lines.push('');
      lines.push(`${day.weekday} ${day.date}`);
      lines.push(renderDay(day.items));
    }
    return { ok: true, message: lines.join('\n') };
  }

  return { ok: false, message: 'Unsupported request.' };
}

module.exports = { run };
