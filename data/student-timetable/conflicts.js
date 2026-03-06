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

function detectConflicts(existingItems, newEvent) {
  const out = [];
  const ns = parseHHMM(newEvent && newEvent.start_time);
  const ne = parseHHMM(newEvent && newEvent.end_time);

  // Only timed special events participate in overlap checks (v1).
  if (ns == null || ne == null) return out;

  for (const it of existingItems || []) {
    const isTimed = it && it.start_time && it.end_time;
    if (!isTimed) continue;
    const s = parseHHMM(it.start_time);
    const e = parseHHMM(it.end_time);
    if (overlapsRange(ns, ne, s, e)) {
      out.push({
        with: it.source || 'unknown',
        title: it.title || '',
        start_time: it.start_time || '',
        end_time: it.end_time || ''
      });
    }
  }
  return out;
}

module.exports = { detectConflicts };
