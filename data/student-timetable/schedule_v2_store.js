const fs = require('fs');
const path = require('path');

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function exists(p) {
  try {
    fs.accessSync(p);
    return true;
  } catch {
    return false;
  }
}

function loadScheduleV2(workspaceRoot, profileId) {
  const base = path.join(workspaceRoot, 'schedules', 'profiles', profileId);
  const schedulePath = path.join(base, 'schedule.json');
  if (!exists(schedulePath)) {
    return { schedule: null, paths: { schedulePath } };
  }
  return { schedule: readJson(schedulePath), paths: { schedulePath } };
}

module.exports = { loadScheduleV2 };
