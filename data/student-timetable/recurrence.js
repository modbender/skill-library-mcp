function isoDate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function parseISODate(s) {
  if (!s) return null;
  const m = String(s).trim().match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return null;
  const dt = new Date(`${m[1]}-${m[2]}-${m[3]}T00:00:00`);
  if (Number.isNaN(dt.getTime())) return null;
  return dt;
}

function daysBetween(a, b) {
  const ms = 24 * 60 * 60 * 1000;
  const da = new Date(a.getFullYear(), a.getMonth(), a.getDate());
  const db = new Date(b.getFullYear(), b.getMonth(), b.getDate());
  return Math.floor((db.getTime() - da.getTime()) / ms);
}

function occursOnDate(item, date) {
  const rec = item && item.recurrence ? item.recurrence : { type: 'every_week' };
  const type = rec.type || 'every_week';

  if (type === 'every_week') {
    return true;
  }

  if (type === 'biweekly') {
    const start = parseISODate(rec.start_date);
    if (!start) {
      return true;
    }
    const diffDays = daysBetween(start, date);
    if (diffDays < 0) {
      return false;
    }
    const weeks = Math.floor(diffDays / 7);
    return weeks % 2 === 0;
  }

  return true;
}

module.exports = { occursOnDate, isoDate, parseISODate };
