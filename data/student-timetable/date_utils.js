const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

function startOfDay(d) {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
}

function addDays(d, n) {
  const x = new Date(d);
  x.setDate(x.getDate() + n);
  return x;
}

function dayName(d) {
  return DAY_NAMES[d.getDay()];
}

function formatISODate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${dd}`;
}

function weekStartMonday(d) {
  const x = startOfDay(d);
  const dow = x.getDay(); // 0 Sunday
  const diff = dow === 0 ? -6 : 1 - dow;
  return addDays(x, diff);
}

module.exports = {
  startOfDay,
  addDays,
  dayName,
  formatISODate,
  weekStartMonday
};
